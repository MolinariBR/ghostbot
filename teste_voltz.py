#!/usr/bin/env python3
"""
Teste de Integração com a API Voltz

Este script testa as principais funcionalidades da API Voltz, incluindo:
- Consulta de saldo
- Criação de invoices
- Envio de pagamentos
- Consulta de status de pagamento
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime

class TesteVoltzAPI:
    """Classe para testar a integração com a API Voltz"""
    
    def __init__(self):
        # Configurações da API Voltz (substitua pelas suas credenciais)
        self.config = {
            'node_url': 'https://lnvoltz.com',
            'wallet_id': 'f3c366b7fb6f43fa9467c4dccedaf824',
            'admin_key': '8fce34f4b0f8446a990418bd167dc644',
            'invoice_key': 'b2f68df91c8848f6a1db26f2e403321f',
            'api_version': 'v1'
        }
        self.session = None
        self.base_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_auth_headers(self, use_admin: bool = True):
        """Retorna os headers de autenticação"""
        headers = self.base_headers.copy()
        headers['X-Api-Key'] = self.config['admin_key'] if use_admin else self.config['invoice_key']
        return headers
    
    async def get_balance(self) -> Dict[str, Any]:
        """Obtém o saldo da carteira Voltz"""
        url = f"{self.config['node_url']}/api/{self.config['api_version']}/wallet"
        
        try:
            async with self.session.get(
                url, 
                headers=self._get_auth_headers()
            ) as response:
                data = await response.json()
                
                if response.status == 200:
                    return {
                        'success': True,
                        'balance': data.get('balance', 0),
                        'currency': 'sats',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Erro ao consultar saldo'),
                        'status_code': response.status
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }
    
    async def create_invoice(
        self, 
        amount_sats: int, 
        memo: str = "Teste de integração",
        expiry: int = 3600
    ) -> Dict[str, Any]:
        """Cria uma nova fatura na rede Lightning"""
        # Usando o endpoint correto para criar invoices na API Voltz
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/payments"
        
        # Usando o formato correto para a API Voltz
        payload = {
            'amount': amount_sats,
            'description': memo,  # Usando 'description' que é o parâmetro esperado
            'expires_in': 3600,  # Em segundos (1 hora)
            'private': False,  # Fatura pública
            'memo': memo  # Adicionando memo também por garantia
        }
        
        print(f"\n🔍 Detalhes da requisição:")
        print(f"URL: {endpoint}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            # Usando a chave de admin para criar a fatura
            headers = self._get_auth_headers(use_admin=True)
            # Adicionando o wallet_id no header
            headers['X-Wallet-Id'] = self.config['wallet_id']
            print(f"Headers: {json.dumps(headers, indent=2)}")
            
            async with self.session.post(
                endpoint,
                headers=headers,
                json=payload,
                ssl=False  # Desativa verificação SSL para evitar problemas de certificado
            ) as response:
                response_text = await response.text()
                print(f"\n📥 Resposta da API (Status: {response.status}):")
                print(f"Headers: {dict(response.headers)}")
                print(f"Conteúdo: {response_text}")
                
                try:
                    data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': f'Resposta inválida da API: {response_text}',
                        'status_code': response.status
                    }
                
                if response.status == 201:
                    return {
                        'success': True,
                        'payment_request': data.get('payment_request'),
                        'payment_hash': data.get('payment_hash'),
                        'expires_at': data.get('expires_at')
                    }
                else:
                    error_msg = data.get('message', 'Erro ao criar fatura')
                    if not error_msg and 'error' in data:
                        error_msg = data['error']
                    elif not error_msg and 'errors' in data:
                        error_msg = str(data['errors'])
                    
                    return {
                        'success': False,
                        'error': error_msg,
                        'status_code': response.status,
                        'response_data': data
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }
    
    async def pay_invoice(self, payment_request: str) -> Dict[str, Any]:
        """Envia um pagamento via Lightning Network"""
        url = f"{self.config['node_url']}/api/{self.config['api_version']}/payments"
        
        payload = {
            'payment_request': payment_request
        }
        
        try:
            async with self.session.post(
                url,
                headers=self._get_auth_headers(),
                json=payload
            ) as response:
                data = await response.json()
                
                if response.status in (200, 201):
                    return {
                        'success': True,
                        'payment_hash': data.get('payment_hash'),
                        'fee_sats': data.get('fee_sats', 0),
                        'status': data.get('status', 'pending')
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Erro ao enviar pagamento'),
                        'status_code': response.status
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }
    
    async def check_payment_status(self, payment_hash: str) -> Dict[str, Any]:
        """Verifica o status de um pagamento"""
        url = f"{self.config['node_url']}/api/{self.config['api_version']}/payments/{payment_hash}"
        
        try:
            async with self.session.get(
                url,
                headers=self._get_auth_headers()
            ) as response:
                data = await response.json()
                
                if response.status == 200:
                    return {
                        'success': True,
                        'status': data.get('status'),
                        'amount_sent': data.get('amount_sent'),
                        'fee_sats': data.get('fee_sats', 0),
                        'created_at': data.get('created_at'),
                        'completed_at': data.get('completed_at')
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Erro ao verificar pagamento'),
                        'status_code': response.status
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }

    def _is_lightning_address(self, address: str) -> bool:
        """Check if the address is a valid Lightning address (email format)"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', address))

    async def _get_lnurl_invoice(self, address: str, amount: int, memo: str = '') -> str:
        """
        Obtém uma fatura BOLT11 a partir de um endereço Lightning usando o protocolo LNURL
        Especializado para bouncyflight79@walletofsatoshi.com
        """
        import aiohttp
        import json
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        print(f"\n🔍 Processando endereço Lightning: {address}")
        
        # Verifica se é o endereço específico que queremos
        if address.lower() != 'bouncyflight79@walletofsatoshi.com':
            raise ValueError("Este método suporta apenas o endereço bouncyflight79@walletofsatoshi.com")
        
        # Configurações específicas para walletofsatoshi.com
        username, domain = 'bouncyflight79', 'walletofsatoshi.com'
        print(f"  - Usuário: {username}")
        print(f"  - Domínio: {domain}")
        
        # URL direta para o LNURL do Wallet of Satoshi
        lnurl_endpoint = f"https://{domain}/.well-known/lnurlp/{username}"
        print(f"\n🔗 Acessando: {lnurl_endpoint}")
        
        # Configurações da requisição
        timeout = aiohttp.ClientTimeout(total=15)
        
        try:
            # Primeiro, obtemos os metadados do LNURL
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Cabeçalhos para parecer um navegador
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': f'https://{domain}/',
                    'Origin': f'https://{domain}'
                }
                
                print(f"  - Fazendo requisição para LNURL...")
                
                # Primeira requisição: obter metadados do LNURL
                try:
                    async with session.get(lnurl_endpoint, headers=headers, ssl=True) as response:
                        print(f"  - Status da resposta: {response.status}")
                        
                        if response.status != 200:
                            error_text = await response.text()
                            print(f"  - Erro na resposta: {response.status} {response.reason}")
                            print(f"  - Conteúdo: {error_text}")
                            raise Exception(f"Falha ao acessar o endpoint LNURL: {response.status} {response.reason}")
                        
                        try:
                            data = await response.json()
                            print(f"  - Resposta JSON recebida")
                            print(json.dumps(data, indent=2, ensure_ascii=False))
                        except Exception as e:
                            error_text = await response.text()
                            print(f"  - Erro ao decodificar JSON: {e}")
                            print(f"  - Conteúdo da resposta: {error_text}")
                            raise Exception("Resposta inválida do servidor LNURL")
                        
                        if data.get('status') == 'ERROR':
                            error_msg = data.get('reason', 'Erro desconhecido')
                            print(f"  - Erro na resposta LNURL: {error_msg}")
                            raise Exception(f"Erro no LNURL: {error_msg}")
                        
                        callback_url = data.get('callback')
                        if not callback_url:
                            print("  - ERRO: Nenhuma URL de callback na resposta")
                            raise Exception("URL de callback não encontrada na resposta do LNURL")
                        
                        # Parse the callback URL
                        parsed = urlparse(callback_url)
                        
                        # Convert amount to millisatoshis (1 sat = 1000 msats)
                        amount_msats = amount * 1000
                        
                        # Build the query parameters
                        query_params = {
                            'amount': str(amount_msats)
                        }
                        
                        # Add memo if provided and if the LNURL supports comments
                        if memo and data.get('comment_allowed', 0) > 0:
                            query_params['comment'] = memo
                        
                        # Rebuild the URL with new query parameters
                        new_query = urlencode(query_params)
                        callback_with_params = f"{callback_url}{'&' if '?' in callback_url else '?'}{new_query}"
                        
                        print(f"  - URL de callback com parâmetros: {callback_with_params}")
                        
                        # Segunda requisição: obter a fatura BOLT11
                        print(f"  - Solicitando fatura BOLT11...")
                        async with session.get(callback_with_params, headers=headers, ssl=True) as invoice_response:
                            if invoice_response.status != 200:
                                error_text = await invoice_response.text()
                                print(f"  - Erro ao obter fatura: {invoice_response.status} {invoice_response.reason}")
                                print(f"  - Conteúdo: {error_text}")
                                raise Exception(f"Falha ao obter fatura: {invoice_response.status} {invoice_response.reason}")
                            
                            try:
                                invoice_data = await invoice_response.json()
                                print("  - Resposta da fatura recebida:")
                                print(json.dumps(invoice_data, indent=2, ensure_ascii=False))
                                
                                if invoice_data.get('status') == 'ERROR':
                                    error_msg = invoice_data.get('reason', 'Erro desconhecido')
                                    print(f"  - Erro na resposta da fatura: {error_msg}")
                                    raise Exception(f"Erro ao gerar fatura: {error_msg}")
                                
                                bolt11 = invoice_data.get('pr')
                                if not bolt11:
                                    print("  - ERRO: Nenhuma fatura BOLT11 na resposta")
                                    raise Exception("Nenhuma fatura BOLT11 encontrada na resposta")
                                
                                print(f"✅ Fatura BOLT11 obtida com sucesso!")
                                print(f"   - Fatura: {bolt11[:50]}...{bolt11[-10:]}")
                                
                                return bolt11
                                
                            except Exception as e:
                                error_text = await invoice_response.text()
                                print(f"  - Erro ao processar resposta da fatura: {e}")
                                print(f"  - Conteúdo: {error_text}")
                                raise Exception(f"Erro ao processar resposta da fatura: {str(e)}")
                
                except aiohttp.ClientError as e:
                    print(f"  - Erro de conexão: {str(e)}")
                    raise Exception(f"Erro de conexão: {str(e)}")
                
                except Exception as e:
                    print(f"  - Erro inesperado: {str(e)}")
                    raise Exception(f"Erro ao processar requisição LNURL: {str(e)}")
        
        except Exception as e:
            print(f"❌ Erro ao obter fatura LNURL: {str(e)}")
            raise

    async def pay_lightning_address(self, address: str, amount_sats: int, memo: str = "Pagamento via API") -> Dict[str, Any]:
        """
        Envia um pagamento para um endereço Lightning ou BOLT11
        
        Args:
            address: Endereço Lightning (email) ou BOLT11
            amount_sats: Quantidade em satoshis
            memo: Mensagem opcional
            
        Returns:
            Dict com o resultado da operação
        """
        import aiohttp
        
        # Verifica se é um endereço Lightning (email)
        if self._is_lightning_address(address):
            print(f"🔍 Endereço Lightning detectado: {address}")
            print("🔗 Obtendo fatura BOLT11 via LNURL...")
            
            try:
                # Obtém uma fatura BOLT11 para este endereço Lightning
                invoice = await self._get_lnurl_invoice(address, amount_sats, memo)
                print(f"✅ Fatura BOLT11 obtida: {invoice[:50]}...")
                
                # Agora paga a fatura
                return await self.pay_invoice(invoice)
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Erro ao obter fatura LNURL: {str(e)}',
                    'status_code': 500
                }
        
        # Se não for um endereço Lightning, assume que é uma fatura BOLT11
        print(f"🔍 Fatura BOLT11 detectada: {address[:50]}...")
        return await self.pay_invoice(address)
        
    async def pay_invoice(self, payment_request: str) -> Dict[str, Any]:
        """
        Paga uma fatura BOLT11
        
        Args:
            payment_request: Fatura BOLT11 a ser paga
            
        Returns:
            Dict com o resultado da operação
        """
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/payments"
        
        payload = {
            'out': True,
            'bolt11': payment_request,
            'unit': 'sat'
        }
        
        print(f"\n🔍 Enviando pagamento para fatura BOLT11...")
        print(f"Fatura: {payment_request[:50]}...")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            # Ensure we have a session
            if not hasattr(self, 'session') or self.session is None or self.session.closed:
                self.session = aiohttp.ClientSession()
            
            # Get auth headers
            headers = self._get_auth_headers(use_admin=True)
            headers['X-Wallet-Id'] = self.config['wallet_id']
            
            # Make the request
            async with self.session.post(
                endpoint,
                headers=headers,
                json=payload,
                ssl=False
            ) as response:
                response_text = await response.text()
                print(f"\n📥 Resposta da API (Status: {response.status}):")
                print(f"Conteúdo: {response_text}")
                
                try:
                    data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': f'Resposta inválida da API: {response_text}',
                        'status_code': response.status,
                        'raw_response': response_text
                    }
                
                if response.status in (200, 201):
                    return {
                        'success': True,
                        'payment_hash': data.get('payment_hash'),
                        'fee_sats': data.get('fee_sats', 0),
                        'status': data.get('status', 'pending'),
                        'data': data
                    }
                else:
                    error_msg = data.get('message') or data.get('error') or 'Erro ao enviar pagamento'
                    return {
                        'success': False,
                        'error': error_msg,
                        'status_code': response.status,
                        'response_data': data
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }

