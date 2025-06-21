"""
Módulo para integração com a API de pagamentos PIX do servidor VPS.
"""
import os
import json
import requests
import logging
from typing import Dict, Optional, Any
from decimal import Decimal

# Configuração de logging
logger = logging.getLogger(__name__)

class PixAPIError(Exception):
    """Exceção para erros na API de pagamentos PIX."""
    pass

class PixAPI:
    """Cliente para a API de pagamentos PIX do servidor VPS."""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Inicializa o cliente da API PIX.
        
        Args:
            api_url: URL base da API (opcional, busca do ambiente)
        """
        self.api_url = (api_url or os.getenv('PIX_API_URL', 'https://ghostp2p.squareweb.app/api/bot_deposit.php')).rstrip('/')
        
        if not self.api_url:
            raise PixAPIError("URL da API PIX não configurada. Defina a variável de ambiente PIX_API_URL")
    
    def _make_request(self, path: str = '', data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Faz uma requisição para a API PIX.
        
        Args:
            path: Caminho do endpoint (opcional)
            data: Dados a serem enviados no corpo da requisição
            
        Returns:
            Dict: Resposta da API
            
        Raises:
            PixAPIError: Em caso de erro na requisição
        """
        if data is None:
            data = {}
            
        # Usa a URL base diretamente, sem adicionar caminhos adicionais
        url = self.api_url
        logger.info(f"Fazendo requisição para: {url}")
        logger.info(f"Dados da requisição: {data}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'GhostBot/1.0'
        }
        
        try:
            logger.info(f"Enviando requisição POST para {url}")
            
            # Adiciona timestamp à requisição
            import time
            data['timestamp'] = int(time.time())
            
            response = requests.post(
                url=url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Resposta recebida - Status: {response.status_code}")
            logger.info(f"Conteúdo da resposta: {response.text[:500]}...")  # Limita o log aos primeiros 500 caracteres
            
            response.raise_for_status()  # Levanta exceção para códigos de erro HTTP
            
            # Verifica se a resposta é um JSON válido
            try:
                response_data = response.json()
                logger.info(f"Resposta JSON decodificada: {response_data}")
            except ValueError as e:
                error_msg = f"Resposta inválida do servidor: {response.text}"
                logger.error(error_msg)
                raise PixAPIError(error_msg) from e
            
            # A API pode retornar o resultado diretamente ou em um campo 'data'
            if 'data' in response_data:
                return response_data['data']
            return response_data
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição para {url}: {str(e)}"
            logger.error(error_msg)
            raise PixAPIError(error_msg) from e
    
    def criar_pagamento(self, valor_centavos: int, chave_pix: str) -> Dict[str, str]:
        """
        Cria um novo pagamento PIX.
        
        Args:
            valor_centavos: Valor do pagamento em centavos
            chave_pix: Chave PIX do destinatário
            
        Returns:
            Dict: Dados do pagamento incluindo QR Code
            
        Raises:
            PixAPIError: Em caso de erro na criação do pagamento
        """
        logger.info(f"Iniciando criação de pagamento PIX - Valor: {valor_centavos} centavos, Chave: {chave_pix}")
        
        if not self.api_url:
            error_msg = "URL da API PIX não configurada"
            logger.error(error_msg)
            raise PixAPIError(error_msg)
        
        if not isinstance(valor_centavos, int) or valor_centavos <= 0:
            error_msg = f"Valor inválido: {valor_centavos} (deve ser um número inteiro positivo de centavos)"
            logger.error(error_msg)
            raise PixAPIError("Valor deve ser um número inteiro positivo de centavos")
            
        if not chave_pix or not isinstance(chave_pix, str):
            error_msg = f"Chave PIX inválida: {chave_pix}"
            logger.error(error_msg)
            raise PixAPIError("Chave PIX inválida")
        
        try:
            # Prepara os dados para a API
            # A API espera amount_in_cents (em centavos) e address (chave PIX)
            data = {
                'amount_in_cents': valor_centavos,  # Já está em centavos
                'address': chave_pix
            }
            
            logger.info(f"Dados do pagamento: {data}")
            
            # Chama a API
            logger.info("Chamando _make_request...")
            response = self._make_request(data=data)
            logger.info(f"Resposta da API: {response}")
            
            # Verifica se a resposta contém os campos esperados
            # A API pode retornar os dados em response['data'] ou diretamente no response
            response_data = response.get('data', response)
            
            required_fields = ['qr_image_url', 'qr_copy_paste', 'transaction_id']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                error_msg = f"Resposta da API incompleta. Campos faltando: {', '.join(missing_fields)}"
                logger.error(error_msg)
                logger.error(f"Campos recebidos: {list(response_data.keys())}")
                raise PixAPIError("Resposta da API incompleta")
            
            # Formata a resposta no formato esperado pelo código existente
            result = {
                'qr_image_url': str(response_data['qr_image_url']),
                'qr_copy_paste': str(response_data['qr_copy_paste']),
                'transaction_id': str(response_data['transaction_id'])
            }
            
            logger.info("Pagamento PIX criado com sucesso")
            logger.info(f"QR Code URL: {result['qr_image_url']}")
            logger.info(f"Transaction ID: {result['transaction_id']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            raise PixAPIError(f"Falha na comunicação com a API: {str(e)}")
        except PixAPIError:
            raise  # Re-lança exceções já tratadas
        except Exception as e:
            logger.error(f"Erro inesperado ao criar pagamento PIX: {e}")
            raise PixAPIError(f"Erro inesperado: {str(e)}")

# Instância global para ser importada
pix_api = PixAPI()

def formatar_valor_brl(valor_centavos: int) -> str:
    """Formata um valor em centavos para string BRL."""
    valor = Decimal(valor_centavos) / 100
    return f"R$ {valor:,.2f}".replace(".", "v").replace(",", ".").replace("v", ",")

def obter_dados_ted() -> Dict[str, str]:
    """Retorna os dados para transferência TED."""
    return {
        'banco': os.getenv('TED_BANCO', 'Banco do Brasil'),
        'agencia': os.getenv('TED_AGENCIA', '0000-1'),
        'conta': os.getenv('TED_CONTA', '12345-6'),
        'cpf_cnpj': os.getenv('TED_CPF_CNPJ', '000.000.000-00'),
        'favorecido': os.getenv('TED_FAVORECIDO', 'Nome da Empresa LTDA'),
        'tipo_conta': 'Conta Corrente'
    }

def obter_chat_boleto() -> str:
    """Retorna o chat ID ou username para envio de boleto."""
    return os.getenv('BOLETO_CHAT_ID', '@triacorelabs')

# Exemplo de uso
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Exemplo de criação de pagamento
    try:
        # Cria uma instância da API
        api = PixAPI()
        
        # Cria um pagamento de R$ 10,00
        pagamento = api.criar_pagamento(
            valor_centavos=1000,  # R$ 10,00
            chave_pix="chave_pix@exemplo.com"
        )
        
        print(f"Pagamento criado: {pagamento['transaction_id']}")
        print(f"QR Code URL: {pagamento['qr_image_url']}")
        print(f"Código PIX: {pagamento['qr_copy_paste']}")
        
    except PixAPIError as e:
        print(f"Erro na API PIX: {e}")
