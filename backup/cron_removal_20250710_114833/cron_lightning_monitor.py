#!/usr/bin/env python3
"""
Cron job para monitorar transações Lightning pendentes.
Executa a cada 30 segundos e verifica se há depósitos Lightning 
com PIX confirmado (blockchainTxID presente) aguardando invoice.
"""

import sys
import os
import asyncio
import logging
import requests
from datetime import datetime

# Detectar o diretório do projeto automaticamente
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = SCRIPT_DIR  # Este script está na raiz do projeto

# Adicionar o diretório do projeto ao path
sys.path.append(PROJECT_DIR)

# Ativar o ambiente virtual programaticamente
activate_this = os.path.join(PROJECT_DIR, '.venv', 'bin', 'activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

from telegram import Bot
from handlers.lightning_integration import monitorar_pix_e_processar_lightning

# Configuração de logging
log_file = os.path.join(PROJECT_DIR, 'logs', 'lightning_cron.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def check_pending_lightning_deposits():
    """
    Verifica depósitos Lightning pendentes com PIX confirmado.
    """
    try:
        # Buscar depósitos Lightning pendentes no backend
        url = "https://useghost.squareweb.app/rest/deposit.php"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Erro ao buscar depósitos: HTTP {response.status_code}")
            return
        
        data = response.json()
        deposits = data.get('deposits', [])
        
        # Filtrar apenas Lightning com PIX confirmado mas invoice não processado
        lightning_pending = []
        for deposit in deposits:
            rede = deposit.get('rede', '').lower()
            blockchain_txid = deposit.get('blockchainTxID', '')
            status = deposit.get('status', '')
            depix_id = deposit.get('depix_id', '')
            chatid = deposit.get('chatid', '')
            
            # Condições para processar:
            # 1. É Lightning
            # 2. Tem blockchainTxID (PIX confirmado) 
            # 3. Status ainda não é completado
            # 4. Tem chatid válido
            if ('lightning' in rede and 
                blockchain_txid and blockchain_txid.strip() != '' and
                status not in ['completed', 'cancelled', 'failed'] and
                depix_id and chatid):
                lightning_pending.append(deposit)
        
        logger.info(f"Encontrados {len(lightning_pending)} depósitos Lightning pendentes com PIX confirmado")
        
        if not lightning_pending:
            return
        
        # Carregar token do bot
        try:
            from tokens import Config
            bot_token = Config.BOT_TOKEN
        except Exception as e:
            logger.error(f"Erro ao carregar token do bot: {e}")
            return
        
        bot = Bot(token=bot_token)
        
        # Processar cada depósito Lightning pendente
        for deposit in lightning_pending:
            depix_id = deposit['depix_id']
            chatid = int(deposit['chatid'])
            
            logger.info(f"Processando Lightning pendente: {depix_id} para chat {chatid}")
            
            try:
                # Usar a função corrigida que verifica blockchainTxID primeiro
                await monitorar_pix_e_processar_lightning(
                    depix_id=depix_id,
                    chat_id=chatid, 
                    is_lightning=True,
                    bot=bot
                )
            except Exception as e:
                logger.error(f"Erro ao processar Lightning {depix_id}: {e}")
        
    except Exception as e:
        logger.error(f"Erro no cron Lightning: {e}")

async def main():
    """Função principal do cron job."""
    logger.info("=== Iniciando verificação Lightning ===")
    await check_pending_lightning_deposits()
    logger.info("=== Verificação Lightning concluída ===")

if __name__ == "__main__":
    asyncio.run(main())