async def main():
    """Função principal para executar os testes"""
    print("🔌 Teste de Envio para Lightning Address")
    
    async with TesteVoltzAPI() as api:
        try:
            # 1. Testar conexão e obter saldo
            print("\n1. Obtendo saldo da carteira...")
            balance = await api.get_balance()
            print(f"✅ Saldo: {balance.get('balance', 0)} sats")
            
            # 2. Enviar pagamento para Lightning Address
            print("\n2. Enviando pagamento para Lightning Address...")
            
            # Endereço Lightning para teste
            lightning_address = "bouncyflight79@walletofsatoshi.com"
            amount_sats = 10  # Valor em satoshis
            
            print(f"\n💡 Enviando {amount_sats} sats para {lightning_address}...")
            
            result = await api.pay_lightning_address(
                address=lightning_address,
                amount_sats=amount_sats,
                memo="Teste de pagamento via API"
            )
            
            if result.get('success'):
                print(f"\n✅ Pagamento enviado com sucesso!")
                print(f"   Hash: {result.get('payment_hash')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Taxa: {result.get('fee_sats', 0)} sats")
                
                # 3. Verificar status do pagamento
                print("\n3. Verificando status do pagamento...")
                payment_hash = result.get('payment_hash')
                if payment_hash:
                    # Aguardar alguns segundos para o pagamento ser processado
                    import asyncio
                    print("   Aguardando confirmação do pagamento...")
                    await asyncio.sleep(5)  # Espera 5 segundos
                    
                    payment_status = await api.check_payment_status(payment_hash)
                    print(f"   Status do pagamento: {payment_status.get('status')}")
                    
                    # Se ainda estiver pendente, tenta mais algumas vezes
                    max_retries = 3
                    retry_count = 0
                    
                    while payment_status.get('status') == 'pending' and retry_count < max_retries:
                        retry_count += 1
                        print(f"   Aguardando confirmação... Tentativa {retry_count}/{max_retries}")
                        await asyncio.sleep(5)  # Espera mais 5 segundos
                        payment_status = await api.check_payment_status(payment_hash)
                        print(f"   Status atual: {payment_status.get('status')}")
                    
                    print("\n🔍 Detalhes finais do pagamento:")
                    print(json.dumps(payment_status, indent=2, ensure_ascii=False))
            else:
                print(f"\n❌ Erro ao enviar pagamento: {result.get('error')}")
                if 'response_data' in result:
                    print("\n📄 Resposta detalhada da API:")
                    print(json.dumps(result['response_data'], indent=2, ensure_ascii=False))
                
        except Exception as e:
            print(f"\n❌ Erro durante a execução: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Garante que a sessão seja fechada corretamente
            if hasattr(api, 'session') and api.session and not api.session.closed:
                await api.session.close()

if __name__ == "__main__":
    asyncio.run(main())
