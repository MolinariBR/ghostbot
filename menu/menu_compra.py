from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

# 1 Passo - Menu de compra

MENU_OPCOES = [['Comprar', 'Vender'], ['Termos', 'Ajuda']]
menu_markup = ReplyKeyboardMarkup(MENU_OPCOES, resize_keyboard=True)

MENU_MOEDAS = [["BTC", "USDT", "DEPIX"], ["Voltar"]]
moedas_markup = ReplyKeyboardMarkup(MENU_MOEDAS, resize_keyboard=True)

async def mostrar_menu_compra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Escolha uma opção:",
        reply_markup=menu_markup
    )
# 2 Passo - Escolher moeda
async def tratar_opcao_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    # Passo 2 - Escolher moeda
    if texto == "Comprar":
        await update.message.reply_text(
            "Selecione a moeda:",
            reply_markup=moedas_markup
        )
        return
    if texto == "Voltar":
        await mostrar_menu_compra(update, context)
        return
    # Passo 3 - Menu de rede
    if texto == "BTC":
        redes_btc = [["Ochain", "Liquid", "Lightning"], ["Voltar"]]
        redes_markup = ReplyKeyboardMarkup(redes_btc, resize_keyboard=True)
        await update.message.reply_text(
            "Selecione a rede para BTC:",
            reply_markup=redes_markup
        )
        return
    if texto == "DEPIX":
        redes_depix = [["Liquid"], ["Voltar"]]
        redes_markup = ReplyKeyboardMarkup(redes_depix, resize_keyboard=True)
        await update.message.reply_text(
            "Selecione a rede para DEPIX:",
            reply_markup=redes_markup
        )
        return
    if texto == "USDT":
        redes_usdt = [["Liquid", "Polygon"], ["Voltar"]]
        redes_markup = ReplyKeyboardMarkup(redes_usdt, resize_keyboard=True)
        await update.message.reply_text(
            "Selecione a rede para USDT:",
            reply_markup=redes_markup
        )
        return
    # Passo 4 - Valor do investimento
    valores_fixos = [["10.00", "25.00", "50.00"], ["250.00", "500.00", "850.00"], ["Voltar"]]
    valores_markup = ReplyKeyboardMarkup(valores_fixos, resize_keyboard=True, one_time_keyboard=True)
    if texto in ["Ochain", "Liquid", "Lightning", "Polygon"]:
        await update.message.reply_text(
            "Informe o valor do investimento ou escolha uma opção:",
            reply_markup=valores_markup
        )
        await update.message.reply_text(
            "Você também pode digitar um valor personalizado (mínimo 10.00, máximo 4999.99)")
        return
    if texto == "Voltar":
        # Volta para o menu de redes
        await update.message.reply_text(
            "Selecione a moeda:",
            reply_markup=moedas_markup
        )
        return
    # Validação do valor personalizado
    try:
        valor = float(texto.replace(",", "."))
        amount_in_cents = int(valor * 100)
        if 1000 <= amount_in_cents <= 499999:
            valor_real = amount_in_cents / 100
            await update.message.reply_text(f"Valor selecionado: {valor_real:.2f}")
            # Passo 5 - Resumo da compra
            id_compra = "123456"  # Gerar/obter ID real no backend
            moeda = context.user_data.get("moeda", "BTC")
            rede = context.user_data.get("rede", "Lightning")
            comissao = 200  # Exemplo em centavos
            parceiro = 100
            cotacao = 25000000  # Exemplo em centavos
            voce_recebe = amount_in_cents - comissao - parceiro
            resumo = (
                f"RESUMO DA COMPRA\n"
                f"ID: {id_compra}\n"
                f"Moeda: {moeda}\n"
                f"Rede: {rede}\n"
                f"Valor: {valor_real:.2f}\n"
                f"Comissão: {comissao/100:.2f}\n"
                f"Parceiro: {parceiro/100:.2f}\n"
                f"Cotação: {cotacao/100:.2f}\n"
                f"Você Recebe: {voce_recebe/100:.2f}"
            )
            await update.message.reply_text(resumo)
            # Passo 6 - Forma de Pagamento
            formas_pagamento = [["PIX", "TED", "BOLETO"], ["Voltar"]]
            pagamento_markup = ReplyKeyboardMarkup(formas_pagamento, resize_keyboard=True)
            await update.message.reply_text(
                "Selecione a forma de pagamento:",
                reply_markup=pagamento_markup
            )
            return
        elif amount_in_cents < 1000:
            await update.message.reply_text("Valor mínimo permitido é 1000 centavos (10.00)")
            return
        elif amount_in_cents > 499999:
            await update.message.reply_text(
                "Para compras acima do limite máximo, fale diretamente com nosso atendente: @GhosttP2P_bot"
            )
            return
    except ValueError:
        pass
    # Passo 6 - Forma de Pagamento
    if texto == "TED" or texto == "BOLETO":
        await update.message.reply_text(
            "Para pagamentos via TED ou BOLETO, fale diretamente com nosso atendente: @GhosttP2P_bot"
        )
        return
    if texto == "PIX":
        await update.message.reply_text(
            "Pagamento via PIX selecionado! Aguarde instruções para finalizar."
        )
        # Aqui pode seguir para o fluxo PIX
        return
    if texto == "Voltar":
        # Volta para o resumo da compra
        # Recomenda-se reexibir o resumo e o menu de pagamento
        formas_pagamento = [["PIX", "TED", "BOLETO"], ["Voltar"]]
        pagamento_markup = ReplyKeyboardMarkup(formas_pagamento, resize_keyboard=True)
        await update.message.reply_text(
            "Selecione a forma de pagamento:",
            reply_markup=pagamento_markup
        )
        return
