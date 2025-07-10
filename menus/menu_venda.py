from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import MessageHandler, ConversationHandler, CommandHandler, filters
from telegram.ext import ContextTypes

# 🚀 NOVA INTEGRAÇÃO: Sistema de Redirecionamentos
from limites.redirecionamentos import redirecionar_para_venda

# Variável para armazenar a função do menu principal
menu_principal_func = None

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

async def iniciar_venda(update: Update, context) -> int:
    """Inicia o fluxo de venda redirecionando para @GhosttP2P."""
    # � REDIRECIONAMENTO AUTOMÁTICO: Todas as vendas vão para @GhosttP2P
    await redirecionar_para_venda(update, context)
    return ConversationHandler.END

async def escolher_moeda_venda(update: Update, context) -> int:
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

async def processar_quantidade_venda(update: Update, context) -> int:
    """Processa a quantidade informada e pede o endereço de saque."""
    if update.message.text == "🔙 Voltar":
        return await iniciar_venda(update, context)
    try:
        quantidade = float(update.message.text.replace(',', '.'))
        if quantidade <= 0:
            raise ValueError("Quantidade inválida")
        
        # 🚀 NOVA INTEGRAÇÃO: Validação de Limites PIX para Venda
        # Assumindo que o valor é em BRL para validação dos limites
        validacao = LimitesValor.validar_pix_venda(quantidade)
        if not validacao['valido']:
            await update.message.reply_text(
                f"❌ {validacao['mensagem']}\n\n"
                f"💡 {validacao['dica']}\n\n"
                "💰 Digite a quantidade que deseja vender:",
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Voltar")]], resize_keyboard=True)
            )
            return QUANTIDADE
        
        moeda = context.user_data.get('moeda_venda', '')
        # Arredondamento conforme moeda
        if "BTC" in moeda.upper():
            quantidade = round(quantidade, 8)
        else:
            quantidade = round(quantidade, 2)
        context.user_data['quantidade_venda'] = quantidade
        await update.message.reply_text(
            "📭 Agora, envie o endereço da carteira para receber os fundos:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Voltar")]], resize_keyboard=True)
        )
        return ENDERECO
    except ValueError:
        await update.message.reply_text(
            "⚠️ Quantidade inválida! Por favor, digite um valor numérico maior que zero.",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Voltar")]], resize_keyboard=True)
        )
        return QUANTIDADE

async def processar_endereco(update: Update, context) -> int:
    """Processa o endereço e mostra a confirmação."""
    if update.message.text == "🔙 Voltar":
        return await iniciar_venda(update, context)
    endereco = update.message.text
    context.user_data['endereco'] = endereco
    moeda = context.user_data.get('moeda_venda', 'a moeda selecionada')
    quantidade = context.user_data.get('quantidade_venda', 0)
    mensagem = (
        f"📝 *Confirme os dados da venda:*\n\n"
        f"• *Moeda:* {moeda}\n"
        f"• *Quantidade:* {quantidade}\n"
        f"• *Endereço:* `{endereco}`\n\n"
        "Deseja confirmar a venda?"
    )
    keyboard = [
        [KeyboardButton("✅ Confirmar Venda"), KeyboardButton("🔙 Cancelar")],
        [KeyboardButton("🔙 Voltar")]
    ]
    await update.message.reply_text(
        mensagem,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CONFIRMAR

async def confirmar_venda(update: Update, context) -> int:
    """Confirma a venda e finaliza o processo."""
    moeda = context.user_data.get('moeda_venda', 'a moeda selecionada')
    quantidade = context.user_data.get('quantidade_venda', 0)
    endereco = context.user_data.get('endereco', 'não informado')
    mensagem = (
        "✅ *Venda processada com sucesso!*\n\n"
        f"• *Moeda:* {moeda}\n"
        f"• *Quantidade:* {quantidade}\n"
        f"• *Endereço:* `{endereco}`\n\n"
        "Obrigado por utilizar nossos serviços!"
    )
    await update.message.reply_text(
        mensagem,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(menu_principal_func(), resize_keyboard=True) if menu_principal_func else None
    )
    context.user_data.clear()
    return -1  # ConversationHandler.END

async def cancelar_venda(update: Update, context) -> int:
    """Cancela a venda e volta ao menu principal."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Venda cancelada.",
        reply_markup=ReplyKeyboardMarkup(menu_principal_func(), resize_keyboard=True) if menu_principal_func else None
    )
    return -1  # ConversationHandler.END

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
    global menu_principal_func
    menu_principal_func = menu_func
    def menu_principal():
        return menu_func()
    return menu_principal
