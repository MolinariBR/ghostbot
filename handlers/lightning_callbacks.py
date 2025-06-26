"""
Handler para callbacks do sistema Lightning
"""
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from menus.menu_compra import iniciar_compra

logger = logging.getLogger(__name__)

async def handle_comprar_novamente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para o botão 'Comprar Novamente'
    """
    try:
        query = update.callback_query
        await query.answer()
        
        # Edita a mensagem para confirmar
        await query.edit_message_text(
            text="🛒 **Iniciando nova compra...**\n\n"
                 "Você será redirecionado para o menu de compra.",
            parse_mode='Markdown'
        )
        
        # Chama a função de iniciar compra
        # Como não temos update.message, vamos criar um contexto apropriado
        # Envia nova mensagem com o menu de compra
        await iniciar_compra(update, context)
        
        logger.info(f"Usuário {query.from_user.id} iniciou nova compra via botão")
        
    except Exception as e:
        logger.error(f"Erro no handler comprar_novamente: {e}")
        try:
            await update.callback_query.answer("❌ Erro ao iniciar nova compra. Use /start")
        except:
            pass

# Handler para registrar no bot
comprar_novamente_handler = CallbackQueryHandler(
    handle_comprar_novamente, 
    pattern="^comprar_novamente$"
)
