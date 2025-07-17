"""
State Validator - Validação de estado do usuário
===============================================

Este módulo fornece validação de estado para garantir consistência
dos dados do usuário durante as conversas do bot.
"""

import logging
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from core.session_manager import get_user_data, set_user_data, clear_user_data

logger = logging.getLogger(__name__)

class StateValidator:
    """
    Validador de estado para bot do Telegram.
    
    Garante:
    - Consistência de dados
    - Validação de entrada
    - Prevenção de estados inválidos
    """
    
    @staticmethod
    async def validate_pedido_state(user_id: str) -> Dict[str, Any]:
        """
        Valida o estado atual do pedido do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com estado validado ou erro
        """
        try:
            # Obter dados do pedido
            pedido_id = await get_user_data(user_id, 'pedido_id')
            valor = await get_user_data(user_id, 'valor')
            moeda = await get_user_data(user_id, 'moeda')
            status = await get_user_data(user_id, 'status')
            
            # Validar campos obrigatórios
            if not pedido_id:
                return {
                    'valid': False,
                    'error': 'Pedido não encontrado',
                    'message': '❌ **Pedido não encontrado**\n\n🔄 Inicie uma nova compra.'
                }
            
            if not valor or not moeda:
                return {
                    'valid': False,
                    'error': 'Dados do pedido incompletos',
                    'message': '❌ **Dados incompletos**\n\n🔄 Inicie uma nova compra.'
                }
            
            # Validar valores
            try:
                valor_float = float(valor)
                if valor_float <= 0:
                    return {
                        'valid': False,
                        'error': 'Valor inválido',
                        'message': '❌ **Valor inválido**\n\n💰 O valor deve ser maior que zero.'
                    }
            except (ValueError, TypeError):
                return {
                    'valid': False,
                    'error': 'Valor não numérico',
                    'message': '❌ **Valor inválido**\n\n💰 O valor deve ser um número válido.'
                }
            
            # Validar moeda
            moedas_validas = ['BRL', 'USD', 'USDT', 'BTC', 'SAT']
            if moeda not in moedas_validas:
                return {
                    'valid': False,
                    'error': 'Moeda inválida',
                    'message': f'❌ **Moeda inválida**\n\n💱 Moedas aceitas: {", ".join(moedas_validas)}'
                }
            
            # Validar status
            status_validos = ['aguardando_pagamento', 'pago', 'enviando', 'concluido', 'cancelado']
            if status and status not in status_validos:
                return {
                    'valid': False,
                    'error': 'Status inválido',
                    'message': '❌ **Status inválido**\n\n🔄 Inicie uma nova compra.'
                }
            
            return {
                'valid': True,
                'pedido_id': pedido_id,
                'valor': valor_float,
                'moeda': moeda,
                'status': status
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na validação do pedido: {e}")
            return {
                'valid': False,
                'error': 'Erro interno',
                'message': '❌ **Erro interno**\n\n🔧 Tente novamente ou entre em contato com o suporte.'
            }
    
    @staticmethod
    async def validate_lightning_address(address: str) -> Dict[str, Any]:
        """
        Valida um endereço Lightning.
        
        Args:
            address: Endereço Lightning a ser validado
            
        Returns:
            Dicionário com resultado da validação
        """
        try:
            if not address or not address.strip():
                return {
                    'valid': False,
                    'error': 'Endereço vazio',
                    'message': '❌ **Endereço vazio**\n\n⚡ Por favor, envie um endereço Lightning válido.'
                }
            
            address = address.strip()
            
            # Validar Lightning Address (formato: user@domain.com)
            if '@' in address:
                parts = address.split('@')
                if len(parts) != 2:
                    return {
                        'valid': False,
                        'error': 'Formato Lightning Address inválido',
                        'message': '❌ **Formato inválido**\n\n⚡ Lightning Address deve ser: `user@domain.com`'
                    }
                
                user, domain = parts
                if not user or not domain or '.' not in domain:
                    return {
                        'valid': False,
                        'error': 'Lightning Address malformado',
                        'message': '❌ **Endereço inválido**\n\n⚡ Exemplo válido: `sua_carteira@walletofsatoshi.com`'
                    }
                
                return {
                    'valid': True,
                    'type': 'lightning_address',
                    'address': address
                }
            
            # Validar Invoice Lightning (formato: lnbc...)
            elif address.startswith('lnbc'):
                if len(address) < 50:  # Invoice mínimo
                    return {
                        'valid': False,
                        'error': 'Invoice Lightning muito curto',
                        'message': '❌ **Invoice inválido**\n\n⚡ O invoice Lightning deve ter pelo menos 50 caracteres.'
                    }
                
                return {
                    'valid': True,
                    'type': 'lightning_invoice',
                    'address': address
                }
            
            else:
                return {
                    'valid': False,
                    'error': 'Formato não reconhecido',
                    'message': '❌ **Formato não reconhecido**\n\n⚡ **Formatos aceitos:**\n'
                              '• Lightning Address: `user@domain.com`\n'
                              '• Invoice Lightning: `lnbc...`\n\n'
                              '💡 **Exemplo:** `sua_carteira@walletofsatoshi.com`'
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na validação do endereço Lightning: {e}")
            return {
                'valid': False,
                'error': 'Erro interno',
                'message': '❌ **Erro interno**\n\n🔧 Tente novamente ou entre em contato com o suporte.'
            }
    
    @staticmethod
    async def validate_valor_entrada(valor: str, moeda: str) -> Dict[str, Any]:
        """
        Valida o valor de entrada do usuário.
        
        Args:
            valor: Valor digitado pelo usuário
            moeda: Moeda selecionada
            
        Returns:
            Dicionário com resultado da validação
        """
        try:
            if not valor or not valor.strip():
                return {
                    'valid': False,
                    'error': 'Valor vazio',
                    'message': '❌ **Valor vazio**\n\n💰 Por favor, digite um valor válido.'
                }
            
            valor = valor.strip().replace(',', '.')
            
            # Validar se é número
            try:
                valor_float = float(valor)
            except ValueError:
                return {
                    'valid': False,
                    'error': 'Valor não numérico',
                    'message': '❌ **Valor inválido**\n\n💰 Digite apenas números (ex: 100.50).'
                }
            
            # Validar valor mínimo e máximo por moeda
            limites = {
                'BRL': {'min': 10.0, 'max': 10000.0},
                'USD': {'min': 2.0, 'max': 2000.0},
                'USDT': {'min': 2.0, 'max': 2000.0},
                'BTC': {'min': 0.0001, 'max': 1.0},
                'SAT': {'min': 10000, 'max': 100000000}
            }
            
            if moeda not in limites:
                return {
                    'valid': False,
                    'error': 'Moeda não suportada',
                    'message': f'❌ **Moeda não suportada**\n\n💱 Moedas aceitas: {", ".join(limites.keys())}'
                }
            
            limite = limites[moeda]
            
            if valor_float < limite['min']:
                return {
                    'valid': False,
                    'error': 'Valor muito baixo',
                    'message': f'❌ **Valor muito baixo**\n\n💰 Valor mínimo para {moeda}: {limite["min"]}'
                }
            
            if valor_float > limite['max']:
                return {
                    'valid': False,
                    'error': 'Valor muito alto',
                    'message': f'❌ **Valor muito alto**\n\n💰 Valor máximo para {moeda}: {limite["max"]}'
                }
            
            return {
                'valid': True,
                'valor': valor_float,
                'moeda': moeda
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na validação do valor: {e}")
            return {
                'valid': False,
                'error': 'Erro interno',
                'message': '❌ **Erro interno**\n\n🔧 Tente novamente ou entre em contato com o suporte.'
            }
    
    @staticmethod
    async def clear_user_state(user_id: str) -> None:
        """
        Limpa o estado do usuário de forma segura.
        """
        try:
            # Limpar toda a sessão do usuário
            await clear_user_data(user_id)
            
            logger.info(f"🧹 Estado limpo para usuário: {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar estado do usuário {user_id}: {e}")

# Instância global do StateValidator
state_validator = StateValidator() 