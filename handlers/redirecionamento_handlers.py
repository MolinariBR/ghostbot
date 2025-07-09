#!/usr/bin/env python3
"""
Handlers de Redirecionamento
Integra os redirecionamentos automáticos nos handlers do bot.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from limites.redirecionamentos import redirecionar_para_ted_boleto, redirecionar_para_suporte

async def handler_ted_boleto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler para métodos de pagamento TED/Boleto.
    Redireciona automaticamente para @GhosttP2P.
    """
    await redirecionar_para_ted_boleto(update, context)
    return ConversationHandler.END

async def handler_metodo_pagamento_ted(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler específico para TED.
    """
    await redirecionar_para_ted_boleto(update, context)
    return ConversationHandler.END

async def handler_metodo_pagamento_boleto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler específico para Boleto.
    """
    await redirecionar_para_ted_boleto(update, context)
    return ConversationHandler.END

async def handler_lightning_network(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler para Lightning Network - redirecionamento temporário.
    """
    await redirecionar_para_suporte(update, context, "Lightning Network")
    return ConversationHandler.END
