"""
Handler para notificações de pagamentos completados e botão "Comprar Novamente"
"""
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, CallbackQueryHandler, filters, ContextTypes

logger = logging.getLogger(__name__)

async def comprar_novamente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o botão 'Comprar Novamente'"""
    try:
        # Importa a função de iniciar compra
        from menus.menu_compra import iniciar_compra
        
        # Se for um callback query (botão inline)
        if update.callback_query:
            await update.callback_query.answer("Iniciando nova compra...")
            # Cria um novo update para simular o clique em comprar
            update.message = update.callback_query.message
        
        # Chama a função de iniciar compra
        return await iniciar_compra(update, context)
        
    except Exception as e:
        logger.error(f"Erro no handler comprar_novamente: {e}")
        await update.message.reply_text(
            "❌ Erro ao iniciar nova compra. Use o menu principal.",
            parse_mode='Markdown'
        )

async def enviar_notificacao_lightning_completada(bot, user_id: int, dados_compra: dict):
    """
    Envia notificação quando uma compra Lightning for completada
    
    Args:
        bot: Instância do bot Telegram
        user_id: ID do usuário no Telegram
        dados_compra: Dados da compra completada
    """
    try:
        # Monta a mensagem de agradecimento
        mensagem = f"""🎉 *COMPRA COMPLETADA COM SUCESSO!*

✅ Sua compra Lightning foi processada automaticamente.

💰 *Valor investido:* R$ {dados_compra.get('valor_brl', 0):,.2f}
⚡ *Recebido:* {dados_compra.get('valor_recebido', 0):.8f} BTC
🔗 *Rede:* Lightning Network

🙏 *Obrigado pela compra e confiança!*

Continue investindo com a gente! 👇"""

        # Cria botão inline "Comprar Novamente"
        teclado_inline = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Comprar Novamente", callback_data="comprar_novamente")]
        ])
        
        # Envia a mensagem com o botão
        await bot.send_message(
            chat_id=user_id,
            text=mensagem,
            parse_mode='Markdown',
            reply_markup=teclado_inline
        )
        
        logger.info(f"Notificação Lightning enviada para usuário {user_id}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação Lightning: {e}")

def setup_compra_handlers(application):
    """Configura os handlers relacionados a compras"""
    # Handler para o botão "Comprar Novamente"
    application.add_handler(
        CallbackQueryHandler(comprar_novamente, pattern="^comprar_novamente$")
    )
    
    # Handler para texto "Comprar Novamente" (caso seja enviado como mensagem)
    application.add_handler(
        MessageHandler(filters.Regex('^🛒 Comprar Novamente$'), comprar_novamente)
    )
    
    logger.info("Handlers de compra configurados")
