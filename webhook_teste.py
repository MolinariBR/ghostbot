#!/usr/bin/env python3
"""
Webhook Telegram integrado com o bot principal
Substitui o método de polling por webhook para melhor performance e menor uso de recursos.
"""

from aiohttp import web
import os
import logging
import asyncio
import json
from typing import Dict, Any
import aiohttp

# Importar configurações do projeto
from tokens import Config

# Configurações
BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ghost_webhook_secret_2025")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://useghost.squareweb.app")  # URL do servidor em produção
PORT = int(os.getenv("PORT", 8080))

# Para desenvolvimento local, usar ngrok ou similar
if Config.IS_PRODUCTION:
    WEBHOOK_BASE_URL = WEBHOOK_URL
else:
    # Em desenvolvimento, você pode usar ngrok: https://your-ngrok-url.ngrok.io
    WEBHOOK_BASE_URL = os.getenv("NGROK_URL", "http://localhost:8080")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

routes = web.RouteTableDef()

# Importar as funções do bot principal
try:
    from bot import processar_mensagem, bot_instance
    BOT_INTEGRADO = True
    logging.info("Bot principal integrado com sucesso!")
except ImportError:
    BOT_INTEGRADO = False
    logging.warning("Bot principal não encontrado, executando em modo teste")

@routes.post("/webhook/{secret}")
async def telegram_webhook(request):
    secret = request.match_info.get("secret")
    if secret != WEBHOOK_SECRET:
        logging.warning(f"Tentativa de acesso com secret inválido: {secret}")
        return web.Response(status=403, text="Forbidden")
    
    try:
        data = await request.json()
        logging.info(f"Recebido update: {json.dumps(data, indent=2)}")
        
        if BOT_INTEGRADO:
            # Processar com o bot principal
            await processar_update_webhook(data)
        else:
            # Modo teste - apenas log
            logging.info("Modo teste: update recebido mas não processado")
        
        return web.json_response({"ok": True})
    except Exception as e:
        logging.error(f"Erro no webhook: {e}")
        return web.Response(status=400, text="Bad Request")

async def processar_update_webhook(update_data: Dict[str, Any]):
    """Processa um update recebido via webhook"""
    try:
        if BOT_INTEGRADO and bot_instance:
            # Usar o processamento do bot principal
            await bot_instance.process_new_updates([update_data])
            logging.info("Update processado pelo bot principal")
        else:
            # Fallback manual se bot não estiver integrado
            if 'message' in update_data:
                message = update_data['message']
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                
                logging.info(f"Processando mensagem de {chat_id}: {text}")
                
                # Resposta simples para teste
                await enviar_resposta_teste(chat_id, "Webhook funcionando! ✅")
                
            elif 'callback_query' in update_data:
                callback = update_data['callback_query']
                logging.info(f"Processando callback: {callback.get('data', '')}")
                
    except Exception as e:
        logging.error(f"Erro ao processar update: {e}")

async def enviar_resposta_teste(chat_id: int, texto: str):
    """Envia uma resposta de teste via API do Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": texto
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    logging.info(f"Mensagem enviada para {chat_id}")
                else:
                    logging.error(f"Erro ao enviar mensagem: {resp.status}")
    except Exception as e:
        logging.error(f"Erro ao enviar resposta teste: {e}")

@routes.get("/health")
async def health_check(request):
    """Endpoint para verificar se o webhook está funcionando"""
    return web.json_response({
        "status": "ok",
        "bot_integrado": BOT_INTEGRADO,
        "timestamp": asyncio.get_event_loop().time(),
        "webhook_url": f"{WEBHOOK_BASE_URL}/webhook/{WEBHOOK_SECRET}",
        "production": Config.IS_PRODUCTION,
        "server_url": WEBHOOK_BASE_URL
    })

@routes.get("/webhook_info")
async def webhook_info(request):
    """Mostra informações sobre o webhook atual"""
    async with aiohttp.ClientSession() as session:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
        
        async with session.get(telegram_url) as resp:
            result = await resp.json()
            logging.info(f"Info webhook atual: {result}")
            return web.json_response(result)

@routes.post("/set_webhook")
async def set_webhook_endpoint(request):
    """Configura o webhook no Telegram"""
    if not WEBHOOK_BASE_URL:
        return web.json_response({
            "error": "WEBHOOK_BASE_URL não configurada"
        }, status=400)
    
    webhook_url = f"{WEBHOOK_BASE_URL}/webhook/{WEBHOOK_SECRET}"
    
    async with aiohttp.ClientSession() as session:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        payload = {
            "url": webhook_url,
            "drop_pending_updates": True,
            "max_connections": 40,
            "allowed_updates": ["message", "callback_query"]
        }
        
        async with session.post(telegram_url, json=payload) as resp:
            result = await resp.json()
            logging.info(f"Resultado setWebhook: {result}")
            return web.json_response(result)

@routes.post("/remove_webhook")
async def remove_webhook_endpoint(request):
    """Remove o webhook do Telegram (volta para polling)"""
    async with aiohttp.ClientSession() as session:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        payload = {
            "drop_pending_updates": True
        }
        
        async with session.post(telegram_url, json=payload) as resp:
            result = await resp.json()
            logging.info(f"Webhook removido: {result}")
            return web.json_response(result)

@routes.get("/test_webhook_config")
async def test_webhook_config(request):
    """Testa a configuração do webhook para produção"""
    webhook_url = f"{WEBHOOK_BASE_URL}/webhook/{WEBHOOK_SECRET}"
    
    return web.json_response({
        "webhook_url": webhook_url,
        "production": Config.IS_PRODUCTION,
        "server_base": WEBHOOK_BASE_URL,
        "bot_token_configured": bool(BOT_TOKEN and BOT_TOKEN != "COLOQUE_SEU_TOKEN_AQUI"),
        "ready_for_production": Config.IS_PRODUCTION and bool(BOT_TOKEN),
        "instructions": {
            "1": "Configure o webhook usando POST /set_webhook",
            "2": f"Telegram enviará updates para: {webhook_url}",
            "3": "Verifique status com GET /webhook_info"
        }
    })

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logging.info(f"Iniciando servidor webhook de teste na porta {port}")
    web.run_app(app, host="0.0.0.0", port=port)
