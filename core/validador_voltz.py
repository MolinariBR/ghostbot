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
from config.config import WALLET_ID, ADMIN_KEY, INVOICE_KEY, NODE_URL

# Configuração de logging
logger = logging.getLogger(__name__)

class ValidadorVoltz:
    """
    Classe para validação e verificação de pagamentos Lightning Network usando a API Voltz.
    """
    
    def __init__(self, wallet_id: str, admin_key: str, invoice_key: str, node_url: str = "https://lnvoltz.com"):
        """
        Inicializa o validador com as credenciais da API Voltz.
        """
        self.config = {
            'node_url': node_url.rstrip('/'),
            'wallet_id': wallet_id,
            'admin_key': admin_key,
            'invoice_key': invoice_key,
            'api_version': 'v1'
        }
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=90, connect=90, sock_connect=90, sock_read=90)
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
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fecha a sessão HTTP quando o bloco 'async with' terminar."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _ensure_session(self):
        """Garante que a sessão HTTP está criada."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

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

    # --- Consulta de Saldo ---
    async def consultar_saldo(self) -> Dict[str, Any]:
        """
        Consulta o saldo da carteira Voltz.
        Usa a invoice_key para autenticação, conforme documentação oficial.
        Returns:
            Dicionário com saldo em sats ou mensagem de erro.
        """
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/wallet"
        try:
            await self._ensure_session()
            assert self.session is not None
            async with self.session.get(endpoint, headers=self._get_headers(use_admin=False)) as response:
                if response.status == 200:
                    data = await response.json()
                    saldo_voltz = data.get('balance', 0)
                    # Heurística: se for muito grande, está em msats
                    if saldo_voltz > 100_000:
                        saldo_sats = saldo_voltz // 1000
                        logger.info(f"[LIGHTNING] Saldo bruto retornado pela Voltz (msats): {saldo_voltz}")
                        logger.info(f"[LIGHTNING] Saldo convertido para sats: {saldo_sats}")
                    else:
                        saldo_sats = saldo_voltz
                        logger.info(f"[LIGHTNING] Saldo retornado pela Voltz (sats): {saldo_sats}")
                    return {
                        'success': True,
                        'data': {
                            'balance': saldo_sats,
                            'currency': 'sats'
                        }
                    }
                else:
                    error = await response.text()
                    logger.error(f"Erro ao consultar saldo: {response.status} - {error}")
                    return {
                        'success': False,
                        'error': f"Erro ao consultar saldo: {response.status} - {error}"
                    }
        except Exception as e:
            logger.exception("Exceção ao consultar saldo")
            return {
                'success': False,
                'error': f"Exceção ao consultar saldo: {str(e)}"
            }

    # --- Criação de Fatura Lightning ---
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
            await self._ensure_session()
            assert self.session is not None
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
                    logger.error(f"Falha ao criar fatura: {error}")
                    return {
                        'success': False,
                        'error': f"Falha ao criar fatura: {error}"
                    }
        except Exception as e:
            logger.exception("Exceção ao criar fatura")
            return {
                'success': False,
                'error': f"Exceção ao criar fatura: {str(e)}"
            }

    # --- Verificação de Pagamento Recebido ---
    async def verificar_pagamento(self, payment_hash: str) -> Dict[str, Any]:
        """
        Verifica o status de um pagamento recebido usando o hash do pagamento.
        Args:
            payment_hash: Hash do pagamento a ser verificado
        Returns:
            Dicionário com o status do pagamento e informações adicionais
        """
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/wallet/{self.config['wallet_id']}/invoice/{payment_hash}"
        try:
            await self._ensure_session()
            assert self.session is not None
            async with self.session.get(
                endpoint, 
                headers=self._get_headers(use_admin=False)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status', 'unknown').lower()
                    pago = status in ['paid', 'complete']
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
                    logger.error(f"Erro ao verificar pagamento: {response.status} - {error}")
                    return {
                        'success': False,
                        'error': f"Erro ao verificar pagamento: {response.status} - {error}"
                    }
        except Exception as e:
            logger.exception("Exceção ao verificar pagamento")
            return {
                'success': False,
                'error': f"Exceção ao verificar pagamento: {str(e)}"
            }

    # --- Envio de Pagamento Lightning ---
    async def enviar_pagamento(self, lightning_address: str, valor_sats: int) -> Dict[str, Any]:
        """
        Envia um pagamento Lightning para um Lightning Address (nome@dominio.com).
        1. Resolve o Lightning Address para LNURL-pay.
        2. Solicita uma invoice BOLT11 para o valor desejado.
        3. Paga a invoice usando a API Voltz.
        Args:
            lightning_address: Endereço Lightning (ex: nome@dominio.com)
            valor_sats: Valor em satoshis a ser enviado
        Returns:
            Dicionário com o resultado do pagamento ou mensagem de erro
        """
        try:
            # 1. Descobrir endpoint LNURL-pay
            if '@' not in lightning_address:
                return {'success': False, 'error': 'Endereço Lightning inválido.'}
            name, domain = lightning_address.split('@', 1)
            lnurlp_url = f'https://{domain}/.well-known/lnurlp/{name}'
            await self._ensure_session()
            assert self.session is not None
            async with self.session.get(lnurlp_url) as lnurlp_resp:
                if lnurlp_resp.status != 200:
                    erro = await lnurlp_resp.text()
                    return {'success': False, 'error': f'Erro ao resolver Lightning Address: {erro}'}
                lnurlp_data = await lnurlp_resp.json()
                callback = lnurlp_data.get('callback')
                if not callback:
                    return {'success': False, 'error': 'Lightning Address não suporta LNURL-pay.'}
                # 2. Solicitar invoice para o valor desejado
                params = {'amount': valor_sats * 1000}  # LNURL-pay usa msats
                async with self.session.get(callback, params=params) as invoice_resp:
                    if invoice_resp.status != 200:
                        erro = await invoice_resp.text()
                        return {'success': False, 'error': f'Erro ao solicitar invoice: {erro}'}
                    invoice_data = await invoice_resp.json()
                    invoice = invoice_data.get('pr')
                    if not invoice:
                        return {'success': False, 'error': 'LNURL-pay não retornou invoice.'}
            # 3. Pagar a invoice usando a API Voltz
            import time
            endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/payments"
            payload = {
                'out': True,
                'bolt11': invoice
            }
            start_time = time.time()
            logger.info(f"[LIGHTNING] Iniciando requisição para Voltz (enviar pagamento)...")
            async with self.session.post(
                endpoint,
                headers=self._get_headers(),
                json=payload
            ) as response:
                elapsed = time.time() - start_time
                logger.info(f"[LIGHTNING] Requisição para Voltz finalizada em {elapsed:.2f} segundos (status {response.status})")
                try:
                    data = await response.json()
                except Exception:
                    data = await response.text()
                    logger.error(f'Resposta inesperada da Voltz: {data}')
                    return {
                        'success': False,
                        'error': f'Falha ao enviar pagamento: resposta inesperada: {data}'
                    }
                if response.status == 201 and isinstance(data, dict) and 'payment_hash' in data:
                    return {
                        'success': True,
                        'data': {
                            'payment_hash': data['payment_hash'],
                            'status': 'pending',
                            'destino': lightning_address,
                            'valor_sats': valor_sats
                        }
                    }
                else:
                    error = data.get('message', data) if isinstance(data, dict) else data
                    logger.error(f'Falha ao enviar pagamento: {error}')
                    return {
                        'success': False,
                        'error': f'Falha ao enviar pagamento: {error}'
                    }
        except Exception as e:
            logger.exception('Exceção ao enviar pagamento')
            return {
                'success': False,
                'error': f'Exceção ao enviar pagamento: {str(e)}'
            }

    # --- Verificação de Invoice Enviada (Outgoing) ---
    async def verificar_invoice(self, payment_hash: str) -> Dict[str, Any]:
        """
        Verifica o status de um pagamento enviado (outgoing) usando o payment_hash.
        Args:
            payment_hash: Hash do pagamento enviado
        Returns:
            Dicionário com o status do pagamento e informações relevantes
        """
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/payments/{payment_hash}"
        try:
            await self._ensure_session()
            assert self.session is not None
            async with self.session.get(
                endpoint,
                headers=self._get_headers(use_admin=True)
            ) as response:
                data = await response.json()
                if response.status == 200:
                    status = data.get('status', 'unknown').lower()
                    pago = status in ['paid', 'complete']
                    mensagem = self.status_messages.get(status, self.status_messages['unknown'])
                    return {
                        'success': True,
                        'data': {
                            'status': status,
                            'pago': pago,
                            'message': mensagem,
                            'payment_hash': data.get('payment_hash', ''),
                            'amount': data.get('amount', 0),
                            'fee': data.get('fee', 0),
                            'bolt11': data.get('bolt11', ''),
                            'preimage': data.get('preimage', ''),
                            'destination': data.get('destination', ''),
                            'created_at': data.get('created_at'),
                            'paid_at': data.get('paid_at'),
                            'expires_at': data.get('expires_at')
                        }
                    }
                else:
                    error = data.get('message', await response.text())
                    logger.error(f"Erro ao verificar invoice: {response.status} - {error}")
                    return {
                        'success': False,
                        'error': f"Erro ao verificar invoice: {response.status} - {error}"
                    }
        except Exception as e:
            logger.exception("Exceção ao verificar invoice")
            return {
                'success': False,
                'error': f"Exceção ao verificar invoice: {str(e)}"
            }

    # --- Decodificação de Invoice Lightning ---
    async def decodificar_invoice(self, invoice: str) -> Dict[str, Any]:
        """
        Decodifica uma invoice Lightning (bolt11 ou lnurl) usando a API Voltz.
        Args:
            invoice: Invoice Lightning (bolt11 ou lnurl)
        Returns:
            Dicionário com os dados decodificados ou mensagem de erro
        """
        endpoint = f"{self.config['node_url']}/api/{self.config['api_version']}/payments/decode"
        payload = {"data": invoice}
        try:
            await self._ensure_session()
            assert self.session is not None
            async with self.session.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json=payload
            ) as response:
                data = await response.json()
                if response.status == 200:
                    return {"success": True, "data": data}
                else:
                    logger.error(f"Erro ao decodificar invoice: {data}")
                    return {"success": False, "error": data}
        except Exception as e:
            logger.exception("Exceção ao decodificar invoice")
            return {"success": False, "error": str(e)}

# --- Funções Globais de Conveniência ---
_instancia_global = None

def configurar(wallet_id: str = WALLET_ID, admin_key: str = ADMIN_KEY, invoice_key: str = INVOICE_KEY, node_url: str = NODE_URL):
    """
    Configura a instância global do ValidadorVoltz.
    """
    global _instancia_global
    _instancia_global = ValidadorVoltz(wallet_id, admin_key, invoice_key, node_url)

async def consultar_saldo() -> Dict[str, Any]:
    """
    Consulta o saldo da carteira usando a instância global.
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    async with _instancia_global as validador:
        return await validador.consultar_saldo()

