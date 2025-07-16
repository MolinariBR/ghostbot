from telegram import Update
from telegram.ext import ContextTypes

async def tratar_menu_venda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Para vender, fale diretamente com nosso atendente: @GhosttP2P_bot"
        )
