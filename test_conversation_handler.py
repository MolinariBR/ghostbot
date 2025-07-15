#!/usr/bin/env python3
"""
Script de teste para verificar a configuração do ConversationHandler.
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes, ConversationHandler
from menu.menu_compra import get_conversation_handler, ESCOLHER_MOEDA, ESCOLHER_REDE, ESCOLHER_VALOR

async def test_conversation_handler():
    """Testa a configuração do ConversationHandler."""
    print("🧪 [TESTE] Iniciando teste do ConversationHandler")
    
    # Obter o ConversationHandler
    conversation_handler = get_conversation_handler()
    print(f"🟢 [TESTE] ConversationHandler obtido: {type(conversation_handler)}")
    
    # Verificar os estados
    states = conversation_handler.states
    print(f"🟢 [TESTE] Estados configurados: {list(states.keys())}")
    
    # Verificar se ESCOLHER_MOEDA está configurado
    if ESCOLHER_MOEDA in states:
        handlers = states[ESCOLHER_MOEDA]
        print(f"🟢 [TESTE] Handlers para ESCOLHER_MOEDA: {len(handlers)}")
        for handler in handlers:
            print(f"  - {type(handler)}")
    else:
        print("❌ [TESTE] ESCOLHER_MOEDA não está configurado!")
    
    # Verificar se ESCOLHER_REDE está configurado
    if ESCOLHER_REDE in states:
        handlers = states[ESCOLHER_REDE]
        print(f"🟢 [TESTE] Handlers para ESCOLHER_REDE: {len(handlers)}")
        for handler in handlers:
            print(f"  - {type(handler)}")
    else:
        print("❌ [TESTE] ESCOLHER_REDE não está configurado!")
    
    # Verificar se ESCOLHER_VALOR está configurado
    if ESCOLHER_VALOR in states:
        handlers = states[ESCOLHER_VALOR]
        print(f"🟢 [TESTE] Handlers para ESCOLHER_VALOR: {len(handlers)}")
        for handler in handlers:
            print(f"  - {type(handler)}")
    else:
        print("❌ [TESTE] ESCOLHER_VALOR não está configurado!")
    
    # Verificar entry points
    entry_points = conversation_handler.entry_points
    print(f"🟢 [TESTE] Entry points: {len(entry_points)}")
    for handler in entry_points:
        print(f"  - {type(handler)}")
    
    # Verificar fallbacks
    fallbacks = conversation_handler.fallbacks
    print(f"🟢 [TESTE] Fallbacks: {len(fallbacks)}")
    for handler in fallbacks:
        print(f"  - {type(handler)}")
    
    print("\n✅ [TESTE] Análise do ConversationHandler concluída")

if __name__ == "__main__":
    asyncio.run(test_conversation_handler()) 