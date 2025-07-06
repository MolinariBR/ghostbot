"""
Módulo para integração com a API de pagamentos PIX do servidor VPS.
"""
import json
import requests
import logging
from typing import Dict, Optional, Any
from decimal import Decimal

# Importa as configurações do tokens.py
from tokens import Config

# Configuração de logging
logger = logging.getLogger(__name__)


class PixAPIError(Exception):
    """Exceção para erros na API de pagamentos PIX."""
    pass


class PixAPI:
    """Cliente para a API de pagamentos PIX do servidor VPS."""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Inicializa o cliente da API de depósito.
        
        Args:
            api_url: URL base da API (opcional, usa PIX_API_URL do tokens.py por padrão)
        """
        # Endpoint da API de depósito
        self.api_url = (api_url or getattr(Config, 'PIX_API_URL', 'https://useghost.squareweb.app/api/bot_deposit.php')).rstrip('/')
        
        if not self.api_url:
            raise PixAPIError("URL da API de depósito não configurada. Defina PIX_API_URL no tokens.py")
    
    def _make_request(self, method: str, path: str = '', data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Faz uma requisição para a API PIX.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            path: Caminho do endpoint (opcional)
            data: Dados a serem enviados no corpo da requisição
            
        Returns:
            Resposta da API como dicionário
            
        Raises:
            PixAPIError: Em caso de erro na requisição
        """
        if data is None:
            data = {}
            
        url = f"{self.api_url}/{path.lstrip('/')}" if path else self.api_url
        logger.info(f"Fazendo requisição {method} para: {url}")
        logger.info(f"Dados da requisição: {data}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'GhostBot/1.0'
        }
        
        try:
            logger.info(f"Enviando requisição {method} para {url}")
            
            # Adiciona timestamp à requisição
            import time
            data['timestamp'] = int(time.time())
            
            # Log dos dados que serão enviados
            logger.info(f"Dados completos a serem enviados: {json.dumps(data, indent=2)}")
            
            # Envia a requisição com o método especificado
            if method.upper() == 'GET':
                response = requests.get(
                    url=url,
                    params=data,  # Para GET, os parâmetros vão na URL
                    headers=headers,
                    timeout=30
                )
            else:
                # Para outros métodos (POST, PUT, etc.), envia os dados no corpo
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,  # Usa json= para enviar como application/json
                    headers=headers,
                    timeout=30
                )
            
            logger.info(f"Resposta recebida - Status: {response.status_code}")
            logger.info(f"Cabeçalhos da resposta: {response.headers}")
            logger.info(f"Conteúdo da resposta: {response.text}")
            
            response.raise_for_status()  # Levanta exceção para códigos de erro HTTP
            
            # Verifica se a resposta é um JSON válido
            try:
                response_data = response.json()
                logger.info(f"Resposta JSON decodificada: {json.dumps(response_data, indent=2)}")
            except ValueError as e:
                error_msg = f"Resposta inválida do servidor: {response.text}"
                logger.error(error_msg)
                raise PixAPIError(error_msg) from e
            
            # Verifica se há erros na resposta
            if not response_data.get('success', False):
                error_msg = response_data.get('error', 'Erro desconhecido na API')
                logger.error(f"Erro na API: {error_msg}")
                raise PixAPIError(f"Erro na API: {error_msg}")
            
            # Retorna a resposta completa, incluindo o campo 'data' se existir
            return response_data
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Erro HTTP {e.response.status_code} na requisição para {url}: {str(e)}"
            if e.response.content:
                try:
                    error_data = e.response.json()
                    error_msg += f" - {json.dumps(error_data, indent=2)}"
                except:
                    error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise PixAPIError(error_msg) from e
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição para {url}: {str(e)}"
            logger.error(error_msg)
            raise PixAPIError(error_msg) from e
    
    def criar_pagamento(self, valor_centavos: int, endereco: str = None) -> Dict[str, str]:
        """
        Cria um novo pagamento PIX.
        
        Args:
            valor_centavos: Valor do pagamento em centavos
            endereco: Endereço de destino do PIX (obrigatório)
            
        Returns:
            Dicionário com os dados do pagamento incluindo QR Code e transaction_id
            
        Raises:
            PixAPIError: Em caso de erro na criação do pagamento
        """
        logger.info(f"Iniciando criação de pagamento PIX - Valor: {valor_centavos} centavos, Endereço: {endereco}")
        
        if not self.api_url:
            error_msg = "URL da API PIX não configurada"
            logger.error(error_msg)
            raise PixAPIError(error_msg)
        
        if not isinstance(valor_centavos, int) or valor_centavos <= 0:
            error_msg = f"Valor inválido: {valor_centavos} (deve ser um número inteiro positivo de centavos)"
            logger.error(error_msg)
            raise PixAPIError("Valor deve ser um número inteiro positivo de centavos")
        
        if not endereco:
            error_msg = "Endereço de destino não fornecido"
            logger.error(error_msg)
            raise PixAPIError("Endereço de destino é obrigatório")
        
        try:
            # Prepara os dados para a API
            # O endpoint espera os seguintes campos:
            # - amount_in_cents: valor em centavos (obrigatório)
            # - address: endereço de destino da criptomoeda (obrigatório)
            # - type: tipo de depósito (opcional, padrão 'pix')
            data = {
                'amount_in_cents': valor_centavos,  # Valor em centavos (obrigatório)
                'address': endereco,               # Endereço de destino da criptomoeda (obrigatório)
                'type': 'pix'                      # Tipo de depósito
            }
            
            logger.info(f"Dados do pagamento: {data}")
            
            # Chama a API
            logger.info(f"Chamando API de depósito em: {self.api_url}")
            
            # Faz a requisição para o endpoint do backend
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            logger.info(f"Headers da requisição: {headers}")
            
            # Envia a requisição para o endpoint de depósito
            response = requests.post(
                self.api_url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Resposta da API - Status: {response.status_code}")
            logger.info(f"Conteúdo da resposta: {response.text}")
            
            # Verifica se houve erro na requisição
            response.raise_for_status()
            
            # Tenta decodificar a resposta JSON
            try:
                response_data = response.json()
                logger.info(f"Resposta JSON decodificada: {response_data}")
            except ValueError as e:
                error_msg = f"Erro ao decodificar resposta JSON: {e}"
                logger.error(error_msg)
                raise PixAPIError("Resposta inválida da API")
            
            # Verifica se a resposta contém o campo 'success'
            if 'success' not in response_data:
                error_msg = "Resposta da API inválida: campo 'success' não encontrado"
                logger.error(error_msg)
                raise PixAPIError("Resposta da API inválida")
            
            # Verifica se a requisição foi bem-sucedida
            if not response_data['success']:
                error_msg = response_data.get('error', 'Erro desconhecido na API')
                logger.error(f"Erro na API: {error_msg}")
                
                # Tenta obter mais detalhes do erro, se disponíveis
                if 'message' in response_data and response_data['message'] != error_msg:
                    error_msg += f" - {response_data['message']}"
                
                raise PixAPIError(f"Erro na API: {error_msg}")
            
            # Extrai os dados da resposta
            payment_data = response_data.get('data', {})
            if not payment_data:
                error_msg = "Resposta da API sem dados de pagamento"
                logger.error(error_msg)
                raise PixAPIError(error_msg)
            
            # Verifica e mapeia os campos da resposta
            # A API pode retornar qr_copy_paste ou qr_code_text
            if 'qr_copy_paste' in payment_data and 'qr_code_text' not in payment_data:
                payment_data['qr_code_text'] = payment_data['qr_copy_paste']
            
            # Verifica os campos obrigatórios na resposta
            required_fields = ['qr_image_url', 'qr_code_text', 'transaction_id']
            missing_fields = [field for field in required_fields if field not in payment_data]
            
            if missing_fields:
                error_msg = f"Resposta da API incompleta. Campos faltando: {', '.join(missing_fields)}"
                logger.error(error_msg)
                logger.error(f"Campos recebidos: {list(payment_data.keys())}")
                logger.error(f"Conteúdo completo da resposta: {response_data}")
                raise PixAPIError("Resposta da API incompleta")
            
            # Prepara o resultado
            result = {
                'qr_image_url': payment_data['qr_image_url'],
                'qr_code_text': payment_data['qr_code_text'],
                'transaction_id': payment_data['transaction_id']
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
    """
    Formata um valor em centavos para string BRL.
    
    Args:
        valor_centavos: Valor em centavos a ser formatado
        
    Returns:
        String formatada no padrão monetário brasileiro (R$ 1.234,56)
    """
    valor = Decimal(valor_centavos) / 100
    return f"R$ {valor:,.2f}".replace(".", "X").replace(",", ".").replace("X", ",")

def obter_dados_ted() -> Dict[str, str]:
    """
    Retorna os dados para transferência TED a partir das configurações.
    
    Returns:
        Dicionário com as informações bancárias para TED
    """
    return {
        'banco': getattr(Config, 'TED_BANCO', 'Banco do Brasil'),
        'agencia': getattr(Config, 'TED_AGENCIA', '0000-1'),
        'conta': getattr(Config, 'TED_CONTA', '12345-6'),
        'cpf_cnpj': getattr(Config, 'TED_CPF_CNPJ', '000.000.000-00'),
        'favorecido': getattr(Config, 'TED_FAVORECIDO', 'Nome da Empresa LTDA'),
        'tipo_conta': 'Conta Corrente'
    }

def obter_chat_boleto() -> str:
    """
    Retorna o chat ID ou username para envio de boleto.
    
    Returns:
        String com o chat ID ou username configurado
    """
    return getattr(Config, 'BOLETO_CHAT_ID', '@triacorelabs')

# Exemplo de uso
if __name__ == "__main__":
    import sys
    
    # Configura o logging para exibir mensagens no console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    print("=== Teste de Integração com API PIX ===\n")
    
    try:
        # Cria uma instância da API
        print("Inicializando cliente da API PIX...")
        api = PixAPI()
        print(f"API inicializada com URL: {api.api_url}\n")
        
        # Testa a obtenção de dados para TED
        print("Obtendo dados para transferência TED...")
        dados_ted = obter_dados_ted()
        print(f"Dados para TED: {json.dumps(dados_ted, indent=2, ensure_ascii=False)}\n")
        
        # Testa a formatação de valor
        valor_centavos = 123456  # R$ 1.234,56
        valor_formatado = formatar_valor_brl(valor_centavos)
        print(f"Valor formatado: {valor_centavos} centavos = {valor_formatado}\n")
        
        # Testa a obtenção do chat para boleto
        chat_boleto = obter_chat_boleto()
        print(f"Chat para envio de boleto: {chat_boleto}\n")
        
        print("Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"\n⚠️ Erro durante o teste: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
