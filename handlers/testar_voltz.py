from telegram import Update
from telegram.ext import ContextTypes

# Importe a função de saque Voltz real do seu projeto
from menus.menu_compra import processar_metodo_pagamento

async def testar_voltz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando de teste para simular um pagamento confirmado e acionar o fluxo Voltz sem pagar o PIX.
    Só use em ambiente de desenvolvimento!

    # ATENÇÃO: Este trecho é para testes e deve ser REMOVIDO em produção!
    """
    # Preenche dados simulados
    context.user_data.update({
        "moeda": "BTC",
        "rede": "Lightning",
        "valor_brl": 50.0,
        "cotacao": 300000.0,
        "endereco_recebimento": "voltzapi@tria.com"
    })
    # Simula escolha do método de pagamento
    update.message.text = "💠 PIX"
    await processar_metodo_pagamento(update, context)
    await update.message.reply_text("[DEBUG] Fluxo Voltz testado sem pagamento real.")
