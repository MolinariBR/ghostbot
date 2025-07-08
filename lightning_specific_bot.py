#!/usr/bin/env python3
"""
Lightning Bot Específico - Processa apenas depósito específico do usuário
Evita spam de notificações de todos os depósitos do sistema
"""

import requests
import json
import time
import logging
from datetime import datetime
import sys
import os

# Configurações
SPECIFIC_ENDPOINT = "https://useghost.squareweb.app/api/lightning_cron_specific.php"
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Configurar com token real
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mau/bot/ghost/logs/lightning_specific.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class LightningSpecificBot:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
    
    def process_specific_deposit(self, depix_id, chat_id):
        """
        Processa um depósito Lightning específico para um usuário específico
        
        Args:
            depix_id: ID do depósito a processar
            chat_id: Chat ID do usuário
        """
        try:
            logging.info(f"Processando depósito específico {depix_id} para chat {chat_id}")
            
            # Consultar endpoint específico
            url = f"{SPECIFIC_ENDPOINT}?depix_id={depix_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('success'):
                logging.error(f"Erro ao processar {depix_id}: {data.get('error')}")
                return False
            
            result = data.get('result', {})
            status = result.get('status')
            
            # Verificar se precisa de ação do usuário
            if status == 'awaiting_client_invoice':
                amount_sats = result.get('amount_sats', 0)
                amount_brl = result.get('amount_brl', 0)
                
                # Enviar mensagem específica para este usuário
                success = self.send_lightning_request(
                    chat_id=chat_id,
                    depix_id=depix_id,
                    amount_sats=amount_sats,
                    amount_brl=amount_brl
                )
                
                if success:
                    logging.info(f"✅ Notificação enviada para chat {chat_id} - Depósito {depix_id}")
                    return True
                else:
                    logging.error(f"❌ Falha ao enviar notificação para chat {chat_id}")
                    return False
            else:
                logging.info(f"Depósito {depix_id} não precisa de ação: {status}")
                return True
                
        except Exception as e:
            logging.error(f"Erro ao processar depósito {depix_id}: {e}")
            return False
    
    def send_lightning_request(self, chat_id, depix_id, amount_sats, amount_brl):
        """Envia mensagem solicitando Lightning Address/Invoice para usuário específico"""
        try:
            message = f"""🎉 *SEU DEPÓSITO PIX FOI CONFIRMADO!*

💰 *Valor depositado:* R$ {amount_brl:.2f}
⚡ *Bitcoin a receber:* {amount_sats:,} sats
📄 *ID do seu depósito:* `{depix_id}`

🔗 *Para receber seus bitcoins via Lightning Network:*

📝 *Envie uma das opções:*
• *Lightning Address:* usuario@walletofsatoshi.com
• *BOLT11 Invoice:* lnbc1...

💡 *Dica:* Use wallets como Wallet of Satoshi, Phoenix, ou Breez

⏱️ *Responda com seu endereço Lightning para processar o pagamento automaticamente.*

🆔 *Seu depósito específico:* `{depix_id}`"""
            
            result = self.send_telegram_message(chat_id, message)
            return result.get('success', False)
            
        except Exception as e:
            logging.error(f"Erro ao preparar notificação específica: {e}")
            return False
    
    def send_telegram_message(self, chat_id, message):
        """Envia mensagem via API do Telegram"""
        try:
            url = f"{TELEGRAM_API}/sendMessage"
            
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            response = self.session.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    return {'success': True, 'message_id': result['result']['message_id']}
                else:
                    return {'success': False, 'error': f"API Telegram erro: {result}"}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {'success': False, 'error': f"Erro na requisição: {e}"}

def main():
    """Função principal - pode ser chamada com depix_id específico"""
    
    if len(sys.argv) < 3:
        print("Uso: python lightning_specific_bot.py <depix_id> <chat_id>")
        print("Exemplo: python lightning_specific_bot.py 0197e9e7d0d17dfc9b9ee24c0c36ba2a 7910260237")
        sys.exit(1)
    
    depix_id = sys.argv[1]
    chat_id = sys.argv[2]
    
    print(f"🚀 Processando depósito específico {depix_id} para chat {chat_id}")
    
    bot = LightningSpecificBot()
    success = bot.process_specific_deposit(depix_id, chat_id)
    
    if success:
        print(f"✅ Depósito {depix_id} processado com sucesso!")
    else:
        print(f"❌ Erro ao processar depósito {depix_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()
