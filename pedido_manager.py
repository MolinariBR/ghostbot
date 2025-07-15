#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Pedidos para Bot Telegram

Este módulo gerencia o salvamento de pedidos no banco de dados e
ativa a verificação automática de pagamentos PIX.
"""

import asyncio
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, Callable

from core.validador_depix import ValidadorDepix
from config.config import BASE_URL

# Configuração de logging
logger = logging.getLogger(__name__)

class PedidoManager:
    """
    Classe para gerenciar pedidos e verificação de pagamentos.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de pedidos."""
        self.api_base_url = BASE_URL
        self.lightning_callback = None  # Callback para ativar Lightning Address
        print("🟢 [PEDIDO_MANAGER] Inicializado - aguardando eventos de compra...")
    
    def set_lightning_callback(self, callback: Callable):
        """
        Define o callback para ativar o estado de Lightning Address.
        
        Args:
            callback: Função que será chamada quando o pagamento for confirmado
        """
        self.lightning_callback = callback
        print("🟢 [PEDIDO_MANAGER] Callback de Lightning Address configurado")
    
    async def salvar_pedido_e_verificar(self, pedido_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva o pedido no banco e inicia a verificação de pagamento.
        
        Args:
            pedido_data: Dados do pedido a ser salvo
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            print("🟡 [PEDIDO_MANAGER] Salvando pedido no banco...")
            
            # Salvar pedido no banco
            resultado_salvar = await self._salvar_pedido_banco(pedido_data)
            
            if not resultado_salvar['success']:
                return resultado_salvar
            
            pedido_id = resultado_salvar['pedido_id']
            print(f"✅ [PEDIDO_MANAGER] Pedido #{pedido_id} salvo com sucesso")
            
            # Iniciar verificação em background
            asyncio.create_task(self._verificar_pagamento_background(pedido_id, pedido_data))
            
            return {
                'success': True,
                'pedido_id': pedido_id,
                'message': 'Pedido salvo e verificação iniciada'
            }
            
        except Exception as e:
            print(f"❌ [PEDIDO_MANAGER] Erro ao salvar pedido: {e}")
            return {
                'success': False,
                'error': f'Erro ao salvar pedido: {str(e)}'
            }
    
    async def _salvar_pedido_banco(self, pedido_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva o pedido no banco de dados.
        
        Args:
            pedido_data: Dados do pedido
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            # Preparar dados para o banco
            dados_banco = {
                'user_id': pedido_data['user_id'],
                'username': pedido_data['username'],
                'moeda': pedido_data['moeda'],
                'rede': pedido_data['rede'],
                'valor_sats': pedido_data['valor_sats'],
                'valor_btc': pedido_data['valor_btc'],
                'valor_real': pedido_data['valor_real'],
                'cotacao_preco_btc': pedido_data.get('cotacao', {}).get('preco_btc', 0),
                'cotacao_fonte': pedido_data.get('cotacao', {}).get('fonte', 'fallback'),
                'status': pedido_data['status'],
                'criado_em': datetime.now().isoformat()
            }
            
            # Chamar API para salvar no banco
            response = requests.post(
                f"{self.api_base_url}/api/deposit.php",
                json=dados_banco,
                timeout=30
            )
            
            if response.status_code == 200:
                resultado = response.json()
                
                if resultado.get('success'):
                    return {
                        'success': True,
                        'pedido_id': resultado['data']['id']
                    }
                else:
                    return {
                        'success': False,
                        'error': resultado.get('error', 'Erro desconhecido')
                    }
            else:
                return {
                    'success': False,
                    'error': f'Erro HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao salvar no banco: {str(e)}'
            }
    
    async def _verificar_pagamento_background(self, pedido_id: int, pedido_data: Dict[str, Any]):
        """
        Executa a verificação de pagamento em background.
        
        Args:
            pedido_id: ID do pedido
            pedido_data: Dados do pedido
        """
        try:
            print(f"🟡 [PEDIDO_MANAGER] Iniciando verificação para pedido #{pedido_id}")
            
            # Configurar validador Depix
            validador = ValidadorDepix(
                api_key="sua_api_key_aqui",  # Substituir pela chave real
                base_url="https://useghost.squareweb.app/ghostbackend"
            )
            
            # Verificar pagamento 5 vezes a cada 30 segundos
            max_tentativas = 5
            intervalo = 30  # segundos
            
            for tentativa in range(max_tentativas):
                print(f"🟡 [PEDIDO_MANAGER] Tentativa {tentativa + 1}/{max_tentativas} para pedido #{pedido_id}")
                
                try:
                    # Verificar pagamento
                    resultado = await validador.verificar_pagamento_pedido(pedido_id)
                    
                    if resultado.get('success'):
                        if resultado['data'].get('pago'):
                            print(f"✅ [PEDIDO_MANAGER] Pagamento confirmado para pedido #{pedido_id}")
                            
                            # Atualizar status do pedido
                            await self.atualizar_status_pedido(
                                pedido_id, 
                                'pagamento_confirmado',
                                {
                                    'blockchain_txid': resultado['data'].get('blockchain_txid'),
                                    'confirmado_em': datetime.now().isoformat()
                                }
                            )
                            
                            # Chamar callback para ativar Lightning Address
                            user_id = pedido_data['user_id']
                            await self._ativar_lightning_address(user_id, pedido_id)
                            
                            return  # Sair da verificação
                        else:
                            print(f"⏳ [PEDIDO_MANAGER] Pagamento ainda pendente para pedido #{pedido_id}")
                    else:
                        print(f"⚠️ [PEDIDO_MANAGER] Erro na verificação: {resultado.get('error')}")
                        
                except Exception as e:
                    print(f"❌ [PEDIDO_MANAGER] Erro na tentativa {tentativa + 1}: {e}")
                
                # Aguardar antes da próxima tentativa (exceto na última)
                if tentativa < max_tentativas - 1:
                    print(f"⏰ [PEDIDO_MANAGER] Aguardando {intervalo}s antes da próxima tentativa...")
                    await asyncio.sleep(intervalo)
            
            print(f"⏰ [PEDIDO_MANAGER] Verificação finalizada para pedido #{pedido_id} - pagamento não confirmado")
            
            # Atualizar status para expirado se não foi confirmado
            await self.atualizar_status_pedido(pedido_id, 'expirado')
            
        except Exception as e:
            print(f"❌ [PEDIDO_MANAGER] Erro na verificação em background: {e}")
    
    async def _ativar_lightning_address(self, user_id: int, pedido_id: int):
        """
        Ativa o estado de aguardar endereço Lightning.
        
        Args:
            user_id: ID do usuário
            pedido_id: ID do pedido
        """
        try:
            print(f"🟢 [PEDIDO_MANAGER] Ativando Lightning Address para usuário {user_id}, pedido {pedido_id}")
            
            # Chamar o callback se estiver configurado
            if self.lightning_callback:
                await self.lightning_callback(user_id, pedido_id)
                print(f"✅ [PEDIDO_MANAGER] Callback de Lightning Address executado para usuário {user_id}")
            else:
                print(f"⚠️ [PEDIDO_MANAGER] Callback de Lightning Address não configurado")
            
        except Exception as e:
            print(f"❌ [PEDIDO_MANAGER] Erro ao ativar Lightning Address: {e}")
    
    async def atualizar_status_pedido(self, pedido_id: int, status: str, dados_extras: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Atualiza o status de um pedido no banco de dados.
        
        Args:
            pedido_id: ID do pedido
            status: Novo status
            dados_extras: Dados extras para salvar
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            dados_atualizacao = {
                'pedido_id': pedido_id,
                'status': status,
                'atualizado_em': datetime.now().isoformat()
            }
            
            if dados_extras:
                dados_atualizacao.update(dados_extras)
            
            # Chamar API para atualizar
            response = requests.post(
                f"{self.api_base_url}/api/update_pedido.php",
                json=dados_atualizacao,
                timeout=30
            )
            
            if response.status_code == 200:
                resultado = response.json()
                
                if resultado.get('success'):
                    print(f"✅ [PEDIDO_MANAGER] Status do pedido #{pedido_id} atualizado para '{status}'")
                    return {'success': True}
                else:
                    print(f"❌ [PEDIDO_MANAGER] Erro ao atualizar status: {resultado.get('error')}")
                    return {'success': False, 'error': resultado.get('error')}
            else:
                print(f"❌ [PEDIDO_MANAGER] Erro HTTP {response.status_code} ao atualizar status")
                return {'success': False, 'error': f'Erro HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"❌ [PEDIDO_MANAGER] Erro ao atualizar status: {e}")
            return {'success': False, 'error': str(e)}

# Instância global
pedido_manager = PedidoManager() 