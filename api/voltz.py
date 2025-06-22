"""
Módulo para integração com a API Voltz para saques via Lightning Network.
"""
import logging
import requests
from typing import Dict, Tuple, Optional
from urllib.parse import quote

# Configuração de logging
logger = logging.getLogger(__name__)

class VoltzAPI:
    """Cliente para a API Voltz para operações de saque via Lightning Network."""
    
    def __init__(self, base_url: str = 'https://lnvoltz.com'):
        """
        Inicializa o cliente da API Voltz.
        
        Args:
            base_url: URL base da API Voltz
        """
        self.base_url = base_url.rstrip('/')
        self.admin_key = '8fce34f4b0f8446a990418bd167dc644'
        self.wallet_id = 'f3c366b7fb6f43fa9467c4dccedaf824'
        self.timeout = 30
        
    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None, 
                      is_admin: bool = True) -> dict:
        """
        Executa uma requisição para a API Voltz.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint da API
            data: Dados a serem enviados (opcional)
            is_admin: Se True, usa a chave de administração
            
        Returns:
            dict: Resposta da API
            
        Raises:
            Exception: Em caso de erro na requisição
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': self.admin_key if is_admin else ''
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição para {url}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def create_withdraw_link(self, amount_sats: int, description: str = 'Saque Ghost Bot') -> Dict[str, str]:
        """
        Cria um novo link de saque.
        
        Args:
            amount_sats: Valor do saque em satoshis
            description: Descrição do saque (opcional)
            
        Returns:
            dict: Dados do link de saque contendo 'id', 'lnurl' e 'qr_code_url'
        """
        endpoint = '/withdraw/api/v1/links'
        data = {
            'title': description,
            'min_withdrawable': amount_sats * 1000,  # em msats
            'max_withdrawable': amount_sats * 1000,  # em msats
            'uses': 1,
            'wait_time': 1,  # 1 minuto
            'is_unique': True
        }
        
        try:
            response = self._make_request('POST', endpoint, data)
            
            # Gera a URL do QR code
            qr_code_url = self._generate_qr_code(response['lnurl'])
            
            return {
                'id': response['id'],
                'lnurl': response['lnurl'],
                'qr_code_url': qr_code_url
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar link de saque: {str(e)}")
            raise Exception(f"Erro ao criar link de saque: {str(e)}")
    
    def get_wallet_balance(self) -> int:
        """
        Obtém o saldo atual da carteira em satoshis.
        
        Returns:
            int: Saldo em satoshis
        """
        endpoint = f'/api/v1/wallet/{self.wallet_id}'
        
        try:
            response = self._make_request('GET', endpoint, is_admin=True)
            return response.get('balance', 0) // 1000  # Converte de msats para sats
            
        except Exception as e:
            logger.error(f"Erro ao obter saldo: {str(e)}")
            raise Exception(f"Erro ao obter saldo: {str(e)}")
    
    @staticmethod
    def _generate_qr_code(lnurl: str) -> str:
        """
        Gera uma URL de QR code a partir de um LNURL.
        
        Args:
            lnurl: LNURL para gerar o QR code
            
        Returns:
            str: URL do QR code
        """
        encoded_lnurl = quote(lnurl)
        return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_lnurl}"
    
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
