from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters, ConversationHandler, CommandHandler

# Estados do menu de venda
ESCOLHER_MOEDA, QUANTIDADE, ENDERECO, CONFIRMAR = range(4)

def menu_moedas_venda():
    """Retorna o teclado com as opções de moedas para venda."""
    keyboard = [
        [KeyboardButton("₿ Vender Bitcoin (BTC)")],
        [KeyboardButton("💵 Vender Tether (USDT)")],
        [KeyboardButton("💠 Vender Depix")],
        [KeyboardButton("🔙 Voltar")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def iniciar_venda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o fluxo de venda mostrando as moedas disponíveis."""
    await update.message.reply_text(
        "💱 *ESCOLHA A MOEDA PARA VENDA*\n\n"
        "Selecione uma das opções abaixo:",
        reply_markup=menu_moedas_venda(),
        parse_mode='Markdown'
    )
    return ESCOLHER_MOEDA

async def escolher_moeda_venda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a escolha da moeda e pede a quantidade."""
    if update.message.text == "🔙 Voltar":
        return await cancelar_venda(update, context)
        
    moeda = update.message.text
    context.user_data['moeda_venda'] = moeda
    
    await update.message.reply_text(
        f"💵 *{moeda}*\n\n"
        "💰 Digite a quantidade que deseja vender:",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Voltar")]], resize_keyboard=True)
    )
    return QUANTIDADE

async def processar_quantidade_venda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a quantidade informada e pede o endereço de saque."""
    if update.message.text == "🔙 Voltar":
        return await iniciar_venda(update, context)
        
    try:
        quantidade = float(update.message.text.replace(',', '.'))
        if quantidade <= 0:
            raise ValueError("Quantidade inválida")
            
        context.user_data['quantidade'] = quantidade
        
        await update.message.reply_text(
            "📤 *ENDEREÇO DE SAQUE*\n\n"
            "Por favor, informe o endereço para onde deseja receber os fundos:",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Voltar")]], resize_keyboard=True)
        )
        return ENDERECO
        
    except (ValueError, TypeError):
        await update.message.reply_text(
            "❌ Quantidade inválida. Por favor, digite um número válido maior que zero."
        )
        return QUANTIDADE

async def processar_endereco(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa o endereço e mostra a confirmação."""
    if update.message.text == "🔙 Voltar":
        return await iniciar_venda(update, context)
        
    endereco = update.message.text
    context.user_data['endereco'] = endereco
    
    moeda = context.user_data.get('moeda_venda', 'a moeda selecionada')
    quantidade = context.user_data.get('quantidade', 0)
    
    # Aqui você pode adicionar a lógica para calcular o valor em BRL
    # Por enquanto, vamos apenas mostrar os dados informados
    
    keyboard = [
        [KeyboardButton("✅ Confirmar Venda")],
        [KeyboardButton("🔙 Cancelar")]
    ]
    
    await update.message.reply_text(
        "📋 *RESUMO DA VENDA*\n\n"
        f"• Moeda: {moeda}\n"
        f"• Quantidade: {quantidade:.8f}\n"
        f"• Endereço: `{endereco}`\n\n"
        "Confirma a venda?",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CONFIRMAR

async def confirmar_venda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirma a venda e finaliza o processo."""
    moeda = context.user_data.get('moeda_venda', 'a moeda selecionada')
    quantidade = context.user_data.get('quantidade', 0)
    endereco = context.user_data.get('endereco', 'não informado')
    
    # Aqui você pode adicionar a lógica para processar a venda
    # Por enquanto, apenas confirmamos
    
    await update.message.reply_text(
        "✅ *VENDA REALIZADA COM SUCESSO!*\n\n"
        f"• Moeda: {moeda}\n"
        f"• Quantidade: {quantidade:.8f}\n"
        f"• Endereço: `{endereco}`\n\n"
        "Os fundos serão processados e enviados em breve.\n"
        "Obrigado por utilizar nossos serviços!",
        parse_mode='Markdown',
        reply_markup=menu_principal()
    )
    
    # Limpa os dados temporários
    context.user_data.clear()
    return ConversationHandler.END

async def cancelar_venda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela a venda e volta ao menu principal."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Venda cancelada.",
        reply_markup=menu_principal()
    )
    return ConversationHandler.END

def get_venda_conversation():
    """Retorna o ConversationHandler para o fluxo de venda."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^💰 Vender$'), iniciar_venda)],
        states={
            ESCOLHER_MOEDA: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), cancelar_venda),
                MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_moeda_venda)
            ],
            QUANTIDADE: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), iniciar_venda),
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_quantidade_venda)
            ],
            ENDERECO: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), iniciar_venda),
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_endereco)
            ],
            CONFIRMAR: [
                MessageHandler(filters.Regex('^✅ Confirmar Venda$'), confirmar_venda),
                MessageHandler(filters.Regex('^🔙 Cancelar$'), cancelar_venda)
            ]
        },
        fallbacks=[
            CommandHandler('start', cancelar_venda),
            MessageHandler(filters.Regex('^/cancelar$'), cancelar_venda)
        ],
        name="venda_conversation"
    )

# Importação circular resolvida com uma função
def set_menu_principal(menu_func):
    global menu_principal
    menu_principal = menu_func
