import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Importa as configurações do tokens.py
from tokens import Config

# Importa os menus
from menus import setup_menus, get_compra_conversation, get_venda_conversation

# Configuração do logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token do bot
TOKEN = Config.TELEGRAM_BOT_TOKEN

# Estados da conversa
MENU, COMPRAR, VENDER, SERVICOS, AJUDA, TERMOS = range(6)

# Função para criar o teclado do menu
def menu_principal():
    keyboard = [
        [KeyboardButton("🛒 Comprar"), KeyboardButton("💰 Vender")],
        [KeyboardButton("🔧 Serviços"), KeyboardButton("❓ Ajuda")],
        [KeyboardButton("📜 Termos")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Configura os menus principais
setup_menus(menu_principal)

# Handlers de comando
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa e mostra o menu principal."""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Olá {user.first_name}!\n"
        "Bem-vindo ao Ghost Bot - Seu assistente de negociação de criptomoedas.\n\n"
        "Selecione uma opção abaixo:",
        reply_markup=menu_principal()
    )
    return MENU

async def vender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lida com a opção de venda."""
    await update.message.reply_text(
        "🔹 *VENDER* 🔹\n\n"
        "Por favor, informe o valor em Bitcoin que deseja vender.",
        parse_mode='Markdown'
    )
    return VENDER

async def servicos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra os serviços disponíveis."""
    await update.message.reply_text(
        "🔹 *SERVIÇOS* 🔹\n\n"
        "• Compra e venda de Bitcoin\n"
        "• Carteira digital segura\n"
        "• Suporte 24/7\n\n"
        "Voltar ao menu: /start",
        parse_mode='Markdown'
    )
    return SERVICOS

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra a ajuda."""
    await update.message.reply_text(
        "🔹 *AJUDA* 🔹\n\n"
        "Precisa de ajuda? Entre em contato com nosso suporte:\n"
        "📧 suporte@ghostbot.com\n"
        "📞 (11) 99999-9999\n\n"
        "Voltar ao menu: /start",
        parse_mode='Markdown'
    )
    return AJUDA

async def termos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra os termos de uso."""
    await update.message.reply_text(
        "🔹 *TERMOS DE USO* 🔹\n\n"
        "1. O usuário é responsável por suas transações.\n"
        "2. As taxas são informadas no momento da operação.\n"
        "3. Não nos responsabilizamos por erros em endereços.\n\n"
        "Voltar ao menu: /start",
        parse_mode='Markdown'
    )
    return TERMOS

def main() -> None:
    """Inicia o bot."""
    # Cria a aplicação
    application = Application.builder().token(TOKEN).build()

    # Adiciona os handlers de conversação
    application.add_handler(CommandHandler('start', start))
    
    # Adiciona os handlers de conversação
    application.add_handler(get_compra_conversation())
    application.add_handler(get_venda_conversation())
    
    # Adiciona handlers para os outros menus
    application.add_handler(MessageHandler(filters.Regex('^🔧 Serviços$'), servicos))
    application.add_handler(MessageHandler(filters.Regex('^❓ Ajuda$'), ajuda))
    application.add_handler(MessageHandler(filters.Regex('^📜 Termos$'), termos))
    application.add_handler(MessageHandler(filters.Regex('^🔙 Voltar$'), start))

    # Inicia o bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
