#!/usr/bin/env python3
"""
Bot principal do Ghost Bot com Webhook - Substitui polling por webhook
Versão otimizada para containers com webhook ao invés de polling.
"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# Configura o path para incluir o diretório raiz
sys.path.insert(0, str(Path(__file__).parent.resolve()))

# Importações principais
from aiohttp import web
import json
from typing import Dict, Any

# Importar configurações
from tokens import Config

# Importar o bot principal para usar suas funções
try:
    from bot import (
        application, 
        processar_mensagem,
        logger
    )
    BOT_PRINCIPAL_DISPONIVEL = True
    logger.info("Bot principal importado com sucesso para webhook!")
except ImportError as e:
    logger.error(f"Erro ao importar bot principal: {e}")
    BOT_PRINCIPAL_DISPONIVEL = False

# Configurações do webhook
BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ghost_webhook_secret_2025")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_PUBLIC_URL = os.getenv("WEBHOOK_PUBLIC_URL", "")

# Rotas do webhook
routes = web.RouteTableDef()

@routes.post("/webhook/{secret}")
async def telegram_webhook(request):
    """Endpoint principal que recebe updates do Telegram"""
    secret = request.match_info.get("secret")
    if secret != WEBHOOK_SECRET:
        logger.warning(f"Tentativa de acesso com secret inválido: {secret}")
        return web.Response(status=403, text="Forbidden")
    
    try:
        data = await request.json()
        logger.info(f"Recebido update via webhook: {data.get('update_id', 'unknown')}")
        
        if BOT_PRINCIPAL_DISPONIVEL and application:
            # Processar usando o bot principal
            await processar_update_telegram(data)
        else:
            logger.error("Bot principal não disponível!")
            
        return web.json_response({"ok": True})
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return web.Response(status=400, text="Bad Request")

async def processar_update_telegram(update_data: Dict[str, Any]):
    """Processa update do Telegram usando as funções do bot principal"""
    try:
        # Converte o dict em objeto Update do python-telegram-bot
        from telegram import Update
        
        update = Update.de_json(update_data, application.bot)
        
        if update:
            # Processa o update usando o sistema do bot principal
            await application.process_update(update)
            logger.info(f"Update {update.update_id} processado com sucesso")
        else:
            logger.error("Falha ao converter update_data em objeto Update")
            
    except Exception as e:
        logger.error(f"Erro ao processar update: {e}")

@routes.get("/health")
async def health_check(request):
    """Verifica se o webhook está funcionando"""
    return web.json_response({
        "status": "ok",
        "bot_disponivel": BOT_PRINCIPAL_DISPONIVEL,
        "webhook_url": f"{WEBHOOK_PUBLIC_URL}/webhook/{WEBHOOK_SECRET}" if WEBHOOK_PUBLIC_URL else "Não configurada",
        "modo": "webhook"
    })

@routes.post("/set_webhook")
async def configurar_webhook(request):
    """Configura o webhook no Telegram"""
    if not WEBHOOK_PUBLIC_URL:
        return web.json_response({
            "error": "WEBHOOK_PUBLIC_URL deve ser configurada"
        }, status=400)
    
    webhook_url = f"{WEBHOOK_PUBLIC_URL}/webhook/{WEBHOOK_SECRET}"
    
    try:
        # Usa a instância do bot principal para configurar webhook
        result = await application.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            max_connections=40,
            allowed_updates=["message", "callback_query"]
        )
        
        if result:
            logger.info(f"Webhook configurado: {webhook_url}")
            return web.json_response({"ok": True, "webhook_url": webhook_url})
        else:
            return web.json_response({"error": "Falha ao configurar webhook"}, status=400)
            
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {e}")
        return web.json_response({"error": str(e)}, status=500)

@routes.post("/remove_webhook")
async def remover_webhook(request):
    """Remove webhook (volta para polling)"""
    try:
        result = await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook removido. Bot pode voltar para polling.")
        return web.json_response({"ok": True, "message": "Webhook removido"})
    except Exception as e:
        logger.error(f"Erro ao remover webhook: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def iniciar_webhook():
    """Inicia o servidor webhook"""
    app = web.Application()
    app.add_routes(routes)
    
    logger.info(f"Iniciando servidor webhook na porta {PORT}")
    logger.info(f"Webhook disponível em: http://{WEBHOOK_HOST}:{PORT}/webhook/{WEBHOOK_SECRET}")
    
    if WEBHOOK_PUBLIC_URL:
        logger.info(f"URL pública: {WEBHOOK_PUBLIC_URL}/webhook/{WEBHOOK_SECRET}")
    else:
        logger.warning("WEBHOOK_PUBLIC_URL não configurada!")
    
    # Inicia o servidor
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBHOOK_HOST, PORT)
    await site.start()
    
    logger.info("Servidor webhook iniciado! Aguardando mensagens...")
    
    # Mantém o servidor rodando
    try:
        while True:
            await asyncio.sleep(3600)  # Dorme por 1 hora
    except KeyboardInterrupt:
        logger.info("Webhook interrompido pelo usuário")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    if not BOT_PRINCIPAL_DISPONIVEL:
        logger.error("Bot principal não disponível! Não é possível iniciar webhook.")
        sys.exit(1)
        
    try:
        asyncio.run(iniciar_webhook())
    except KeyboardInterrupt:
        logger.info("Bot webhook encerrado.")
    except Exception as e:
        logger.error(f"Erro fatal no webhook: {e}")
        sys.exit(1)
