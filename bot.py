import logging
from config.config import BOT_TOKEN
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from api.depix import pix_api, PixAPIError
from menu.menu_compra import get_conversation_handler, ativar_aguardar_lightning_address
from api.pedido_manager import pedido_manager

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ghostbot")

# Variável global para armazenar a instância do bot
bot_instance = None

async def pix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args or len(context.args) < 2:
            if update.message:
                await update.message.reply_text("Uso: /pix <valor_centavos> <endereco_PIX>")
            return
        valor_centavos = int(context.args[0]) if context.args else 0
        endereco = context.args[1] if context.args else ''
        if update.message:
            await update.message.reply_text("Processando pagamento PIX...")
        result = pix_api.criar_pagamento(valor_centavos, endereco)
        msg = (
            f"Pagamento criado!\n"
            f"QR Code: {result.get('qr_image_url', '')}\n"
            f"Copia e Cola: {result.get('qr_code_text', '')}\n"
            f"ID: {result.get('transaction_id', '')}"
        )
        if update.message:
            await update.message.reply_text(msg)
    except PixAPIError as e:
        if update.message:
            await update.message.reply_text(f"Erro ao criar pagamento PIX: {e}")
    except Exception as e:
        if update.message:
            await update.message.reply_text(f"Erro inesperado: {e}")

async def lightning_callback(user_id: int, pedido_id: int):
    """
    Callback para ativar o estado de aguardar endereço Lightning.
    Esta função será chamada pelo pedido_manager quando o pagamento PIX for confirmado.
    """
    try:
        global bot_instance
        
        if not bot_instance:
            print("❌ [BOT] Instância do bot não disponível")
            return
        
        print(f"🟢 [BOT] Callback Lightning ativado para usuário {user_id}, pedido {pedido_id}")
        
        # Enviar mensagem para o usuário solicitando o endereço Lightning
        await bot_instance.send_message(
            chat_id=user_id,
            text="🎉 **Pagamento PIX Confirmado!**\n\n"
                 "✅ Seu pagamento foi recebido e confirmado!\n\n"
                 "⚡ **Agora envie seu endereço Lightning:**\n\n"
                 "📱 **Formatos aceitos:**\n"
                 "• Lightning Address: `user@domain.com`\n"
                 "• Invoice Lightning: `lnbc...`\n\n"
                 "💡 **Exemplo:** `sua_carteira@walletofsatoshi.com`\n\n"
                 "Envie seu endereço agora:",
            parse_mode='Markdown'
        )
        
        print(f"✅ [BOT] Mensagem de Lightning Address enviada para usuário {user_id}")
        
    except Exception as e:
        print(f"❌ [BOT] Erro no callback Lightning: {e}")

async def ativar_lightning_address_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para ativar o estado de aguardar endereço Lightning.
    Esta função será chamada quando o pagamento PIX for confirmado.
    """
    try:
        # Extrair dados do contexto
        user_id = update.effective_user.id if update.effective_user else None
        pedido_id = context.user_data.get('pedido_id') if context.user_data else None
        if not pedido_id:
            if update.message:
                await update.message.reply_text(
                    "❌ **Erro:** Pedido não encontrado.\n"
                    "Por favor, inicie uma nova compra.",
                    parse_mode='Markdown'
                )
            return
        if user_id is not None:
            print(f"🟢 [BOT] Ativando Lightning Address para usuário {user_id}, pedido {pedido_id}")
            # Ativar o estado de aguardar endereço Lightning
            await ativar_aguardar_lightning_address(context, user_id, pedido_id)
    except Exception as e:
        print(f"❌ [BOT] Erro ao ativar Lightning Address: {e}")
        if update.message:
            await update.message.reply_text(
                f"❌ **Erro inesperado:**\n{str(e)}\n\n"
                f"Entre em contato com o suporte.",
                parse_mode='Markdown'
            )

if __name__ == "__main__":
    logger.info("Iniciando GhostBot...")
    app = Application.builder().token(BOT_TOKEN).build()
    # Armazenar a instância do bot globalmente
    bot_instance = app.bot
    # Configurar o callback do pedido_manager, se disponível
    if hasattr(pedido_manager, 'set_lightning_callback'):
        pedido_manager.set_lightning_callback(lightning_callback)  # type: ignore
    # Adicionar o ConversationHandler do menu de compra
    conversation_handler = get_conversation_handler()
    app.add_handler(conversation_handler)
    # Adicionar handler para PIX
    app.add_handler(CommandHandler("pix", pix))
    # Adicionar handler para ativar Lightning Address
    app.add_handler(CommandHandler("lightning", ativar_lightning_address_handler))
    print("🟢 [BOT] GhostBot iniciado com sucesso!")
    print("🟢 [BOT] ConversationHandler configurado")
    print("🟢 [BOT] Callback de Lightning Address configurado")
    print("🟢 [BOT] Aguardando comandos...")
    app.run_polling()
