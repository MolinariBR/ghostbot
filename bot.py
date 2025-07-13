import logging
from config.config import BOT_TOKEN
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from api.depix import pix_api, PixAPIError
from menu.menu_compra import mostrar_menu_compra, tratar_opcao_menu

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ghostbot")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu_compra(update, context)

async def pix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 2:
            await update.message.reply_text("Uso: /pix <valor_centavos> <endereco_PIX>")
            return
        valor_centavos = int(context.args[0])
        endereco = context.args[1]
        await update.message.reply_text("Processando pagamento PIX...")
        result = pix_api.criar_pagamento(valor_centavos, endereco)
        msg = (
            f"Pagamento criado!\n"
            f"QR Code: {result['qr_image_url']}\n"
            f"Copia e Cola: {result['qr_code_text']}\n"
            f"ID: {result['transaction_id']}"
        )
        await update.message.reply_text(msg)
    except PixAPIError as e:
        await update.message.reply_text(f"Erro ao criar pagamento PIX: {e}")
    except Exception as e:
        await update.message.reply_text(f"Erro inesperado: {e}")

if __name__ == "__main__":
    logger.info("Iniciando GhostBot...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pix", pix))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tratar_opcao_menu))
    app.run_polling()
