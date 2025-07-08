#!/usr/bin/env python3
"""
Cron Lightning Monitor - Versão Robusta
Monitora depósitos Lightning aguardando invoice do cliente
"""

import sys
import os
import asyncio
import logging
import requests
import time
from datetime import datetime

# Detectar o diretório do projeto automaticamente
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = SCRIPT_DIR

# Adicionar o diretório do projeto ao path
sys.path.append(PROJECT_DIR)

from telegram import Bot

# Configuração de logging
log_file = os.path.join(PROJECT_DIR, 'logs', 'lightning_cron_robust.log')
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

async def verificar_deposito_especifico(depix_id):
    """Verificar um depósito específico via API com retry."""
    
    max_retries = 3
    for tentativa in range(max_retries):
        try:
            logger.info(f"Tentativa {tentativa + 1} - Verificando depósito {depix_id}")
            
            url = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                deposits = data.get('deposits', [])
                
                if deposits:
                    deposit = deposits[0]
                    logger.info(f"✅ Depósito {depix_id} encontrado:")
                    logger.info(f"   Status: {deposit.get('status')}")
                    logger.info(f"   Rede: {deposit.get('rede')}")
                    logger.info(f"   BlockchainTxID: {deposit.get('blockchainTxID')}")
                    logger.info(f"   ChatID: {deposit.get('chatid')}")
                    logger.info(f"   Valor: R$ {deposit.get('amount_in_cents', 0)/100:.2f}")
                    
                    return deposit
                else:
                    logger.warning(f"Depósito {depix_id} não encontrado na resposta")
                    return None
            else:
                logger.error(f"Erro HTTP {response.status_code} ao consultar {depix_id}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout na tentativa {tentativa + 1} para {depix_id}")
            if tentativa < max_retries - 1:
                time.sleep(5)
        except Exception as e:
            logger.error(f"Erro na tentativa {tentativa + 1} para {depix_id}: {e}")
            if tentativa < max_retries - 1:
                time.sleep(5)
    
    return None

async def processar_lightning_com_bot(deposit, bot):
    """Processar depósito Lightning via bot."""
    
    depix_id = deposit['depix_id']
    chatid = deposit['chatid']
    status = deposit.get('status', '')
    rede = deposit.get('rede', '')
    blockchain_txid = deposit.get('blockchainTxID', '')
    amount_cents = deposit.get('amount_in_cents', 0)
    
    logger.info(f"🔄 Processando Lightning: {depix_id}")
    
    # Verificar se é Lightning com PIX confirmado
    if ('lightning' not in rede.lower() or 
        not blockchain_txid or blockchain_txid.strip() == ''):
        logger.info(f"❌ Depósito {depix_id} não é Lightning confirmado")
        return False
    
    # Verificar se status permite processamento
    if status in ['completed', 'cancelled', 'failed']:
        logger.info(f"❌ Depósito {depix_id} já finalizado: {status}")
        return False
    
    # Calcular satoshis (BTC ~R$ 600.000 = ~166.67 sats/real)
    amount_sats = int((amount_cents / 100) * 166.67)
    
    logger.info(f"💰 Valor: R$ {amount_cents/100:.2f} = {amount_sats} sats")
    
    # Verificar se chat é válido
    try:
        chat_id_int = int(chatid)
    except (ValueError, TypeError):
        logger.error(f"❌ ChatID inválido para {depix_id}: {chatid}")
        return False
    
    # Enviar mensagem solicitando invoice Lightning
    try:
        message = f"""
⚡ **PIX CONFIRMADO - LIGHTNING PENDENTE**

💰 **Valor confirmado:** R$ {amount_cents/100:.2f}
⚡ **BTC a receber:** {amount_sats:,} sats

🔗 **PRÓXIMO PASSO:**
Para receber seus bitcoins via Lightning Network, você precisa fornecer um **invoice Lightning** da sua carteira.

📱 **Como gerar invoice:**
• Abra sua carteira Lightning (Phoenix, Wallet of Satoshi, etc.)
• Clique em "Receber"
• Digite o valor: **{amount_sats} sats**
• Copie o invoice gerado
• Cole aqui no chat

⏰ **Aguardando seu invoice Lightning...**

💡 **Dica:** O invoice deve começar com "lnbc" ou "lntb"

🔗 **Depósito ID:** `{depix_id}`
        """
        
        await bot.send_message(
            chat_id=chat_id_int,
            text=message,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Mensagem Lightning enviada para chat {chat_id_int}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem para {chat_id_int}: {e}")
        return False

async def main():
    """Função principal do cron robusto."""
    logger.info("=== INICIANDO CRON LIGHTNING ROBUSTO ===")
    
    try:
        # Carregar token do bot
        from tokens import Config
        bot_token = Config.BOT_TOKEN
        bot = Bot(token=bot_token)
        logger.info("✅ Bot inicializado")
        
        # Lista de depósitos para verificar (incluindo o real)
        depositos_para_verificar = [
            "0197e9e7d0d17dfc9b9ee24c0c36ba2a",  # Depósito real
        ]
        
        # Tentar buscar todos os depósitos Lightning da API
        try:
            logger.info("🔍 Tentando buscar todos os depósitos Lightning...")
            url_all = "https://useghost.squareweb.app/rest/deposit.php"
            response = requests.get(url_all, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                deposits = data.get('deposits', [])
                logger.info(f"✅ {len(deposits)} depósitos encontrados na API")
                
                # Filtrar Lightning com PIX confirmado
                for deposit in deposits:
                    rede = deposit.get('rede', '').lower()
                    blockchain_txid = deposit.get('blockchainTxID', '')
                    status = deposit.get('status', '')
                    depix_id = deposit.get('depix_id', '')
                    chatid = deposit.get('chatid', '')
                    
                    if ('lightning' in rede and 
                        blockchain_txid and blockchain_txid.strip() != '' and
                        status not in ['completed', 'cancelled', 'failed'] and
                        depix_id and chatid):
                        
                        if depix_id not in depositos_para_verificar:
                            depositos_para_verificar.append(depix_id)
                
                logger.info(f"🎯 Total de depósitos Lightning para processar: {len(depositos_para_verificar)}")
            else:
                logger.warning(f"⚠️ API retornou HTTP {response.status_code}, usando lista manual")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao buscar todos os depósitos: {e}, usando lista manual")
        
        # Processar cada depósito
        processados = 0
        for depix_id in depositos_para_verificar:
            logger.info(f"🔍 Verificando depósito: {depix_id}")
            
            deposit = await verificar_deposito_especifico(depix_id)
            
            if deposit:
                resultado = await processar_lightning_com_bot(deposit, bot)
                if resultado:
                    processados += 1
                    logger.info(f"✅ Depósito {depix_id} processado com sucesso")
                else:
                    logger.info(f"⏭️ Depósito {depix_id} não precisou ser processado")
            else:
                logger.warning(f"❌ Depósito {depix_id} não encontrado")
            
            # Pequena pausa entre processamentos
            await asyncio.sleep(2)
        
        logger.info(f"🎉 CRON CONCLUÍDO - {processados} depósitos processados")
        
    except Exception as e:
        logger.error(f"❌ ERRO GERAL NO CRON: {e}")

if __name__ == "__main__":
    asyncio.run(main())
