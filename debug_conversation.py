#!/usr/bin/env python3
"""
Script de debug para verificar o que está acontecendo no ConversationHandler.
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes, ConversationHandler
from menu.menu_compra import get_conversation_handler, ESCOLHER_MOEDA, ESCOLHER_REDE, ESCOLHER_VALOR

async def debug_conversation():
    """Debug do ConversationHandler."""
    print("🔍 [DEBUG] Iniciando debug do ConversationHandler")
    
    # Obter o ConversationHandler
    conversation_handler = get_conversation_handler()
    
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
    
    # Simular o fluxo completo com debug detalhado
    print("\n🔍 [DEBUG] Simulando fluxo com debug detalhado")
    
    # 1. Comando /start
    print("\n🔍 [DEBUG] 1. Comando /start")
    message1 = Mock(spec=Message)
    message1.text = "/start"
    message1.reply_text = AsyncMock()
    
    update1 = Mock(spec=Update)
    update1.message = message1
    update1.effective_user = user
    update1.effective_chat = chat
    
    # Simular o handler do ConversationHandler
    result1 = await conversation_handler.callback(update1, context)
    print(f"🔍 [DEBUG] Resultado do /start: {result1}")
    print(f"🔍 [DEBUG] Estado atual: {context.user_data.get('_conversation_state', 'None')}")
    
    # 2. Usuário clica em "Comprar"
    print("\n🔍 [DEBUG] 2. Usuário clica em 'Comprar'")
    message2 = Mock(spec=Message)
    message2.text = "Comprar"
    message2.reply_text = AsyncMock()
    
    update2 = Mock(spec=Update)
    update2.message = message2
    update2.effective_user = user
    update2.effective_chat = chat
    
    # Simular o handler do ConversationHandler
    result2 = await conversation_handler.callback(update2, context)
    print(f"🔍 [DEBUG] Resultado do 'Comprar': {result2}")
    print(f"🔍 [DEBUG] Estado atual: {context.user_data.get('_conversation_state', 'None')}")
    
    # 3. Usuário escolhe "Bitcoin (BTC)"
    print("\n🔍 [DEBUG] 3. Usuário escolhe 'Bitcoin (BTC)'")
    message3 = Mock(spec=Message)
    message3.text = "Bitcoin (BTC)"
    message3.reply_text = AsyncMock()
    
    update3 = Mock(spec=Update)
    update3.message = message3
    update3.effective_user = user
    update3.effective_chat = chat
    
    # Simular o handler do ConversationHandler
    result3 = await conversation_handler.callback(update3, context)
    print(f"🔍 [DEBUG] Resultado do 'Bitcoin (BTC)': {result3}")
    print(f"🔍 [DEBUG] Estado atual: {context.user_data.get('_conversation_state', 'None')}")
    
    # 4. Usuário escolhe "Lightning"
    print("\n🔍 [DEBUG] 4. Usuário escolhe 'Lightning'")
    message4 = Mock(spec=Message)
    message4.text = "Lightning"
    message4.reply_text = AsyncMock()
    
    update4 = Mock(spec=Update)
    update4.message = message4
    update4.effective_user = user
    update4.effective_chat = chat
    
    # Simular o handler do ConversationHandler
    result4 = await conversation_handler.callback(update4, context)
    print(f"🔍 [DEBUG] Resultado do 'Lightning': {result4}")
    print(f"🔍 [DEBUG] Estado atual: {context.user_data.get('_conversation_state', 'None')}")
    
    print("\n🔍 [DEBUG] Debug concluído")

if __name__ == "__main__":
    asyncio.run(debug_conversation()) 