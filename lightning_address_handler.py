#!/usr/bin/env python3
"""
Lightning Address Handler - Processa Lightning Address/Invoice enviados pelos usuários
Integra com Voltz para fazer pagamentos Lightning automáticos
"""

import re
import requests
import json
import sqlite3
import logging
from datetime import datetime

# Configurações
VOLTZ_API_URL = "https://voltz.api.url"  # Configurar URL real da Voltz
VOLTZ_API_KEY = "YOUR_VOLTZ_API_KEY"  # Configurar chave real
BACKEND_URL = "https://useghost.squareweb.app"
DB_PATH = "/home/mau/bot/ghostbackend/data/deposit.db"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightningAddressHandler:
    
    def __init__(self):
        self.voltz_api_url = VOLTZ_API_URL
        self.voltz_api_key = VOLTZ_API_KEY
        
    def is_lightning_address(self, address):
        """Verifica se é Lightning Address (user@domain.com)"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, address.strip()) is not None
    
    def is_bolt11_invoice(self, invoice):
        """Verifica se é BOLT11 invoice válido"""
        invoice = invoice.strip()
        # BOLT11 começa com 'ln' seguido de 'bc' (mainnet) ou 'tb' (testnet)
        if not re.match(r'^ln(bc|tb)[a-z0-9]+$', invoice, re.IGNORECASE):
            return False
        # Deve ter pelo menos 50 caracteres
        return len(invoice) >= 50
    
    def get_pending_deposit_for_user(self, chat_id):
        """Busca depósito Lightning pendente para o usuário"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Buscar depósito Lightning mais recente não processado para este chat_id
            query = """
                SELECT depix_id, chatid, amount_in_cents, send, status, rede, notified
                FROM deposit 
                WHERE chatid = ? 
                AND rede = 'lightning'
                AND status = 'confirmed'
                AND notified = 1
                AND (lightning_address IS NULL OR lightning_address = '')
                ORDER BY id DESC
                LIMIT 1
            """
            
            cursor.execute(query, (str(chat_id),))
            result = cursor.fetchone()
            
            if result:
                columns = ['depix_id', 'chatid', 'amount_in_cents', 'send', 'status', 'rede', 'notified']
                return dict(zip(columns, result))
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar depósito pendente: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def resolve_lightning_address(self, lightning_address, amount_sats):
        """Resolve Lightning Address para BOLT11 invoice"""
        try:
            # Extrair domínio e usuário
            user, domain = lightning_address.split('@')
            
            # Consultar .well-known endpoint
            well_known_url = f"https://{domain}/.well-known/lnurlp/{user}"
            
            response = requests.get(well_known_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ERROR':
                return {'success': False, 'error': data.get('reason', 'Lightning Address inválido')}
            
            callback_url = data.get('callback')
            min_sendable = data.get('minSendable', 0) // 1000  # msat para sat
            max_sendable = data.get('maxSendable', 0) // 1000  # msat para sat
            
            # Verificar limites
            if amount_sats < min_sendable or amount_sats > max_sendable:
                return {
                    'success': False, 
                    'error': f'Valor {amount_sats} sats fora dos limites ({min_sendable}-{max_sendable} sats)'
                }
            
            # Solicitar invoice
            invoice_response = requests.get(
                callback_url,
                params={'amount': amount_sats * 1000},  # converter para msat
                timeout=10
            )
            invoice_response.raise_for_status()
            
            invoice_data = invoice_response.json()
            
            if invoice_data.get('status') == 'ERROR':
                return {'success': False, 'error': invoice_data.get('reason', 'Erro ao gerar invoice')}
            
            return {
                'success': True,
                'bolt11': invoice_data.get('pr'),
                'payment_hash': invoice_data.get('successAction', {}).get('message', '')
            }
            
        except Exception as e:
            logger.error(f"Erro ao resolver Lightning Address: {e}")
            return {'success': False, 'error': f'Erro na resolução: {str(e)}'}
    
    def pay_via_voltz(self, bolt11_invoice, amount_sats):
        """Executa pagamento via API Voltz"""
        try:
            # TODO: Implementar integração real com Voltz
            # Por enquanto, simular pagamento bem-sucedido
            
            logger.info(f"Simulando pagamento Voltz: {amount_sats} sats via {bolt11_invoice[:50]}...")
            
            # Simular resposta da Voltz
            return {
                'success': True,
                'payment_hash': 'simulated_hash_' + str(int(datetime.now().timestamp())),
                'amount_paid': amount_sats,
                'fee': 1,  # 1 sat de taxa
                'timestamp': datetime.now().isoformat()
            }
            
            # Código real da Voltz seria algo como:
            # headers = {'Authorization': f'Bearer {self.voltz_api_key}'}
            # payload = {'bolt11': bolt11_invoice, 'amount': amount_sats}
            # response = requests.post(f'{self.voltz_api_url}/pay', json=payload, headers=headers)
            # return response.json()
            
        except Exception as e:
            logger.error(f"Erro no pagamento Voltz: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_deposit_lightning_address(self, depix_id, lightning_address, payment_result=None):
        """Atualiza depósito com Lightning Address e resultado do pagamento"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if payment_result and payment_result.get('success'):
                # Pagamento bem-sucedido
                query = """
                    UPDATE deposit 
                    SET lightning_address = ?, 
                        lightning_status = 'completed',
                        payment_hash = ?,
                        lightning_paid_at = datetime('now')
                    WHERE depix_id = ?
                """
                cursor.execute(query, (
                    lightning_address,
                    payment_result.get('payment_hash', ''),
                    depix_id
                ))
            else:
                # Apenas salvar endereço (pagamento pendente ou falhado)
                status = 'failed' if payment_result else 'processing'
                query = """
                    UPDATE deposit 
                    SET lightning_address = ?, 
                        lightning_status = ?
                    WHERE depix_id = ?
                """
                cursor.execute(query, (lightning_address, status, depix_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar depósito: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def process_lightning_input(self, chat_id, user_input):
        """Processa entrada do usuário (Lightning Address ou BOLT11)"""
        try:
            user_input = user_input.strip()
            
            # Buscar depósito pendente para este usuário
            deposit = self.get_pending_deposit_for_user(chat_id)
            if not deposit:
                return {
                    'success': False,
                    'message': '❌ Nenhum depósito Lightning pendente encontrado para você.'
                }
            
            amount_sats = int(deposit.get('send', 0))
            depix_id = deposit['depix_id']
            
            # Determinar tipo de entrada
            if self.is_lightning_address(user_input):
                # Lightning Address
                logger.info(f"Processando Lightning Address: {user_input}")
                
                # Resolver para BOLT11
                resolution = self.resolve_lightning_address(user_input, amount_sats)
                if not resolution['success']:
                    return {
                        'success': False,
                        'message': f"❌ Erro ao processar Lightning Address: {resolution['error']}"
                    }
                
                bolt11 = resolution['bolt11']
                
            elif self.is_bolt11_invoice(user_input):
                # BOLT11 direto
                logger.info(f"Processando BOLT11 invoice")
                bolt11 = user_input
                
            else:
                return {
                    'success': False,
                    'message': '❌ Formato inválido. Envie um Lightning Address (user@domain.com) ou BOLT11 invoice (lnbc...).'
                }
            
            # Executar pagamento
            payment_result = self.pay_via_voltz(bolt11, amount_sats)
            
            # Atualizar banco
            self.update_deposit_lightning_address(depix_id, user_input, payment_result)
            
            if payment_result['success']:
                return {
                    'success': True,
                    'message': f'''✅ **PAGAMENTO LIGHTNING CONCLUÍDO!**

⚡ **Valor enviado:** {amount_sats:,} sats
🔗 **Destino:** {user_input}
🆔 **Payment Hash:** `{payment_result['payment_hash']}`
💰 **Taxa:** {payment_result.get('fee', 0)} sats
📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

🎉 **Seus bitcoins foram enviados com sucesso via Lightning Network!**''',
                    'payment_hash': payment_result['payment_hash']
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ Falha no pagamento: {payment_result.get('error', 'Erro desconhecido')}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar entrada Lightning: {e}")
            return {
                'success': False,
                'message': f"❌ Erro interno: {str(e)}"
            }

def test_handler():
    """Função de teste"""
    handler = LightningAddressHandler()
    
    # Teste Lightning Address
    print("🧪 Testando Lightning Address...")
    result = handler.process_lightning_input("7910260237", "test@walletofsatoshi.com")
    print(json.dumps(result, indent=2))
    
    # Teste BOLT11
    print("\n🧪 Testando BOLT11...")
    result = handler.process_lightning_input("7910260237", "lnbc10u1pjm9h7spp5...")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_handler()
