#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para o validador_depix.py

Este script testa as funcionalidades principais do validador de PIX.
"""

import asyncio
import sys
import os
import logging
from core.validador_depix import consultar_deposito, verificar_pagamento

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def testar_validador(depix_id: str):
    """
    Testa as funções principais do validador de PIX.
    """
    print(f"\n{'='*50}")
    print(f"INICIANDO TESTE PARA DEPIX_ID: {depix_id}")
    print(f"{'='*50}")
    
    try:
        # Teste 1: Consulta de depósito
        print("\n🔍 Testando consulta de depósito...")
        resultado_consulta = await consultar_deposito(depix_id)
        
        print("\n📋 Resultado da consulta:")
        print(f"- Sucesso: {resultado_consulta.get('success', False)}")
        
        if resultado_consulta.get('success'):
            dados = resultado_consulta.get('data', {})
            print(f"- ID: {dados.get('id', 'N/A')}")
            print(f"- Status: {dados.get('status', 'N/A')}")
            print(f"- Valor: R$ {float(dados.get('amount_in_cents', 0))/100:.2f}")
            print(f"- TxID: {dados.get('blockchainTxID', 'N/A')}")
        else:
            print(f"- Erro: {resultado_consulta.get('error', 'Erro desconhecido')}")
        
        # Teste 2: Verificação de pagamento
        print("\n🔍 Testando verificação de pagamento...")
        resultado_pagamento = await verificar_pagamento(depix_id)
        
        print("\n📋 Resultado da verificação de pagamento:")
        print(f"- Sucesso: {resultado_pagamento.get('success', False)}")
        
        if resultado_pagamento.get('success'):
            dados = resultado_pagamento.get('data', {})
            print(f"- Status: {dados.get('status', 'N/A')}")
            print(f"- Mensagem: {dados.get('message', 'N/A')}")
            print(f"- Confirmado: {dados.get('pago', False)}")
        else:
            print(f"- Erro: {resultado_pagamento.get('error', 'Erro desconhecido')}")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*50}")
    print("TESTE CONCLUÍDO")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    # Verifica se um ID de depósito foi fornecido como argumento
    if len(sys.argv) > 1:
        depix_id = sys.argv[1]
    else:
        # ID de exemplo (substitua por um ID real se quiser testar sem argumentos)
        depix_id = input("Digite o ID do depósito PIX para teste: ").strip()
    
    # Executa o teste
    asyncio.run(testar_validador(depix_id))
