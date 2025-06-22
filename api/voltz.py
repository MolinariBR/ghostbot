"""
Módulo para integração com o backend do Ghost para saques via Lightning Network (Voltz).
"""
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class VoltzAPI:
    """Cliente para o backend do Ghost para operações de saque via Lightning Network."""
    
    def __init__(self, backend_url: str = 'https://ghostp2p.squareweb.app/voltz'):
        """
        Inicializa o cliente do backend.
        
        Args:
            backend_url: URL base do backend (ex: https://ghostp2p.squareweb.app/voltz)
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