async def criar_fatura(valor_sats: int, memo: str = "", expiracao: int = 3600) -> Dict[str, Any]:
    """
    Cria uma nova fatura Lightning usando a instância global.
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    async with _instancia_global as validador:
        return await validador.criar_fatura(valor_sats, memo, expiracao)

async def verificar_pagamento(payment_hash: str) -> Dict[str, Any]:
    """
    Verifica o status de um pagamento recebido usando a instância global.
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    async with _instancia_global as validador:
        return await validador.verificar_pagamento(payment_hash)

async def enviar_pagamento(lightning_address: str, valor_sats: int) -> Dict[str, Any]:
    """
    Envia um pagamento usando uma fatura Lightning pela instância global.
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    async with _instancia_global as validador:
        return await validador.enviar_pagamento(lightning_address, valor_sats)

async def verificar_invoice(payment_hash: str) -> Dict[str, Any]:
    """
    Verifica o status de um pagamento enviado (outgoing) usando a instância global.
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    async with _instancia_global as validador:
        return await validador.verificar_invoice(payment_hash)

async def decodificar_invoice(invoice: str) -> Dict[str, Any]:
    """
    Decodifica uma invoice Lightning usando a instância global.
    """
    if not _instancia_global:
        return {'success': False, 'error': 'Validador não configurado. Chame configurar() primeiro.'}
    async with _instancia_global as validador:
        return await validador.decodificar_invoice(invoice)

# Remover bloco __main__ de teste, pois as credenciais agora vêm do config.py