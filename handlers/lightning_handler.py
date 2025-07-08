#!/usr/bin/env python3
"""
Lightning Handler para Ghost Bot - Detecta e processa Lightning Address/Invoice
Integra-se com o backend para processar pagamentos Lightning automaticamente
"""

import re
import requests
import json
from datetime import datetime

# Configurações
BACKEND_URL = "https://useghost.squareweb.app"
PROCESS_LIGHTNING_ENDPOINT = f"{BACKEND_URL}/api/process_lightning_address.php"

class GhostBotLightningHandler:
    
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.telegram_api = f"https://api.telegram.org/bot{bot_token}"
        
    def is_lightning_address(self, text):
        """Verifica se o texto é um Lightning Address (user@domain.com)"""
        if not text or '@' not in text:
            return False
        
        # Regex para Lightning Address
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, text.strip()) is not None
    
    def is_bolt11_invoice(self, text):
        """Verifica se o texto é um BOLT11 invoice"""
        if not text:
            return False
        
        text = text.strip()
        # BOLT11 começa com 'ln' seguido de 'bc' (mainnet) ou 'tb' (testnet)
        if not re.match(r'^ln(bc|tb)[a-z0-9]+$', text, re.IGNORECASE):
            return False
        
        # Deve ter pelo menos 50 caracteres
        return len(text) >= 50
    
    def is_lightning_input(self, text):
        """Verifica se o texto é Lightning Address ou BOLT11"""
        return self.is_lightning_address(text) or self.is_bolt11_invoice(text)
    
    def process_lightning_input(self, chat_id, user_input):
        """Processa Lightning Address/Invoice via backend"""
        try:
            payload = {
                'chat_id': str(chat_id),
                'user_input': user_input.strip()
            }
            
            response = requests.post(
                PROCESS_LIGHTNING_ENDPOINT,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'message': f'❌ Erro no servidor: HTTP {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': '❌ Timeout na requisição. Tente novamente.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'❌ Erro de conexão: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Erro inesperado: {str(e)}'
            }
    
    def send_message(self, chat_id, text, parse_mode='Markdown'):
        """Envia mensagem via Telegram"""
        try:
            url = f"{self.telegram_api}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            return False
    
    def handle_message(self, chat_id, message_text, user_name=""):
        """Handler principal para processar mensagens do usuário"""
        try:
            message_text = message_text.strip()
            
            # Verificar se é Lightning Address ou BOLT11
            if self.is_lightning_input(message_text):
                
                # Notificar que está processando
                processing_msg = "⚡ *Processando seu Lightning Address...*\n\n" \
                               "🔄 Validando endereço\n" \
                               "💫 Preparando pagamento\n" \
                               "⏳ Aguarde um momento..."
                
                self.send_message(chat_id, processing_msg)
                
                # Processar via backend
                result = self.process_lightning_input(chat_id, message_text)
                
                # Enviar resultado
                self.send_message(chat_id, result['message'])
                
                # Log da transação
                status = "SUCCESS" if result['success'] else "FAILED"
                print(f"[{datetime.now()}] Lightning {status}: {chat_id} -> {message_text[:20]}...")
                
                return {
                    'processed': True,
                    'success': result['success'],
                    'type': 'lightning_address' if self.is_lightning_address(message_text) else 'bolt11_invoice'
                }
            
            return {'processed': False, 'reason': 'not_lightning_input'}
            
        except Exception as e:
            error_msg = f"❌ Erro interno ao processar Lightning Address: {str(e)}"
            self.send_message(chat_id, error_msg)
            print(f"Erro no Lightning Handler: {e}")
            
            return {'processed': True, 'success': False, 'error': str(e)}

def test_lightning_handler():
    """Função de teste do handler"""
    # Token de teste (use o token real do Ghost Bot)
    BOT_TOKEN = "7105509014:AAENhZArthrysOBoEmdA6vaxE72pobliahI"
    
    handler = GhostBotLightningHandler(BOT_TOKEN)
    
    # Teste Lightning Address
    print("🧪 Testando Lightning Address...")
    result = handler.handle_message("7910260237", "test@walletofsatoshi.com", "TestUser")
    print(f"Resultado: {result}")
    
    # Teste BOLT11
    print("\n🧪 Testando BOLT11...")
    result = handler.handle_message("7910260237", "lnbc10u1pjm9h7spp5abc123def456", "TestUser")
    print(f"Resultado: {result}")
    
    # Teste entrada inválida
    print("\n🧪 Testando entrada inválida...")
    result = handler.handle_message("7910260237", "texto normal", "TestUser")
    print(f"Resultado: {result}")

if __name__ == "__main__":
    test_lightning_handler()
