#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Integração Lightning Address

Este script testa a integração entre o pedido_manager e o validador_voltz
para envio de pagamentos Lightning.
"""

import asyncio
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.validador_voltz import configurar as configurar_voltz, consultar_saldo, enviar_pagamento
from menu.menu_compra import validar_endereco_lightning

async def test_lightning_integration():
    """Testa a integração Lightning Address."""
    print("🟢 [TESTE] Iniciando teste de integração Lightning...")
    
    # Configurar o validador Voltz
    print("🟡 [TESTE] Configurando validador Voltz...")
    configurar_voltz(
        wallet_id="f3c366b7fb6f43fa9467c4dccedaf824",
        admin_key="8fce34f4b0f8446a990418bd167dc644",
        invoice_key="b2f68df91c8848f6a1db26f2e403321f",
        node_url="https://lnvoltz.com"
    )
    
    # Teste 1: Consultar saldo
    print("\n🟡 [TESTE] 1. Testando consulta de saldo...")
    try:
        saldo_result = await consultar_saldo()
        if saldo_result.get('success'):
            saldo = saldo_result['data']['balance']
            print(f"✅ [TESTE] Saldo atual: {saldo:,} sats")
        else:
            print(f"❌ [TESTE] Erro ao consultar saldo: {saldo_result.get('error')}")
    except Exception as e:
        print(f"❌ [TESTE] Exceção ao consultar saldo: {e}")
    
    # Teste 2: Validar endereços Lightning
    print("\n🟡 [TESTE] 2. Testando validação de endereços Lightning...")
    
    enderecos_teste = [
        "teste@walletofsatoshi.com",
        "user@domain.com",
        "lnbc1234567890abcdef",
        "invalid_address",
        "test@",
        "@domain.com"
    ]
    
    for endereco in enderecos_teste:
        is_valid = validar_endereco_lightning(endereco)
        status = "✅ VÁLIDO" if is_valid else "❌ INVÁLIDO"
        print(f"   {status}: {endereco}")
    
    # Teste 3: Teste de envio de pagamento (com valor pequeno)
    print("\n🟡 [TESTE] 3. Testando envio de pagamento...")
    
    # Endereço de teste (substitua por um endereço válido para teste real)
    endereco_teste = "teste@walletofsatoshi.com"
    valor_teste = 100  # 100 sats
    
    if validar_endereco_lightning(endereco_teste):
        try:
            print(f"🟡 [TESTE] Tentando enviar {valor_teste} sats para {endereco_teste}...")
            
            # Nota: Este teste pode falhar se o endereço não for real
            # É apenas para verificar se a API está funcionando
            pagamento_result = await enviar_pagamento(endereco_teste)
            
            if pagamento_result.get('success'):
                payment_hash = pagamento_result['data']['payment_hash']
                print(f"✅ [TESTE] Pagamento enviado! Hash: {payment_hash}")
            else:
                print(f"⚠️ [TESTE] Erro no envio (esperado para endereço de teste): {pagamento_result.get('error')}")
                
        except Exception as e:
            print(f"⚠️ [TESTE] Exceção no envio (esperado): {e}")
    else:
        print(f"❌ [TESTE] Endereço de teste inválido: {endereco_teste}")
    
    print("\n✅ [TESTE] Teste de integração Lightning concluído!")

if __name__ == "__main__":
    print("🚀 [TESTE] Iniciando teste de integração Lightning Address...")
    asyncio.run(test_lightning_integration()) 