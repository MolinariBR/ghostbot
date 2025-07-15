#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Pagamentos Lightning Network

Este módulo fornece funcionalidades para validar e verificar o status de pagamentos
Lightning Network usando a API Voltz.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Union

# Configuração de logging
logger = logging.getLogger(__name__)

class ValidadorVoltz:
    """
    Classe para validação e verificação de pagamentos Lightning Network usando a API Voltz.
    """
    
    def __init__(self, wallet_id: str, admin_key: str, invoice_key: str, node_url: str = "https://lnvoltz.com"):
        """
        Inicializa o validador com as credenciais da API Voltz.
        
        Args:
            wallet_id: ID da carteira Voltz
            admin_key: Chave de administração da API
            invoice_key: Chave para criar/verificar faturas
            node_url: URL do nó Voltz (opcional)
        """
        self.config = {
            'node_url': node_url.rstrip('/'),
            'wallet_id': wallet_id,
            'admin_key': admin_key,
            'invoice_key': invoice_key,
            'api_version': 'v1'
        }
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_connect=10, sock_read=20)
        
        # Mapeamento de status para mensagens amigáveis
        self.status_messages = {
            'unpaid': '⏳ AGUARDANDO PAGAMENTO',
            'paid': '✅ PAGAMENTO CONFIRMADO',
            'expired': '❌ PAGAMENTO EXPIRADO',
            'failed': '❌ FALHA NO PAGAMENTO',
            'in_flight': '✈️ PAGAMENTO EM ANDAMENTO',
            'unknown': '❓ STATUS DESCONHECIDO'
        }
    
    async def __aenter__(self):
        """Inicializa a sessão HTTP quando usado com 'async with'."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fecha a sessão HTTP quando o bloco 'async with' terminar."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _get_headers(self, use_admin: bool = True) -> Dict[str, str]:
        """
        Retorna os cabeçalhos HTTP para autenticação.
        
        Args:
            use_admin: Se True, usa a chave de admin; caso contrário, usa a chave de fatura
            
        Returns:
            Dicionário com os cabeçalhos de autenticação
        """
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Api-Key': self.config['admin_key'] if use_admin else self.config['invoice_key']
        }
    
    async def consultar_saldo(self) -> Dict[str, Any]:
        """
        Consulta o saldo da carteira.
        
        Returns:
            Dicionário com as informações de saldo ou mensagem de erro
        """
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/wallet/{self.config['wallet_id']}"
        
        try:
            async with self.session.get(endpoint, headers=self._get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'success': True,
                        'data': {
                            'balance': data.get('balance', 0),
                            'currency': 'sats'
                        }
                    }
                else:
                    error = await response.text()
                    return {
                        'success': False,
                        'error': f"Erro ao consultar saldo: {response.status} - {error}"
                    }
        except Exception as e:
            return {
                'success': False,
                'error': f"Exceção ao consultar saldo: {str(e)}"
            }
    
    async def criar_fatura(self, valor_sats: int, memo: str = "", expiracao: int = 3600) -> Dict[str, Any]:
        """
        Cria uma nova fatura Lightning.
        
        Args:
            valor_sats: Valor da fatura em satoshis
            memo: Descrição da fatura (opcional)
            expiracao: Tempo de expiração em segundos (padrão: 1 hora)
            
        Returns:
            Dicionário com os dados da fatura ou mensagem de erro
        """
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/wallet/{self.config['wallet_id']}/invoice"
        
        payload = {
            'amount': valor_sats,
            'memo': memo,
            'expiry': expiracao
        }
        
        try:
            async with self.session.post(
                endpoint, 
                headers=self._get_headers(use_admin=False),
                json=payload
            ) as response:
                data = await response.json()
                
                if response.status == 200 and 'payment_request' in data:
                    return {
                        'success': True,
                        'data': {
                            'payment_request': data['payment_request'],
                            'payment_hash': data.get('payment_hash', ''),
                            'expires_at': datetime.utcnow().timestamp() + expiracao
                        }
                    }
                else:
                    error = data.get('message', 'Erro desconhecido')
                    return {
                        'success': False,
                        'error': f"Falha ao criar fatura: {error}"
                    }
        except Exception as e:
            return {
                'success': False,
                'error': f"Exceção ao criar fatura: {str(e)}"
            }
    
    async def verificar_pagamento(self, payment_hash: str) -> Dict[str, Any]:
        """
        Verifica o status de um pagamento usando o hash do pagamento.
        
        Args:
            payment_hash: Hash do pagamento a ser verificado
            
        Returns:
            Dicionário com o status do pagamento e informações adicionais
        """
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/wallet/{self.config['wallet_id']}/invoice/{payment_hash}"
        
        try:
            async with self.session.get(
                endpoint, 
                headers=self._get_headers(use_admin=False)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Normaliza o status
                    status = data.get('status', 'unknown').lower()
                    
                    # Determina se o pagamento foi confirmado
                    pago = status in ['paid', 'complete']
                    
                    # Obtém mensagem de status amigável
                    mensagem = self.status_messages.get(status, self.status_messages['unknown'])
                    
                    return {
                        'success': True,
                        'data': {
                            'status': status,
                            'pago': pago,
                            'message': mensagem,
                            'payment_hash': data.get('payment_hash', ''),
                            'amount': data.get('amount', 0),
                            'amount_received': data.get('amount_received', 0),
                            'created_at': data.get('created_at'),
                            'paid_at': data.get('paid_at'),
                            'expires_at': data.get('expires_at')
                        }
                    }
                else:
                    error = await response.text()
                    return {
                        'success': False,
                        'error': f"Erro ao verificar pagamento: {response.status} - {error}"
                    }
        except Exception as e:
            return {
                'success': False,
                'error': f"Exceção ao verificar pagamento: {str(e)}"
            }
    
    async def enviar_pagamento(self, payment_request: str) -> Dict[str, Any]:
        """
        Envia um pagamento usando uma fatura Lightning.
        
        Args:
            payment_request: Fatura Lightning (invoice) para pagamento
            
        Returns:
            Dicionário com o resultado do pagamento ou mensagem de erro
        """
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/wallet/{self.config['wallet_id']}/payments"
        
        payload = {
            'payment_request': payment_request
        }
        
        try:
            async with self.session.post(
                endpoint, 
                headers=self._get_headers(),
                json=payload
            ) as response:
                data = await response.json()
                
                if response.status == 200 and 'payment_hash' in data:
                    return {
                        'success': True,
                        'data': {
                            'payment_hash': data['payment_hash'],
                            'amount': data.get('amount', 0),
                            'fee': data.get('fee', 0),
                            'status': 'pending'
                        }
                    }
                else:
                    error = data.get('message', 'Erro desconhecido')
                    return {
                        'success': False,
                        'error': f"Falha ao enviar pagamento: {error}"
                    }
        except Exception as e:
            return {
                'success': False,
                'error': f"Exceção ao enviar pagamento: {str(e)}"
            }


# Funções de conveniência para uso direto
_instancia_global = None

def configurar(wallet_id: str, admin_key: str, invoice_key: str, node_url: str = "https://lnvoltz.com"):
    """
    Configura a instância global do ValidadorVoltz.
    
    Args:
        wallet_id: ID da carteira Voltz
        admin_key: Chave de administração da API
        invoice_key: Chave para criar/verificar faturas
        node_url: URL do nó Voltz (opcional)
    """
    global _instancia_global
    _instancia_global = ValidadorVoltz(wallet_id, admin_key, invoice_key, node_url)

# Funções de conveniência
async def consultar_saldo() -> Dict[str, Any]:
    """
    Consulta o saldo da carteira usando a instância global.
    
    Returns:
        Dicionário com as informações de saldo ou mensagem de erro
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    
    async with _instancia_global as validador:
        return await validador.consultar_saldo()

