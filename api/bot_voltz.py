"""
Módulo para integração com a API Voltz do GhostBot.

Fornece uma interface Python para interagir com o backend Voltz (api_voltz.php)
"""

import requests
import json
import logging
from typing import Dict, Optional, Any, Union
from decimal import Decimal
from config.config import BASE_URL

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('voltz_api')

class VoltzAPIError(Exception):
    """Exceção para erros na API Voltz."""
    pass

class VoltzAPI:
    """
    Cliente para a API Voltz do GhostBot.
    
    Esta classe fornece métodos para interagir com o backend Voltz,
    permitindo criar faturas, realizar pagamentos e verificar status.
    """
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Inicializa o cliente da API Voltz.
        
        Args:
            api_url: URL base da API (opcional, usa BASE_URL do config.py por padrão)
            api_key: Chave de API para autenticação (opcional, pode ser definida depois)
        """
        self.api_url = (api_url or f"{BASE_URL.rstrip('/')}/api_voltz.php").rstrip('/')
        self.api_key = api_key
        self._session = requests.Session()
        self._update_headers()
        
        logger.info(f"Inicializado VoltzAPI com URL: {self.api_url}")
    
    def _update_headers(self):
        """Atualiza os cabeçalhos HTTP com o token de autenticação."""
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'GhostBot/VoltzAPI/1.0',
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
    
    def set_api_key(self, api_key: str):
        """Define a chave de API para autenticação."""
        self.api_key = api_key
        self._update_headers()
        logger.info("Chave de API atualizada")
    
    def _make_request(
        self, 
        method: str, 
        action: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Faz uma requisição para a API Voltz.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            action: Ação da API (ex: 'create_invoice', 'pay_invoice')
            data: Dados a serem enviados no corpo da requisição (para POST/PUT)
            params: Parâmetros de consulta para a URL (para GET)
            
        Returns:
            Dicionário com a resposta da API
            
        Raises:
            VoltzAPIError: Em caso de erro na requisição ou resposta inválida
        """
        url = f"{self.api_url}?action={action}"
        
        # Log da requisição
        log_data = {
            'url': url,
            'method': method,
            'action': action,
            'data': data,
            'params': params
        }
        logger.debug(f"Fazendo requisição: {json.dumps(log_data, default=str)}")
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            # Log da resposta bruta
            logger.debug(f"Resposta recebida - Status: {response.status_code}")
            logger.debug(f"Cabeçalhos: {dict(response.headers)}")
            
            # Tenta fazer o parse do JSON
            try:
                response_data = response.json()
                logger.debug(f"Resposta JSON: {json.dumps(response_data, indent=2, default=str)}")
            except ValueError as e:
                error_msg = f"Resposta não é um JSON válido: {response.text}"
                logger.error(error_msg)
                raise VoltzAPIError(error_msg) from e
            
            # Verifica se houve erro na resposta
            if not response_data.get('success', False):
                error_msg = response_data.get('error', 'Erro desconhecido na API')
                logger.error(f"Erro na API: {error_msg}")
                raise VoltzAPIError(f"Erro na API: {error_msg}")
            
            return response_data.get('data', {})
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição para {url}: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - Status: {e.response.status_code}"
                try:
                    error_data = e.response.json()
                    error_msg += f" - {json.dumps(error_data, indent=2)}"
                except:
                    error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise VoltzAPIError(error_msg) from e
    
    # --- Métodos da API ---
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Obtém o saldo da carteira Voltz.
        
        Returns:
            Dicionário com o saldo e moeda
            
        Example:
            {
                'balance': 1000000,  # em satoshis
                'currency': 'sats'
            }
        """
        return self._make_request('GET', 'balance')
    
    def create_invoice(
        self, 
        amount: Union[int, float, Decimal],
        memo: str = '',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Cria uma nova fatura de recebimento.
        
        Args:
            amount: Valor em satoshis
            memo: Descrição opcional do pagamento
            **kwargs: Parâmetros adicionais para a API
            
        Returns:
            Dicionário com os dados da fatura
            
        Example:
            {
                'payment_request': 'lnbc10n1p5...',
                'payment_hash': 'abc123...',
                'expiry': 3600,
                'created_at': 1620000000
            }
        """
        if isinstance(amount, (float, Decimal)):
            amount = int(amount)
            
        return self._make_request('POST', 'create_invoice', {
            'amount': amount,
            'memo': memo,
            **kwargs
        })
    
    def pay_invoice(
        self, 
        invoice: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Paga uma fatura Lightning.
        
        Args:
            invoice: Fatura BOLT11 ou endereço Lightning
            **kwargs: Parâmetros adicionais para a API
            
        Returns:
            Dicionário com o resultado do pagamento
            
        Example:
            {
                'payment_hash': 'abc123...',
                'status': 'pending',
                'timestamp': 1620000000
            }
        """
        return self._make_request('POST', 'pay_invoice', {
            'invoice': invoice,
            **kwargs
        })
    
    def decode_invoice(self, invoice: str) -> Dict[str, Any]:
        """
        Decodifica uma fatura Lightning.
        
        Args:
            invoice: Fatura BOLT11 ou endereço Lightning
            
        Returns:
            Dicionário com os detalhes da fatura
            
        Example:
            {
                'amount': 1000,
                'description': 'Pagamento de teste',
                'payment_hash': 'abc123...',
                'expiry': 3600,
                'timestamp': 1620000000,
                'expires_at': 1620003600
            }
        """
        return self._make_request('POST', 'decode_invoice', {
            'invoice': invoice
        })
    
    def check_payment(self, payment_hash: str) -> Dict[str, Any]:
        """
        Verifica o status de um pagamento.
        
        Args:
            payment_hash: Hash do pagamento a ser verificado
            
        Returns:
            Dicionário com o status do pagamento
            
        Example:
            {
                'paid': True,
                'payment_hash': 'abc123...',
                'checked_at': 1620000000,
                'details': {
                    'status': 'completed',
                    'amount': 1000,
                    'fee': 2,
                    'preimage': 'xyz789...',
                    'created_at': '2025-07-13T14:30:00Z',
                    'resolved_at': '2025-07-13T14:30:10Z'
                }
            }
        """
        return self._make_request('GET', 'check_payment', params={'hash': payment_hash})


# Instância global para ser importada por outros módulos
voltz_api = VoltzAPI()

# Exemplo de uso
if __name__ == "__main__":
    import sys
    
    # Configura logging para exibir no console
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Exemplo de uso (descomente e ajuste conforme necessário)
    try:
        # Criar uma fatura de teste
        # invoice = voltz_api.create_invoice(1000, "Pagamento de teste")
        # print("Fatura criada:", json.dumps(invoice, indent=2))
        
        # Verificar status de um pagamento
        # status = voltz_api.check_payment("hash_do_pagamento")
        # print("Status do pagamento:", json.dumps(status, indent=2))
        pass
        
    except VoltzAPIError as e:
        print(f"Erro na API Voltz: {e}", file=sys.stderr)
        sys.exit(1)
