import logging
import asyncio
from config.config import BOT_TOKEN
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ApplicationHandlerStop
from api.depix import pix_api, PixAPIError
from menu.menu_compra import get_conversation_handler, ativar_aguardar_lightning_address
from api.pedido_manager import pedido_manager
from menu.menu_compra import registrar_handlers_globais  # <-- Importação adicionada
from core.session_manager import session_manager, get_user_data, set_user_data, clear_user_data
from core.rate_limiter import rate_limiter, rate_limit
from core.state_validator import state_validator
from core.async_queue import async_queue, QueueTask

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ghostbot")

# Variável global para armazenar a instância do bot
bot_instance = None

async def safe_send_message(bot, chat_id: int, text: str, parse_mode: str | None = None, max_retries: int = 3, delay: float = 1.0):
    """
    Envia mensagem com retry automático em caso de erro de rede.
    
    Args:
        bot: Instância do bot do Telegram
        chat_id: ID do chat para enviar a mensagem
        text: Texto da mensagem
        parse_mode: Modo de parsing (Markdown, HTML, etc.)
        max_retries: Número máximo de tentativas
        delay: Delay entre tentativas em segundos
    
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    for attempt in range(max_retries):
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
            
        except Exception as e:
            error_msg = str(e)
            
            # Se for erro de rede, tentar novamente
            if any(network_error in error_msg.lower() for network_error in [
                'networkerror', 'httpx', 'readerror', 'timeout', 'connection'
            ]):
                logger.warning(f"🔄 Tentativa {attempt + 1}/{max_retries} falhou (erro de rede): {error_msg}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (attempt + 1))  # Backoff exponencial
                    continue
                else:
                    logger.error(f"❌ Falha ao enviar mensagem após {max_retries} tentativas: {error_msg}")
                    return False
            
            # Se for outro tipo de erro, não tentar novamente
            else:
                logger.error(f"❌ Erro ao enviar mensagem: {error_msg}")
                return False
    
    return False

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler global para tratar erros do bot.
    """
    try:
        # Log do erro
        logger.error(f"⚠️ Erro no bot: {context.error}")
        
        # Se for um erro de rede, apenas logar (o bot vai tentar novamente automaticamente)
        if "NetworkError" in str(context.error) or "httpx" in str(context.error):
            logger.warning(f"🔄 Erro de rede detectado, tentando novamente: {context.error}")
            return
        
        # Para outros erros, tentar enviar mensagem de erro para o usuário
        try:
            # Verificar se é um Update válido e tem chat usando getattr para evitar erros de tipo
            effective_chat = getattr(update, 'effective_chat', None) if update else None
            if effective_chat and hasattr(effective_chat, 'id'):
                await safe_send_message(
                    context.bot,
                    effective_chat.id,
                    "❌ **Erro inesperado ocorreu**\n\n"
                    "🔧 Nossa equipe foi notificada.\n"
                    "🔄 Tente novamente em alguns segundos.\n\n"
                    "💬 Se o problema persistir, entre em contato com o suporte.",
                    parse_mode='Markdown'
                )
        except Exception as send_error:
            logger.error(f"❌ Erro ao enviar mensagem de erro: {send_error}")
        
    except Exception as e:
        logger.error(f"❌ Erro no error_handler: {e}")

@rate_limit(max_requests=5, window_seconds=60, action="pix")
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
            logger.error("❌ [BOT] Instância do bot não disponível")
            return
        
        logger.info(f"🟢 [BOT] Callback Lightning ativado para usuário {user_id}, pedido {pedido_id}")
        
        # Enviar mensagem para o usuário solicitando o endereço Lightning com retry
        success = await safe_send_message(
            bot_instance,
            user_id,
            "🎉 **Pagamento PIX Confirmado!**\n\n"
                 "✅ Seu pagamento foi recebido e confirmado!\n\n"
                 "⚡ **Agora envie seu endereço Lightning:**\n\n"
                 "📱 **Formatos aceitos:**\n"
                 "• Lightning Address: `user@domain.com`\n"
                 "• Invoice Lightning: `lnbc...`\n\n"
                 "💡 **Exemplo:** `sua_carteira@walletofsatoshi.com`\n\n"
                 "Envie seu endereço agora:",
            parse_mode='Markdown'
        )
        
        if success:
            logger.info(f"✅ [BOT] Mensagem de Lightning Address enviada para usuário {user_id}")
        else:
            logger.error(f"❌ [BOT] Falha ao enviar mensagem de Lightning Address para usuário {user_id}")
        
    except Exception as e:
        logger.error(f"❌ [BOT] Erro no callback Lightning: {e}")

