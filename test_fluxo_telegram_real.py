#!/usr/bin/env python3
"""
Teste Real do Fluxo Completo - Ghost P2P Bot via Telegram
Simula um usuário real fazendo uma compra completa via Telegram, usando backend real e logando todas as respostas.
Salva o log detalhado no backend para debug posterior.
"""
import asyncio
import logging
import time
import re
from telegram import Bot, Update
from telegram.error import TelegramError
from typing import List, Dict, Any, Optional
import subprocess
import sqlite3
import requests

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações do teste
BOT_TOKEN = "7105509014:AAENhZArthrysOBoEmdA6vaxE72pobliahI"
CHAT_ID = 7910260237
LIGHTNING_ADDRESS = "bouncyflight79@walletofsatoshi.com"
VALOR = "10"
# Usar todos os depix_id reais fornecidos
DEPIX_IDS = [
    "0197e0ed06537df9820a28f5a5380a3b",
    "0197e10b5b8f7df9a6bf9430188534e4",
    "0197e12300eb7df9808ca5d7719ea40e",
    "0197e5214a377dfaae6e541f68057444"
]

# Caminho do log detalhado no backend
LOG_PATH = "../ghostbackend/testphp/teste_fluxo_telegram_debug.log"

async def aguardar_resposta(bot, chat_id, texto_esperado, timeout=15, log_func=None):
    """Aguarda até receber uma resposta do bot contendo o texto esperado. Loga todas as mensagens recebidas."""
    import time
    start = time.time()
    while time.time() - start < timeout:
        updates = await bot.get_updates()
        for u in updates:
            if u.message and u.message.chat_id == chat_id:
                if log_func:
                    log_func(f"[DEBUG] Mensagem recebida: {u.message.text}")
                if texto_esperado.lower() in u.message.text.lower():
                    return u.message.text
        await asyncio.sleep(1)
    return None

def buscar_pedido_no_banco(gtxid, db_path="../ghostbackend/data/deposit.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE gtxid = ?", (gtxid,))
    pedido = cursor.fetchone()
    conn.close()
    return pedido

def buscar_pedido_remoto(gtxid, base_url="https://useghost.squareweb.app/api/get_pedido.php"):
    try:
        resp = requests.get(base_url, params={"gtxid": gtxid}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("pedido"):
                return data["pedido"]
    except Exception as e:
        pass
    return None

async def main():
    bot = Bot(token=BOT_TOKEN)
    log_lines = []
    def log(msg):
        logger.info(msg)
        log_lines.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")

    log("==== INÍCIO DO TESTE FLUXO TELEGRAM REAL ====")
    try:
        for depix_id in DEPIX_IDS:
            log(f"\n--- Testando depix_id: {depix_id} ---")
            # 1. /start
            await bot.send_message(chat_id=CHAT_ID, text="/start")
            log("Enviado: /start")
            resp = await aguardar_resposta(bot, CHAT_ID, "Comprar", log_func=log)
            log(f"Recebido: {resp}")

            # 2. Comprar
            await bot.send_message(chat_id=CHAT_ID, text="Comprar")
            log("Enviado: Comprar")
            resp = await aguardar_resposta(bot, CHAT_ID, "BTC", log_func=log)
            log(f"Recebido: {resp}")

            # 3. BTC
            await bot.send_message(chat_id=CHAT_ID, text="BTC")
            log("Enviado: BTC")
            resp = await aguardar_resposta(bot, CHAT_ID, "Lightning", log_func=log)
            log(f"Recebido: {resp}")

            # 4. Lightning
            await bot.send_message(chat_id=CHAT_ID, text="Lightning")
            log("Enviado: Lightning")
            resp = await aguardar_resposta(bot, CHAT_ID, "valor do investimento", log_func=log)
            log(f"Recebido: {resp}")

            # 5. Valor
            await bot.send_message(chat_id=CHAT_ID, text=VALOR)
            log(f"Enviado: {VALOR}")
            resp = await aguardar_resposta(bot, CHAT_ID, "RESUMO DA COMPRA", log_func=log)
            if resp:
                log(f"Resumo do pedido capturado:\n{resp}")
                import re
                m = re.search(r"ID:\s*(\w+)", resp)
                id_pedido = m.group(1) if m else None
            else:
                log("Resumo do pedido NÃO encontrado!")
                id_pedido = None
            if id_pedido:
                log(f"ID do pedido capturado: {id_pedido}")
                log(f"Para consultar o status via curl, use:\n  curl -s 'https://useghost.squareweb.app/api/api_cotacao.php?action=consultar&id={id_pedido}'")
            else:
                log("ID do pedido NÃO encontrado!")

            # 6. Confirmar Pedido
            await bot.send_message(chat_id=CHAT_ID, text="Confirmar Pedido")
            log("Enviado: Confirmar Pedido")
            resp = await aguardar_resposta(bot, CHAT_ID, "registrado com sucesso", log_func=log)
            log(f"Recebido: {resp}")

            # 7. PIX
            await bot.send_message(chat_id=CHAT_ID, text="PIX")
            log("Enviado: PIX")
            resp = await aguardar_resposta(bot, CHAT_ID, "QR Code", log_func=log)
            log(f"Recebido: {resp}")

            # 8. Depix
            await bot.send_message(chat_id=CHAT_ID, text=depix_id)
            log(f"Enviado: {depix_id} (depix)")
            resp = await aguardar_resposta(bot, CHAT_ID, "confirmação do pagamento PIX", log_func=log)
            log(f"Recebido: {resp}")

            # 8.1 Consulta backend para buscar blockchainTxID e gtxid
            try:
                url = f"https://useghost.squareweb.app/api/deposit.php"
                params = {"action": "get", "depix_id": depix_id}
                r = requests.get(url, params=params, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    log(f"Consulta backend: status={data.get('status')}, blockchainTxID={data.get('blockchainTxID')}")
                    if data.get("blockchainTxID"):
                        log(f"✅ blockchainTxID encontrado: {data['blockchainTxID']}")
                        # Supondo que a resposta do backend inclui o gtxid
                        gtxid = data.get("gtxid")
                        if gtxid:
                            pedido = buscar_pedido_remoto(gtxid)
                            if pedido:
                                log(f"✅ Pedido encontrado no banco remoto: {pedido}")
                            else:
                                log(f"❌ Pedido NÃO encontrado no banco remoto para gtxid {gtxid}")
                    else:
                        log(f"❌ blockchainTxID NÃO encontrado para depix_id {depix_id}")
                else:
                    log(f"❌ Erro HTTP ao consultar backend: {r.status_code}")
            except Exception as e:
                log(f"❌ Erro ao consultar backend: {e}")

            # 9. Lightning Address
            await bot.send_message(chat_id=CHAT_ID, text=LIGHTNING_ADDRESS)
            log(f"Enviado: {LIGHTNING_ADDRESS} (Lightning Address)")
            resp = await aguardar_resposta(bot, CHAT_ID, "Endereço Lightning recebido", log_func=log)
            log(f"Recebido: {resp}")

    except Exception as e:
        log(f"ERRO: {e}")

    # Salva o log detalhado no backend
    with open(LOG_PATH, "w") as f:
        f.write("\n".join(log_lines))
    logger.info(f"Log detalhado salvo em {LOG_PATH}")

if __name__ == "__main__":
    asyncio.run(main()) 