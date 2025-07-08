#!/usr/bin/env python3
"""
Lightning Notification Bot - Monitor depósitos Lightning e notifica usuários
Executa periodicamente para detectar depósitos confirmados que precisam de Lightning Address
"""

import requests
import json
import time
import logging
from datetime import datetime
import sys
import os

# Configurações
LIGHTNING_ENDPOINT = "https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php"
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Configurar com token real
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
UPDATE_ENDPOINT = "https://useghost.squareweb.app/rest/deposit.php"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mau/bot/ghost/logs/lightning_notifier.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class LightningNotificationBot:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        
    def check_pending_deposits(self):
        """Verifica depósitos Lightning aguardando invoice do cliente"""
        try:
            logging.info("Consultando endpoint Lightning...")
            
            response = self.session.get(LIGHTNING_ENDPOINT)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('success'):
                logging.error(f"Erro na resposta Lightning: {data.get('error', 'Erro desconhecido')}")
                return []
            
            results = data.get('results', [])
            total = data.get('total_pending', 0)
            
            logging.info(f"Encontrados {total} depósitos Lightning no total")
            
            # Filtrar apenas os que aguardam invoice do cliente
            awaiting_invoice = []
            for result in results:
                result_data = result.get('result', {})
                if result_data.get('status') == 'awaiting_client_invoice':
                    awaiting_invoice.append({
                        'depix_id': result.get('depix_id'),
                        'amount_sats': result_data.get('amount_sats', 0),
                        'message': result_data.get('message', '')
                    })
            
            logging.info(f"Encontrados {len(awaiting_invoice)} depósitos aguardando invoice")
            return awaiting_invoice
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição Lightning: {e}")
            return []
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            return []
    
    def get_deposit_details(self, depix_id):
        """Consulta detalhes completos de um depósito"""
        try:
            url = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            deposits = data.get('deposits', [])
            
            if deposits and len(deposits) > 0:
                return deposits[0]  # Primeiro resultado
            
            return None
            
        except Exception as e:
            logging.error(f"Erro ao buscar detalhes do depósito {depix_id}: {e}")
            return None
    
    def send_lightning_request(self, deposit_details, amount_sats):
        """Envia mensagem solicitando Lightning Address/Invoice"""
        try:
            chat_id = deposit_details['chatid']
            depix_id = deposit_details['depix_id']
            amount_brl = float(deposit_details['amount_in_cents']) / 100
            
            # Verificar se já foi notificado
            if deposit_details.get('notified', 0) == 1:
                logging.info(f"Depósito {depix_id} já foi notificado, pulando...")
                return {'success': True, 'skipped': True}
            
            message = f"""🎉 *DEPÓSITO PIX CONFIRMADO!*

💰 *Valor depositado:* R$ {amount_brl:.2f}
⚡ *Bitcoin a receber:* {amount_sats:,} sats
📄 *ID do depósito:* `{depix_id}`

🔗 *Para receber seus bitcoins via Lightning Network:*

📝 Envie uma das opções:
• *Lightning Address:* usuario@walletofsatoshi.com
• *BOLT11 Invoice:* lnbc1...

💡 *Dica:* Use wallets como Wallet of Satoshi, Phoenix, ou Breez para gerar seu endereço Lightning.

⏱️ *Responda com seu endereço Lightning para processar o pagamento automaticamente.*"""
            
            result = self.send_telegram_message(chat_id, message)
            
            if result['success']:
                # Marcar como notificado
                self.mark_as_notified(depix_id)
                logging.info(f"Notificação enviada com sucesso para {chat_id} - Depósito {depix_id}")
            
            return result
            
        except Exception as e:
            logging.error(f"Erro ao preparar notificação: {e}")
            return {'success': False, 'error': str(e)}
    
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
    
    def mark_as_notified(self, depix_id):
        """Marca depósito como notificado no banco"""
        try:
            # Atualizar via endpoint REST
            url = UPDATE_ENDPOINT
            data = {
                'depix_id': depix_id,
                'notified': 1,
                'action': 'update'
            }
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            logging.info(f"Depósito {depix_id} marcado como notificado")
            
        except Exception as e:
            logging.error(f"Erro ao marcar como notificado: {e}")
    
    def process_notifications(self):
        """Processa todas as notificações pendentes"""
        try:
            logging.info("=== Iniciando verificação de notificações Lightning ===")
            
            pending_deposits = self.check_pending_deposits()
            
            if not pending_deposits:
                logging.info("Nenhum depósito aguardando notificação")
                return {
                    'success': True,
                    'total_pending': 0,
                    'notified': 0,
                    'errors': []
                }
            
            notified_count = 0
            errors = []
            
            for deposit in pending_deposits:
                try:
                    depix_id = deposit['depix_id']
                    amount_sats = deposit['amount_sats']
                    
                    logging.info(f"Processando depósito {depix_id} ({amount_sats} sats)")
                    
                    # Buscar detalhes completos
                    details = self.get_deposit_details(depix_id)
                    if not details:
                        errors.append({'depix_id': depix_id, 'error': 'Detalhes não encontrados'})
                        continue
                    
                    # Enviar notificação
                    result = self.send_lightning_request(details, amount_sats)
                    
                    if result['success']:
                        if not result.get('skipped'):
                            notified_count += 1
                    else:
                        errors.append({'depix_id': depix_id, 'error': result['error']})
                    
                    # Delay entre notificações
                    time.sleep(1)
                    
                except Exception as e:
                    errors.append({'depix_id': deposit.get('depix_id', 'unknown'), 'error': str(e)})
                    logging.error(f"Erro ao processar depósito: {e}")
            
            result = {
                'success': True,
                'total_pending': len(pending_deposits),
                'notified': notified_count,
                'errors': errors,
                'timestamp': datetime.now().isoformat()
            }
            
            logging.info(f"Processamento concluído: {notified_count}/{len(pending_deposits)} notificados")
            
            return result
            
        except Exception as e:
            logging.error(f"Erro crítico no processamento: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_continuous(self, interval_minutes=2):
        """Executa continuamente com intervalo específico"""
        logging.info(f"Iniciando monitoramento contínuo (intervalo: {interval_minutes} minutos)")
        
        while True:
            try:
                result = self.process_notifications()
                
                if result['success']:
                    if result['notified'] > 0:
                        logging.info(f"✅ {result['notified']} notificações enviadas")
                    
                    if result['errors']:
                        logging.warning(f"⚠️ {len(result['errors'])} erros encontrados")
                
                # Aguardar próxima execução
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logging.info("Interrompido pelo usuário")
                break
            except Exception as e:
                logging.error(f"Erro na execução contínua: {e}")
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente

def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        # Modo contínuo
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        bot = LightningNotificationBot()
        bot.run_continuous(interval)
    else:
        # Execução única
        bot = LightningNotificationBot()
        result = bot.process_notifications()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
