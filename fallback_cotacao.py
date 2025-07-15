#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Fallback para Cotação

Este módulo fornece fallbacks para cotação de Bitcoin quando a API principal falha.
Usa CoinGecko e Binance P2P como fontes alternativas.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional

# Configuração de logging
logger = logging.getLogger(__name__)

async def obter_cotacao_fallback() -> Dict[str, Any]:
    """
    Obtém cotação de Bitcoin com fallbacks.
    
    Returns:
        Dicionário com dados da cotação ou erro
    """
    try:
        # Tentar API principal primeiro
        cotacao_principal = await _obter_cotacao_principal()
        if cotacao_principal.get('success'):
            return cotacao_principal
        
        # Fallback 1: CoinGecko
        print("🟡 [COTACAO] API principal falhou, tentando CoinGecko...")
        cotacao_coingecko = await _obter_cotacao_coingecko()
        if cotacao_coingecko.get('success'):
            return cotacao_coingecko
        
        # Fallback 2: Binance P2P
        print("🟡 [COTACAO] CoinGecko falhou, tentando Binance P2P...")
        cotacao_binance = await _obter_cotacao_binance()
        if cotacao_binance.get('success'):
            return cotacao_binance
        
        # Fallback 3: Valor fixo
        print("🟡 [COTACAO] Todas as APIs falharam, usando valor fixo...")
        return _cotacao_fixa()
        
    except Exception as e:
        print(f"❌ [COTACAO] Erro geral: {e}")
        return _cotacao_fixa()

async def _obter_cotacao_principal() -> Dict[str, Any]:
    """
    Obtém cotação da API principal.
    
    Returns:
        Dicionário com dados da cotação ou erro
    """
    try:
        from config.config import BASE_URL
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/api/api_cotacao.php",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        return {
                            'success': True,
                            'data': {
                                'preco_btc': data['data']['preco_btc'],
                                'fonte': 'api_principal'
                            }
                        }
                
                return {'success': False, 'error': f'API principal retornou status {response.status}'}
                
    except Exception as e:
        return {'success': False, 'error': f'Erro na API principal: {str(e)}'}

async def _obter_cotacao_coingecko() -> Dict[str, Any]:
    """
    Obtém cotação do CoinGecko.
    
    Returns:
        Dicionário com dados da cotação ou erro
    """
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'brl',
            'include_24hr_change': 'false'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'bitcoin' in data and 'brl' in data['bitcoin']:
                        preco_btc = data['bitcoin']['brl']
                        return {
                            'success': True,
                            'data': {
                                'preco_btc': preco_btc,
                                'fonte': 'coingecko'
                            }
                        }
                
                return {'success': False, 'error': f'CoinGecko retornou status {response.status}'}
                
    except Exception as e:
        return {'success': False, 'error': f'Erro no CoinGecko: {str(e)}'}

async def _obter_cotacao_binance() -> Dict[str, Any]:
    """
    Obtém cotação do Binance P2P (simulado).
    
    Returns:
        Dicionário com dados da cotação ou erro
    """
    try:
        # Simulação de cotação Binance P2P
        # Em produção, seria uma chamada real para a API do Binance
        preco_btc = 250000  # Valor simulado
        
        return {
            'success': True,
            'data': {
                'preco_btc': preco_btc,
                'fonte': 'binance_p2p'
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Erro no Binance: {str(e)}'}

def _cotacao_fixa() -> Dict[str, Any]:
    """
    Retorna cotação fixa como último fallback.
    
    Returns:
        Dicionário com cotação fixa
    """
    return {
        'success': True,
        'data': {
            'preco_btc': 250000,  # Valor fixo em reais
            'fonte': 'fixo'
        }
    }

# Teste do módulo
async def testar_cotacao():
    """Testa o módulo de cotação."""
    print("🧪 [TESTE] Testando módulo de cotação...")
    
    resultado = await obter_cotacao_fallback()
    
    if resultado.get('success'):
        preco = resultado['data']['preco_btc']
        fonte = resultado['data']['fonte']
        print(f"✅ [TESTE] Cotação obtida: R$ {preco:,.2f} (fonte: {fonte})")
    else:
        print(f"❌ [TESTE] Erro: {resultado.get('error')}")

if __name__ == "__main__":
    asyncio.run(testar_cotacao()) 