@rate_limit(max_requests=3, window_seconds=60, action="lightning")
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
            logger.info(f"🟢 [BOT] Ativando Lightning Address para usuário {user_id}, pedido {pedido_id}")
            # Ativar o estado de aguardar endereço Lightning
            await ativar_aguardar_lightning_address(context.bot, user_id, pedido_id)
    except Exception as e:
        logger.error(f"❌ [BOT] Erro ao ativar Lightning Address: {e}")
        if update.message:
            await update.message.reply_text(
                f"❌ **Erro inesperado:**\n{str(e)}\n\n"
                f"Entre em contato com o suporte.",
                parse_mode='Markdown'
            )

# Registrar handler de teste na fila
async def eco_handler(dados, usuario_id):
    import asyncio
    await asyncio.sleep(1)  # Simula processamento
    return f"Eco: {dados.get('texto', '')}"
async_queue.register_handler('eco', eco_handler)

# Handler do comando /fila para testar a fila
async def fila_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else None
    texto = ' '.join(context.args) if context.args else 'teste'
    if update.message:
        await update.message.reply_text(f"Tarefa enviada para a fila! Aguarde a resposta...")
    if user_id is None:
        return  # Não é possível responder
    # Adiciona tarefa na fila
    task_id = await async_queue.add_task('eco', {'texto': texto}, str(user_id))
    # Polling para aguardar conclusão (máx 10s)
    for _ in range(50):
        task = await async_queue.get_task_status(task_id)
        if task and task.status == task.status.CONCLUIDA:
            # Envia resposta ao usuário
            await context.bot.send_message(chat_id=user_id, text=f"Resultado da fila: {task.resultado}")
            break
        await asyncio.sleep(0.2)
    else:
        await context.bot.send_message(chat_id=user_id, text="Tarefa demorou demais na fila!")

if __name__ == "__main__":
    logger.info("Iniciando GhostBot...")
    # Configuração padrão do cliente HTTP (mais compatível)
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ Cliente HTTP configurado com configuração padrão")
    except Exception as e:
        logger.error(f"❌ Erro ao configurar cliente HTTP: {e}")
        app = Application.builder().token(BOT_TOKEN).build()
        logger.warning("⚠️ Usando configuração padrão do cliente HTTP")
    bot_instance = app.bot
    app.add_error_handler(error_handler)
    logger.info("✅ Error handler global configurado")
    logger.info("✅ SessionManager inicializado")
    logger.info("✅ RateLimiter inicializado")
    logger.info("✅ StateValidator inicializado")
    async def watchdog():
        while True:
            logger.info("⏳ Watchdog: loop ativo")
            await asyncio.sleep(60)
    loop = asyncio.get_event_loop()
    loop.create_task(watchdog())
    logger.info("✅ Watchdog iniciado")
    if hasattr(pedido_manager, 'set_lightning_callback'):
        pedido_manager.set_lightning_callback(lightning_callback)  # type: ignore
    conversation_handler = get_conversation_handler()
    app.add_handler(conversation_handler)
    app.add_handler(CommandHandler("pix", pix))
    app.add_handler(CommandHandler("lightning", ativar_lightning_address_handler))
    app.add_handler(CommandHandler("fila", fila_handler))
    registrar_handlers_globais(app)
    # Inicializar a fila assíncrona ANTES do polling
    loop.run_until_complete(async_queue.start())
    logger.info("✅ AsyncQueue inicializada e workers rodando")
    logger.info("🟢 [BOT] GhostBot iniciado com sucesso!")
    logger.info("🟢 [BOT] Cliente HTTP configurado com configuração padrão")
    logger.info("🟢 [BOT] Error handler global configurado")
    logger.info("🟢 [BOT] ConversationHandler configurado")
    logger.info("🟢 [BOT] Callback de Lightning Address configurado")
    logger.info("🟢 [BOT] Handler global Lightning registrado")
    logger.info("🟢 [BOT] Aguardando comandos...")
    try:
        app.run_polling(
            poll_interval=1.0,
            timeout=30,
            bootstrap_retries=5
        )
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal no polling: {e}")
    finally:
        loop.run_until_complete(async_queue.stop())
        logger.info("🧹 AsyncQueue parada e recursos limpos")
        logger.info("🧹 Recursos limpos")
