#!/usr/bin/env python3
"""
Lightning Address Resolver para Ghost Bot
Converte Lightning Address → BOLT11 → Pagamento via Voltz
Data: 2025-01-27
"""

import requests
import re
import json
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class LightningAddressResolver:
    """
    Resolve Lightning Address para BOLT11 invoice
    Implementa LUD-16 (Lightning Address) + LUD-06 (LNURL-pay)
    """
    
    def __init__(self):
        self.timeout = 10
        self.user_agent = "Ghost Bot/1.0"
    
    def is_valid_lightning_address(self, address: str) -> bool:
        """
        Valida formato Lightning Address
        Formato: username@domain.com
        """
        pattern = r'^[a-z0-9\-_\.+]+@[a-z0-9\-\.]+\.[a-z]{2,}$'
        return bool(re.match(pattern, address.lower()))
    
    def resolve_to_bolt11(self, lightning_address: str, amount_sats: int) -> Dict:
        """
        Resolve Lightning Address para BOLT11 invoice
        
        Args:
            lightning_address: user@domain.com
            amount_sats: Valor em satoshis
            
        Returns:
            dict: {'success': bool, 'bolt11': str, 'error': str}
        """
        try:
            # 1. Validar formato
            if not self.is_valid_lightning_address(lightning_address):
                return {
                    'success': False,
                    'error': 'Formato de Lightning Address inválido'
                }
            
            # 2. Resolver Lightning Address → LNURL endpoint
            lnurl_data = self._resolve_lightning_address(lightning_address)
            if not lnurl_data['success']:
                return lnurl_data
            
            # 3. Fazer request LNURL-pay → obter BOLT11
            bolt11_data = self._request_bolt11(
                lnurl_data['callback'], 
                amount_sats,
                lnurl_data.get('metadata', '')
            )
            
            return bolt11_data
            
        except Exception as e:
            logger.error(f"Erro ao resolver Lightning Address {lightning_address}: {e}")
            return {
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }
    
    def _resolve_lightning_address(self, address: str) -> Dict:
        """
        Passo 1: Resolve Lightning Address → LNURL endpoint
        GET https://domain.com/.well-known/lnurlp/username
        """
        try:
            username, domain = address.split('@')
            well_known_url = f"https://{domain}/.well-known/lnurlp/{username}"
            
            logger.info(f"Resolvendo Lightning Address: {address} → {well_known_url}")
            
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'application/json'
            }
            
            response = requests.get(well_known_url, headers=headers, timeout=self.timeout)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Lightning Address não encontrado (HTTP {response.status_code})'
                }
            
            data = response.json()
            
            # Validar campos obrigatórios LUD-06
            required_fields = ['callback', 'minSendable', 'maxSendable', 'metadata', 'tag']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'error': f'Campo obrigatório ausente: {field}'
                    }
            
            if data.get('tag') != 'payRequest':
                return {
                    'success': False,
                    'error': 'Lightning Address não suporta pagamentos'
                }
            
            return {
                'success': True,
                'callback': data['callback'],
                'min_sendable': data['minSendable'],
                'max_sendable': data['maxSendable'],
                'metadata': data['metadata']
            }
            
        except ValueError:
            return {
                'success': False,
                'error': 'Formato de Lightning Address inválido'
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Erro de rede: {str(e)}'
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': 'Resposta inválida do servidor'
            }
    
    def _request_bolt11(self, callback_url: str, amount_sats: int, metadata: str) -> Dict:
        """
        Passo 2: Request LNURL-pay → obter BOLT11
        GET callback_url?amount=amount_msat
        """
        try:
            amount_msat = amount_sats * 1000
            
            params = {
                'amount': amount_msat
            }
            
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'application/json'
            }
            
            logger.info(f"Solicitando BOLT11: {callback_url} para {amount_sats} sats")
            
            response = requests.get(callback_url, params=params, headers=headers, timeout=self.timeout)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Erro ao solicitar invoice (HTTP {response.status_code})'
                }
            
            data = response.json()
            
            # Verificar se há erro na resposta
            if 'reason' in data or 'status' in data and data['status'] == 'ERROR':
                return {
                    'success': False,
                    'error': data.get('reason', 'Erro desconhecido do servidor')
                }
            
            # Validar campos obrigatórios
            if 'pr' not in data:
                return {
                    'success': False,
                    'error': 'Invoice BOLT11 não retornado'
                }
            
            return {
                'success': True,
                'bolt11': data['pr'],
                'description': data.get('successAction', {}).get('description', ''),
                'expires_at': data.get('expiresAt')
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Erro de rede: {str(e)}'
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': 'Resposta inválida do servidor'
            }

# Função helper para usar no bot
def resolve_lightning_address_to_bolt11(address: str, amount_sats: int) -> Tuple[bool, str, str]:
    """
    Função helper para resolver Lightning Address
    
    Args:
        address: Lightning Address (user@domain.com)
        amount_sats: Valor em satoshis
        
    Returns:
        tuple: (success: bool, bolt11_or_error: str, description: str)
    """
    resolver = LightningAddressResolver()
    result = resolver.resolve_to_bolt11(address, amount_sats)
    
    if result['success']:
        return True, result['bolt11'], result.get('description', '')
    else:
        return False, result['error'], ''

# Exemplo de uso
if __name__ == "__main__":
    resolver = LightningAddressResolver()
    
    # Teste com Lightning Address real
    test_address = "test@walletofsatoshi.com"
    test_amount = 1000  # 1000 sats
    
    print(f"Testando: {test_address} para {test_amount} sats")
    result = resolver.resolve_to_bolt11(test_address, test_amount)
    
    if result['success']:
        print(f"✅ Sucesso! BOLT11: {result['bolt11'][:50]}...")
    else:
        print(f"❌ Erro: {result['error']}")
