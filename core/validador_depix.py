#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Depósitos PIX

Este módulo fornece funcionalidades para validar e verificar o status de depósitos PIX
usando a API Eulem Depix.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Optional, Union, Any

# Chave de API para autenticação
API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0"

# Configuração de logging
logger = logging.getLogger(__name__)

class ValidadorDepix:
    """
    Classe para validação e verificação de depósitos PIX usando a API Eulem Depix.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://depix.eulen.app"):
        """
        Inicializa o validador com as credenciais da API.
        
        Args:
            api_key: Chave de API para autenticação
            base_url: URL base da API (opcional)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.deposit_endpoint = f"{self.base_url}/api/deposit-status"
        self.timeout = aiohttp.ClientTimeout(total=15, connect=5, sock_connect=5, sock_read=5)
        
        # Mapeamento de status para mensagens amigáveis
        self.status_messages = {
            'pending': '⏳ AGUARDANDO PAGAMENTO',
            'paid': '✅ PAGAMENTO CONFIRMADO',
            'completed': '✅ PAGAMENTO CONCLUÍDO',
            'waiting_address': '⚠️ AGUARDANDO ENDEREÇO',
            'expired': '❌ PAGAMENTO EXPIRADO',
            'canceled': '❌ PAGAMENTO CANCELADO',
            'failed': '❌ FALHA NO PAGAMENTO',
            'confirmed': '✅ PAGAMENTO CONFIRMADO',
            'overpaid': '✅ PAGAMENTO CONFIRMADO (VALOR ACIMA)',
            'underpaid': '⚠️ PAGAMENTO INCOMPLETO',
            'depix_sent': '✅ PAGAMENTO RECEBIDO - AGUARDANDO CONFIRMAÇÃO',
            'depix_confirmed': '✅ PAGAMENTO CONFIRMADO',
            'depix_expired': '❌ PAGAMENTO EXPIRADO',
            'depix_canceled': '❌ PAGAMENTO CANCELADO',
            'unknown': '❓ STATUS DESCONHECIDO'
        }
        
        # Mapeamento de status para normalização
        self.status_mapping = {
            'pending': 'pending',
            'paid': 'paid',
            'completed': 'completed',
            'waiting_address': 'waiting_address',
            'expired': 'expired',
            'canceled': 'canceled',
            'failed': 'failed',
            'confirmed': 'completed',
            'overpaid': 'paid',
            'underpaid': 'pending',
            'depix_sent': 'depix_sent',
            'depix_confirmed': 'depix_confirmed',
            'depix_expired': 'depix_expired',
            'depix_canceled': 'depix_canceled'
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna os cabeçalhos HTTP para as requisições."""
        return {
            'User-Agent': 'GhostBot/1.0',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',  # Formato Bearer token
            'Content-Type': 'application/json'
        }
    
    def _normalize_status(self, status: str) -> str:
        """Normaliza o status para um formato padrão."""
        if not status:
            return 'unknown'
        return self.status_mapping.get(status.lower(), 'unknown')
    
    def _format_status_message(self, status: str) -> str:
        """Formata o status para exibição amigável."""
        normalized_status = self._normalize_status(status)
        return self.status_messages.get(normalized_status, f"❓ STATUS DESCONHECIDO: {status}")
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Executa uma requisição HTTP para a API.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint da API
            **kwargs: Argumentos adicionais para a requisição
            
        Returns:
            Dicionário com a resposta da API ou mensagem de erro
        """
        headers = self._get_headers()
        
        # Adiciona os cabeçalhos se não fornecidos
        if 'headers' not in kwargs:
            kwargs['headers'] = headers
        else:
            # Atualiza os cabeçalhos existentes com os nossos
            kwargs['headers'].update(headers)
        
        # Configura o timeout se não fornecido
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        # Configura o SSL como False para evitar problemas de certificado
        if 'ssl' not in kwargs:
            kwargs['ssl'] = False
            
        # Log dos cabeçalhos para debug (remova em produção)
        logger.debug(f"Enviando requisição para {endpoint} com cabeçalhos: {kwargs.get('headers', {})}")
        
        conn = None
        try:
            conn = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)
            
            async with aiohttp.ClientSession(connector=conn) as session:
                async with session.request(method, endpoint, **kwargs) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            return await response.json()
                        except Exception as e:
                            logger.error(f"Erro ao decodificar JSON: {str(e)}")
                            return {"success": False, "error": f"Erro ao decodificar resposta: {str(e)}"}
                    else:
                        error_msg = f"Erro HTTP {response.status}: {response_text}"
                        logger.error(error_msg)
                        return {"success": False, "error": error_msg}
                        
        except asyncio.TimeoutError as e:
            error_msg = f"Tempo limite de conexão excedido: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
        except aiohttp.ClientError as e:
            error_msg = f"Erro de conexão: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}
            
        finally:
            if conn is not None:
                await conn.close()
    
    async def consultar_deposito(self, depix_id: str) -> Dict[str, Any]:
        """
        Consulta o status de um depósito PIX pelo ID.
        
        Args:
            depix_id: ID do depósito PIX
            
        Returns:
            Dicionário com os dados do depósito ou mensagem de erro
        """
        logger.info(f"Consultando depósito ID: {depix_id}")
        
        endpoint = f"{self.deposit_endpoint}?id={depix_id}"
        logger.debug(f"Consultando depósito: {endpoint}")
        response = await self._make_request('GET', endpoint)
        
        # Verifica se a resposta é um dicionário (resposta bem-sucedida)
        if not isinstance(response, dict):
            return {
                "success": False,
                "error": "Resposta inválida do servidor",
                "raw_response": response
            }
            
        # Verifica se há erro na resposta
        if "error" in response and not response.get("success", True):
            return response
            
        # Verifica se há um campo 'response' na resposta
        if 'response' in response and response['response'] is not None:
            data = response['response']
        else:
            # Se não houver 'response', usa a resposta direta
            data = response
            
        if not data:
            # Se não houver dados, retorna erro
            return {
                "success": False,
                "error": "Nenhum dado de depósito encontrado",
                "raw_response": response
            }
            
        status = data.get('status', 'unknown').lower()
        
        # Prepara os dados formatados
        dados_formatados = {
            "blockchainTxID": data.get('blockchainTxID'),
            "status": status,
            "normalized_status": self._normalize_status(status),
            "status_message": self._format_status_message(status),
            "amount_in_cents": data.get('valueInCents', 0),
            "amount_brl": float(data.get('valueInCents', 0)) / 100,
            "pix_key": data.get('pixKey'),
            "payer_name": data.get('payerName'),
            "payer_tax_number": data.get('payerTaxNumber'),
            "expiration": data.get('expiration'),
            "qrId": data.get('qrId', depix_id),
            "bank_tx_id": data.get('bankTxId'),
            "created_at": data.get('createdAt'),
            "updated_at": data.get('updatedAt'),
            "expires_at": data.get('expiresAt'),
            "paid_at": data.get('paidAt'),
            "raw_data": data  # Mantém os dados brutos para referência
        }
        
        return {
            "success": True,
            "data": dados_formatados
        }
    
    async def verificar_pagamento(self, depix_id: str) -> Dict[str, Any]:
        """
        Verifica se um pagamento foi confirmado.
        
        Args:
            depix_id: ID do depósito PIX
            
        Returns:
            Dicionário com o status do pagamento e informações adicionais
        """
        # Primeiro consulta o status do depósito
        resultado = await self.consultar_deposito(depix_id)
        
        # Se houver erro na consulta, retorna o erro
        if not resultado.get("success"):
            return resultado
        
        # Obtém os dados do depósito
        dados = resultado.get("data", {})
        
        # Se não houver dados, retorna erro
        if not dados:
            return {
                "success": False,
                "error": "Nenhum dado de depósito encontrado",
                "pagamento_confirmado": False,
                "status_message": "❌ ERRO AO VERIFICAR PAGAMENTO"
            }
        
        # Obtém e normaliza o status
        status = dados.get("status", "unknown").lower()
        normalized_status = self._normalize_status(status)
        
        # Determina se o pagamento foi confirmado
        pagamento_confirmado = normalized_status in [
            'paid', 'completed', 'confirmed', 'overpaid', 'depix_confirmed'
        ]
        
        # Se tiver blockchainTxID, considera como confirmado independente do status
        if dados.get("blockchainTxID"):
            pagamento_confirmado = True
            status_message = "✅ PAGAMENTO CONFIRMADO NA BLOCKCHAIN"
        else:
            status_message = self._format_status_message(status)
        
        # Prepara o resultado final
        resultado.update({
            "pagamento_confirmado": pagamento_confirmado,
            "status_message": status_message,
            "blockchain_tx_id": dados.get("blockchainTxID"),
            "status": status,
            "normalized_status": normalized_status
        })
        
        return resultado


