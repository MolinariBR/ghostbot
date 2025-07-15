#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Stateless Function - Pedido Manager
"""

import sys
import os
import asyncio
import logging

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_stateless.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_stateless_function():
    """Testa o funcionamento do Stateless Function"""
    
    try:
        logger.info("🧪 INICIANDO TESTE DO STATELESS FUNCTION")
        
        # Importa a função
        from api.pedido_manager import salvar_e_verificar_pagamento
        
        # Dados de teste
        dados_pedido_teste = {
            'gtxid': f'teste_{12345}',
            'chatid': '123456789',
            'moeda': 'BTC',
            'rede': 'Lightning',
            'valor': 50.0,
            'comissao': 5.0,
            'parceiro': 1.0,
            'cotacao': 250000.0,
            'recebe': 0.000176,
            'forma_pagamento': 'PIX'
        }
        
        depix_id_teste = f'teste_depix_{12345}'
        
        logger.info("📊 Dados de teste preparados:")
        logger.info(f"   - gtxid: {dados_pedido_teste['gtxid']}")
        logger.info(f"   - chatid: {dados_pedido_teste['chatid']}")
        logger.info(f"   - valor: R$ {dados_pedido_teste['valor']}")
        logger.info(f"   - depix_id: {depix_id_teste}")
        
        # Executa a função
        logger.info("🚀 Executando salvar_e_verificar_pagamento...")
        salvar_e_verificar_pagamento(dados_pedido_teste, depix_id_teste)
        
        logger.info("✅ TESTE CONCLUÍDO COM SUCESSO")
        
        # Verifica se o arquivo de log foi criado
        if os.path.exists('logs/pedido_manager.log'):
            logger.info("📝 Log do pedido_manager criado com sucesso")
            with open('logs/pedido_manager.log', 'r') as f:
                log_content = f.read()
                logger.info(f"📄 Últimas linhas do log:\n{log_content[-1000:]}")
        else:
            logger.warning("⚠️ Arquivo de log não encontrado")
            
    except Exception as e:
        logger.error(f"❌ ERRO NO TESTE: {e}")
        logger.error(f"📋 Tipo do erro: {type(e).__name__}")
        import traceback
        logger.error(f"📄 Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_stateless_function() 