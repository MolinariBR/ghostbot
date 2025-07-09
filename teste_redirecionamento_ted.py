#!/usr/bin/env python3
"""
Teste do Sistema de Redirecionamento TED/Boleto
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

from limites.redirecionamentos import RedirecionamentoManager
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
    pass

async def test_redirecionamento_ted_boleto():
    """Testa o redirecionamento TED/Boleto."""
    print("🧪 TESTE: Redirecionamento TED/Boleto")
    print("="*50)
    
    update = MockUpdate(12345)
    context = MockContext()
    
    # Testa redirecionamento TED/Boleto
    await RedirecionamentoManager.redirecionar_ted_boleto(update, context)
    
    print("✅ Teste concluído com sucesso!")

if __name__ == "__main__":
    asyncio.run(test_redirecionamento_ted_boleto())
