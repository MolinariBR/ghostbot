# Importa o módulo de compatibilidade primeiro
import compat  # noqa: F401

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
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

# Inicializa o updater e dispatcher
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher


# Estados da conversa
MENU, COMPRAR, VENDER, SERVICOS, AJUDA, TERMOS = range(6)

# Função para criar o teclado do menu
def menu_principal():
    keyboard = [
        [KeyboardButton("🛒 Comprar"), KeyboardButton("💰 Vender")],
        [KeyboardButton("🔧 Serviços"), KeyboardButton("❓ Ajuda")],
        [KeyboardButton("📜 Termos")]
    ]
    return keyboard

# Configura os menus principais
setup_menus(menu_principal)

# Handlers de comando
def start(update: Update, context: CallbackContext) -> int:
    """Inicia a conversa e mostra o menu principal."""
    reply_markup = ReplyKeyboardMarkup(menu_principal(), resize_keyboard=True)
    update.message.reply_text(
        '👋 Olá! Eu sou o Ghost Bot, seu assistente de criptomoedas.\n\n'
        'Escolha uma opção abaixo:',
        reply_markup=reply_markup
    )
    return MENU

def vender(update: Update, context: CallbackContext) -> int:
    """Lida com a opção de venda."""
    update.message.reply_text(
        "🔹 *VENDER* 🔹\n\n"
        "Por favor, informe o valor em Bitcoin que deseja vender.",
        parse_mode='Markdown'
    )
    return VENDER

def servicos(update: Update, context: CallbackContext) -> int:
    """Mostra os serviços disponíveis."""
    update.message.reply_text(
        "🔹 *SERVIÇOS* 🔹\n\n"
        "• Compra e venda de Bitcoin\n"
        "• Carteira digital segura\n"
        "• Suporte 24/7\n\n"
        "Voltar ao menu: /start",
        parse_mode='Markdown'
    )
    return SERVICOS

def ajuda(update: Update, context: CallbackContext) -> int:
    """Mostra a ajuda."""
    update.message.reply_text(
        "🔹 *AJUDA* 🔹\n\n"
        "Precisa de ajuda? Entre em contato com nosso suporte:\n"
        "📧 suporte@ghostbot.com\n"
        "📞 (11) 99999-9999\n\n"
        "Voltar ao menu: /start",
        parse_mode='Markdown'
    )
    return AJUDA

def termos(update: Update, context: CallbackContext) -> int:
    """Mostra os termos de uso."""
    update.message.reply_text(
        "🔹 *TERMOS DE USO* 🔹\n\n"
        "1. O usuário é responsável por suas transações.\n"
        "2. As taxas são informadas no momento da operação.\n"
        "3. Não nos responsabilizamos por erros em endereços.\n\n"
        "Voltar ao menu: /start",
        parse_mode='Markdown'
    )
    return TERMOS

def main():
    """Inicia o bot."""
    # Adiciona os handlers de comando
    dispatcher.add_handler(CommandHandler('start', start))
    
    # Adiciona os handlers de conversação
    dispatcher.add_handler(get_compra_conversation())
    dispatcher.add_handler(get_venda_conversation())
    
    # Adiciona handlers para os outros menus
    dispatcher.add_handler(MessageHandler(Filters.regex('^🔧 Serviços$'), servicos))
    dispatcher.add_handler(MessageHandler(Filters.regex('^❓ Ajuda$'), ajuda))
    dispatcher.add_handler(MessageHandler(Filters.regex('^📜 Termos$'), termos))
    dispatcher.add_handler(MessageHandler(Filters.regex('^🔙 Voltar$'), start))

    # Inicia o bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
