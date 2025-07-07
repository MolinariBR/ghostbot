"""
Módulo para integração com o backend do Ghost para saques via Lightning Network (Voltz).
"""
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class VoltzAPI:
    """Cliente para o backend do Ghost para operações de saque via Lightning Network."""
    
    def __init__(self, backend_url: str = 'https://useghost.squareweb.app/voltz'):
        """
        Inicializa o cliente do backend.
        
        Args:
            backend_url: URL base do backend (ex: https://useghost.squareweb.app/voltz)
        """
        self.backend_url = backend_url.rstrip('/')
        self.timeout = 30
    
    def create_withdraw_link(self, amount_sats: int, description: str = 'Saque Ghost Bot') -> Dict[str, str]:
        """
        Solicita ao backend a criação de um novo link de saque.
        
        Args:
            amount_sats: Valor do saque em satoshis
            description: Descrição do saque (opcional)
            
        Returns:
            dict: Dados do link de saque contendo 'id', 'lnurl' e 'qr_code_url'
        """
        endpoint = f'{self.backend_url}/create_withdraw.php'
        data = {
            'amount_sats': amount_sats,
            'description': description
        }
        try:
            response = requests.post(endpoint, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao requisitar link de saque ao backend: {str(e)}")
            raise Exception(f"Erro ao requisitar link de saque ao backend: {str(e)}")
    
    def get_wallet_balance(self) -> int:
        """
        Solicita ao backend o saldo atual da carteira.
        
        Returns:
            int: Saldo em satoshis
        """
        endpoint = f'{self.backend_url}/get_wallet_balance.php'
        try:
            response = requests.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get('balance', 0)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao requisitar saldo ao backend: {str(e)}")
            raise Exception(f"Erro ao requisitar saldo ao backend: {str(e)}")
    
    def format_withdraw_message(self, amount_sats: float, lnurl: str, qr_code_url: str) -> str:
        """
        Formata a mensagem de saque para o usuário.
        
        Args:
            amount_sats: Valor do saque em satoshis
            lnurl: LNURL para saque
            qr_code_url: URL do QR code
            
        Returns:
            str: Mensagem formatada
        """
        return (
            f"⚡ *Solicitação de Saque* ⚡\n\n"
            f"• Valor: *{amount_sats} sats*\n"
            f"• Rede: *Lightning Network*\n\n"
            "📱 *Como sacar:*\n"
            "1. Abra sua carteira de Lightning\n"
            "2. Escolha 'Enviar' ou 'Saque'\n"
            "3. Escaneie o QR code ou cole o LNURL abaixo:\n\n"
            f"`{lnurl}`\n\n"
            "💰 O valor será creditado em até 10 minutos."
        )
    
    def create_deposit_request(self, chatid: str, userid: str, amount_in_cents: int, 
                              taxa: float, moeda: str, send_amount: float) -> Dict[str, str]:
        """
        Cria registro no deposit.db para processamento automático pelo sistema Voltz.
        
        Args:
            chatid: ID do chat Telegram
            userid: ID do usuário
            amount_in_cents: Valor em centavos (R$ 10,00 = 1000)
            taxa: Taxa/comissão
            moeda: Moeda (BTC, USDT, etc)
            send_amount: Valor a enviar para cliente
            
        Returns:
            dict: Dados do depósito criado
        """
        endpoint = f'{self.backend_url}/../rest/deposit.php'
        
        # Gera depix_id único
        import time, random
        depix_id = f"voltz_{int(time.time())}_{random.randint(1000, 9999)}"
        
        data = {
            'user_id': userid,
            'chatid': chatid,
            'amount_in_cents': amount_in_cents,
            'taxa': taxa,
            'moeda': moeda,
            'rede': 'lightning',
            'address': 'voltz@mail.com',
            'forma_pagamento': 'PIX',
            'send': send_amount,
            'status': 'pending',
            'depix_id': depix_id
        }
        
        try:
            response = requests.post(endpoint, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return {
                    'depix_id': depix_id,
                    'status': 'pending',
                    'message': 'Depósito registrado. Invoice será gerado automaticamente.'
                }
            else:
                raise Exception(result.get('error', 'Erro ao registrar depósito'))
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao registrar depósito: {str(e)}")
            raise Exception(f"Erro ao registrar depósito: {str(e)}")

    def check_deposit_status(self, depix_id: str) -> Dict[str, str]:
        """Verifica status de um depósito via Voltz."""
        endpoint = f'{self.backend_url}/voltz/voltz_status.php'
        data = {'depix_id': depix_id}
        
        try:
            response = requests.post(endpoint, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            return result
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}

    def format_deposit_confirmation_message(self, depix_id: str, amount_in_cents: int, 
                                          moeda: str, send_amount: float) -> str:
        """
        Formata a mensagem de confirmação do depósito.
        
        Args:
            depix_id: ID único do depósito
            amount_in_cents: Valor em centavos
            moeda: Moeda escolhida
            send_amount: Valor a ser enviado
            
        Returns:
            str: Mensagem formatada
        """
        valor_real = amount_in_cents / 100
        
        return (
            f"✅ *Depósito Criado com Sucesso!* ✅\n\n"
            f"🆔 *ID do Depósito:* `{depix_id}`\n"
            f"💰 *Valor PIX:* R$ {valor_real:.2f}\n"
            f"⚡ *Você receberá:* {send_amount} {moeda}\n"
            f"🌐 *Rede:* Lightning Network\n\n"
            f"📱 *Próximos passos:*\n"
            f"• Aguarde o invoice Lightning ser gerado\n"
            f"• Você receberá o QR Code em instantes\n"
            f"• Use sua carteira Lightning para pagar\n\n"
            f"⏱️ *Status:* Processando..."
        )
            
    def format_invoice_message(self, amount_sats: int, payment_request: str, qr_code_url: str) -> str:
        """
        Formata a mensagem do invoice para o usuário.
        
        Args:
            amount_sats: Valor em satoshis
            payment_request: String do invoice (bolt11)
            qr_code_url: URL do QR code
            
        Returns:
            str: Mensagem formatada em Markdown
        """
        return (
            f"⚡ *Invoice Lightning Network* ⚡\n\n"
            f"• Valor: *{amount_sats:,} sats*\n\n"
            "📱 *Como pagar:*\n"
            "1. Abra sua carteira Lightning\n"
            "2. Escolha 'Pagar' ou 'Enviar'\n"
            "3. Escaneie o QR code ou cole o invoice abaixo:\n\n"
            f"`{payment_request}`\n\n"
            "⏱️ Este invoice expira em 1 hora.\n"
            "✅ Pagamento é confirmado instantaneamente."
        )
