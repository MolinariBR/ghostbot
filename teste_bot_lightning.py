#!/usr/bin/env python3
"""
Teste completo: Cria um depósito Lightning com PIX confirmado para testar o bot
"""

import sys
import os
import asyncio
import logging
import requests
import json
import time
import sqlite3
from datetime import datetime

# Detectar o diretório do projeto automaticamente
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = SCRIPT_DIR

# Adicionar o diretório do projeto ao path
sys.path.append(PROJECT_DIR)

from telegram import Bot

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def teste_bot_lightning():
    """Teste simples do bot Lightning."""
    
    try:
        # Carregar token do bot
        from tokens import Config
        bot_token = Config.BOT_TOKEN
        bot = Bot(token=bot_token)
        
        # Testar acesso à API
        logger.info("Testando acesso à API...")
        response = requests.get("https://useghost.squareweb.app/rest/deposit.php", timeout=20)
        logger.info(f"Status da API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            deposits = data.get('deposits', [])
            logger.info(f"Total de depósitos na API: {len(deposits)}")
            
            # Buscar depósito real específico
            depix_real = "0197e9e7d0d17dfc9b9ee24c0c36ba2a"
            for deposit in deposits:
                if deposit.get('depix_id') == depix_real:
                    logger.info(f"✅ Depósito real encontrado: {deposit}")
                    chatid = deposit.get('chatid')
                    
                    # Testar envio de mensagem
                    if chatid and chatid != '':
                        try:
                            test_message = f"""
🧪 **TESTE BOT LIGHTNING**

✅ API funcionando
✅ Depósito real encontrado: `{depix_real}`
✅ Bot conectado

⚡ Status: {deposit.get('status')}
🌐 Rede: {deposit.get('rede')}
💰 Valor: R$ {deposit.get('amount_in_cents', 0)/100:.2f}
🔗 TxID: {deposit.get('blockchainTxID', 'N/A')[:20]}...

🎯 **Bot está pronto para processar Lightning!**
                            """
                            
                            await bot.send_message(
                                chat_id=int(chatid),
                                text=test_message,
                                parse_mode='Markdown'
                            )
                            logger.info(f"✅ Mensagem de teste enviada para chat {chatid}")
                        except Exception as e:
                            logger.error(f"Erro ao enviar mensagem: {e}")
                    break
            else:
                logger.warning(f"Depósito real {depix_real} não encontrado na API")
        else:
            logger.error(f"Erro na API: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Erro geral: {e}")

if __name__ == "__main__":
    asyncio.run(teste_bot_lightning())