# Funções de conveniência para uso direto
_instancia_global = None

def configurar(api_key: str, base_url: str = "https://depix.eulen.app"):
    """
    Configura a instância global do ValidadorDepix.
    
    Args:
        api_key: Chave de API para autenticação
        base_url: URL base da API (opcional)
    """
    global _instancia_global
    _instancia_global = ValidadorDepix(api_key, base_url)

# Configura automaticamente a instância global com a chave de API fornecida
configurar(API_KEY)

async def consultar_deposito(depix_id: str) -> Dict[str, Any]:
    """
    Consulta o status de um depósito PIX (usando a instância global).
    
    Args:
        depix_id: ID do depósito PIX
        
    Returns:
        Dicionário com os dados do depósito ou mensagem de erro
    """
    global _instancia_global
    if _instancia_global is None:
        raise RuntimeError("ValidadorDepix não foi configurado. Chame validador_depix.configurar() primeiro.")
    return await _instancia_global.consultar_deposito(depix_id)

async def verificar_pagamento(depix_id: str) -> Dict[str, Any]:
    """
    Verifica se um pagamento foi confirmado (usando a instância global).
    
    Args:
        depix_id: ID do depósito PIX
        
    Returns:
        Dicionário com o status do pagamento e informações adicionais
    """
    global _instancia_global
    if _instancia_global is None:
        raise RuntimeError("ValidadorDepix não foi configurado. Chame validador_depix.configurar() primeiro.")
    return await _instancia_global.verificar_pagamento(depix_id)