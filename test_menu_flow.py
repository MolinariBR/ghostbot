#!/usr/bin/env python3
"""
Script de teste para verificar o fluxo do menu de compra.
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes
from menu.menu_compra import start, escolher_moeda, escolher_rede, ESCOLHER_MOEDA, ESCOLHER_REDE, ESCOLHER_VALOR

async def test_menu_flow():
    """Testa o fluxo completo do menu."""
    print("🧪 [TESTE] Iniciando teste do fluxo do menu")
    
    # Mock do usuário
    user = Mock(spec=User)
    user.id = 123456
    
    # Mock do chat
    chat = Mock(spec=Chat)
    chat.id = 123456
    
    # Mock do contexto
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    context.bot = AsyncMock()
    
    # Teste 1: Comando /start
    print("\n🟢 [TESTE] Teste 1: Comando /start")
    message1 = Mock(spec=Message)
    message1.text = "/start"
    message1.reply_text = AsyncMock()
    
    update1 = Mock(spec=Update)
    update1.message = message1
    update1.effective_user = user
    update1.effective_chat = chat
    
    result1 = await start(update1, context)
    print(f"🟢 [TESTE] Resultado do start: {result1} (esperado: {ESCOLHER_MOEDA})")
    assert result1 == ESCOLHER_MOEDA, f"Start deveria retornar {ESCOLHER_MOEDA}, mas retornou {result1}"
    
    # Teste 2: Usuário clica em "Comprar"
    print("\n🟢 [TESTE] Teste 2: Usuário clica em 'Comprar'")
    message2 = Mock(spec=Message)
    message2.text = "Comprar"
    message2.reply_text = AsyncMock()
    
    update2 = Mock(spec=Update)
    update2.message = message2
    update2.effective_user = user
    update2.effective_chat = chat
    
    result2 = await escolher_moeda(update2, context)
    print(f"🟢 [TESTE] Resultado do escolher_moeda (Comprar): {result2} (esperado: {ESCOLHER_REDE})")
    assert result2 == ESCOLHER_REDE, f"Escolher moeda deveria retornar {ESCOLHER_REDE}, mas retornou {result2}"
    
    # Teste 3: Usuário escolhe "Bitcoin (BTC)"
    print("\n🟢 [TESTE] Teste 3: Usuário escolhe 'Bitcoin (BTC)'")
    message3 = Mock(spec=Message)
    message3.text = "Bitcoin (BTC)"
    message3.reply_text = AsyncMock()
    
    update3 = Mock(spec=Update)
    update3.message = message3
    update3.effective_user = user
    update3.effective_chat = chat
    
    result3 = await escolher_moeda(update3, context)
    print(f"🟢 [TESTE] Resultado do escolher_moeda (Bitcoin): {result3} (esperado: {ESCOLHER_REDE})")
    assert result3 == ESCOLHER_REDE, f"Escolher moeda deveria retornar {ESCOLHER_REDE}, mas retornou {result3}"
    
    # Teste 4: Usuário escolhe "Lightning"
    print("\n🟢 [TESTE] Teste 4: Usuário escolhe 'Lightning'")
    message4 = Mock(spec=Message)
    message4.text = "Lightning"
    message4.reply_text = AsyncMock()
    
    update4 = Mock(spec=Update)
    update4.message = message4
    update4.effective_user = user
    update4.effective_chat = chat
    
    result4 = await escolher_rede(update4, context)
    print(f"🟢 [TESTE] Resultado do escolher_rede (Lightning): {result4} (esperado: {ESCOLHER_VALOR})")
    assert result4 == ESCOLHER_VALOR, f"Escolher rede deveria retornar {ESCOLHER_VALOR}, mas retornou {result4}"
    
    print("\n✅ [TESTE] Todos os testes passaram!")
    print("✅ [TESTE] O fluxo do menu está funcionando corretamente")

if __name__ == "__main__":
    asyncio.run(test_menu_flow()) 