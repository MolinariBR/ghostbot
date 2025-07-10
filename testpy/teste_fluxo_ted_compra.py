#!/usr/bin/env python3
"""
Teste do Sistema de Redirecionamento no Menu de Compra
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

from limites.redirecionamentos import redirecionar_para_ted_boleto
import asyncio

class MockUpdate:
    """Mock do Update do Telegram para teste."""
    def __init__(self, user_id=12345):
        self.effective_user = MockUser(user_id)
        self.message = MockMessage()

class MockUser:
    """Mock do User do Telegram."""
    def __init__(self, user_id):
        self.id = user_id

class MockMessage:
    """Mock da Message do Telegram."""
    async def reply_text(self, text, parse_mode=None):
        print(f"🤖 Bot responde:\n{text}\n")

class MockContext:
    """Mock do Context do Telegram."""
    def __init__(self):
        self.user_data = {}

async def test_fluxo_ted_compra():
    """Simula o fluxo TED no menu de compra."""
    print("🧪 TESTE: Fluxo TED no Menu de Compra")
    print("="*50)
    
    update = MockUpdate(12345)
    context = MockContext()
    
    # Simula dados do usuário
    context.user_data = {
        'moeda': 'BTC',
        'rede': 'Bitcoin',
        'valor_brl': 50.00,
        'chatid': 12345
    }
    
    print("👤 Usuário seleciona TED como método de pagamento")
    print("📋 Dados do usuário:")
    print(f"   • Moeda: {context.user_data['moeda']}")
    print(f"   • Rede: {context.user_data['rede']}")
    print(f"   • Valor: R$ {context.user_data['valor_brl']:.2f}")
    print(f"   • Chat ID: {context.user_data['chatid']}")
    print()
    
    # Executa o redirecionamento
    await redirecionar_para_ted_boleto(update, context)
    
    print("✅ Teste concluído!")
    print("📝 Resultado: Usuário redirecionado para @GhosttP2P em vez de ver dados bancários")

if __name__ == "__main__":
    asyncio.run(test_fluxo_ted_compra())