async def criar_fatura(valor_sats: int, memo: str = "", expiracao: int = 3600) -> Dict[str, Any]:
    """
    Cria uma nova fatura Lightning usando a instância global.
    
    Args:
        valor_sats: Valor da fatura em satoshis
        memo: Descrição da fatura (opcional)
        expiracao: Tempo de expiração em segundos (padrão: 1 hora)
        
    Returns:
        Dicionário com os dados da fatura ou mensagem de erro
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    
    async with _instancia_global as validador:
        return await validador.criar_fatura(valor_sats, memo, expiracao)

async def verificar_pagamento(payment_hash: str) -> Dict[str, Any]:
    """
    Verifica o status de um pagamento usando o hash do pagamento.
    
    Args:
        payment_hash: Hash do pagamento a ser verificado
        
    Returns:
        Dicionário com o status do pagamento e informações adicionais
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    
    async with _instancia_global as validador:
        return await validador.verificar_pagamento(payment_hash)

async def enviar_pagamento(payment_request: str) -> Dict[str, Any]:
    """
    Envia um pagamento usando uma fatura Lightning.
    
    Args:
        payment_request: Fatura Lightning (invoice) para pagamento
        
    Returns:
        Dicionário com o resultado do pagamento ou mensagem de erro
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    
    async with _instancia_global as validador:
        return await validador.enviar_pagamento(payment_request)

# Exemplo de uso assíncrono
async def exemplo_uso():
    # Configura o validador com as credenciais da API Voltz
    configurar(
        wallet_id="f3c366b7fb6f43fa9467c4dccedaf824",
        admin_key="8fce34f4b0f8446a990418bd167dc644",
        invoice_key="b2f68df91c8848f6a1db26f2e403321f",
        node_url="https://lnvoltz.com"
    )
    
    # Exemplo: Consultar saldo
    print("Consultando saldo...")
    saldo = await consultar_saldo()
    print(f"Saldo: {saldo}")
    
    # Exemplo: Criar fatura
    print("\nCriando fatura...")
    fatura = await criar_fatura(1000, "Teste de integração")
    print(f"Fatura criada: {fatura}")
    
    if fatura.get('success'):
        # Exemplo: Verificar pagamento
        print("\nVerificando pagamento...")
        pagamento = await verificar_pagamento(fatura['data']['payment_hash'])
        print(f"Status do pagamento: {pagamento}")

# Para testar o módulo diretamente
if __name__ == "__main__":
    import os
    
    # Carrega as credenciais
    wallet_id = "f3c366b7fb6f43fa9467c4dccedaf824"
    admin_key = "8fce34f4b0f8446a990418bd167dc644"
    invoice_key = "b2f68df91c8848f6a1db26f2e403321f"
    node_url = "https://lnvoltz.com"
    
    # Configura o validador com as credenciais
    configurar(wallet_id, admin_key, invoice_key, node_url)
    
    # Executa o exemplo
    asyncio.run(exemplo_uso())