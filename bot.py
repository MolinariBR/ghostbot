#!/usr/bin/env python3
"""
Bot principal do Ghost Bot - Assistente de Criptomoedas
"""
import sys

# Verifica a versão do Python
if sys.version_info < (3, 8):
    sys.exit("Erro: Python 3.8 ou superior é necessário para executar este bot.")

import asyncio
import logging
import os
import random
import signal
from datetime import datetime
from pathlib import Path

# Configura o path para incluir o diretório raiz
sys.path.insert(0, str(Path(__file__).parent.resolve()))

# Configura manipuladores de sinal para encerramento gracioso
import signal

def handle_termination_signal(signum, frame):
    """Manipulador de sinal para encerramento gracioso."""
    logger.info(f"Recebido sinal {signum}. Encerrando graciosamente...")
    sys.exit(0)

# Configura os sinais para encerramento gracioso
for sig in (signal.SIGINT, signal.SIGTERM):
    try:
        signal.signal(sig, handle_termination_signal)
    except AttributeError:
        # Windows não suporta todos os sinais
        pass

# Configuração de logging
from logging.handlers import RotatingFileHandler

# Importações do Telegram
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)
from telegram.request import HTTPXRequest
from telegram.constants import ParseMode
from telegram.error import (
    NetworkError, 
    TelegramError, 
    RetryAfter, 
    TimedOut, 
    ChatMigrated, 
    Conflict,
    BadRequest,
    Forbidden,
    BadRequest
)

# Importações locais
from tokens import Config
from config import BotConfig, LogConfig
from menus import setup_menus, get_compra_conversation, get_venda_conversation
from menus.menu_compra import iniciar_compra

def setup_logging():
    """
    Configura o sistema de logging com handlers para console e arquivo.
    
    Returns:
        logging.Logger: Instância do logger configurado.
    """
    # Cria o diretório de logs se não existir
    try:
        LogConfig.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Erro ao criar diretório de logs: {e}")
        # Usa um diretório temporário se não for possível criar o diretório de logs
        import tempfile
        temp_log_dir = Path(tempfile.gettempdir()) / "ghost_bot_logs"
        temp_log_dir.mkdir(exist_ok=True)
        LogConfig.LOG_FILE = temp_log_dir / "bot.log"
    
    # Define o formato do log
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configura o logger raiz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LogConfig.LOG_LEVEL))
    
    # Remove handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Configura o handler para arquivo
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            LogConfig.LOG_FILE,
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Erro ao configurar o handler de arquivo: {e}")
    
    # Configura o handler para console
    try:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
    except Exception as e:
        print(f"Erro ao configurar o handler de console: {e}")
    
    # Configura o nível de log para bibliotecas específicas
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.INFO)
    
    return logger

# Configura o logger
try:
    logger = setup_logging()
    logger.info("Logging configurado com sucesso.")
except Exception as e:
    # Se tudo mais falhar, usa um logger básico
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Erro ao configurar o logger: {e}", exc_info=True)

# Estados da conversa
MENU, COMPRAR, VENDER, SERVICOS, AJUDA, TERMOS = range(6)

# Inicialização do bot
def init_bot():
    """
    Inicializa e retorna a aplicação do bot com configurações otimizadas.
    
    Returns:
        Application: Instância da aplicação do bot configurada.
        
    Raises:
        telegram.error.InvalidToken: Se o token do bot for inválido.
        Exception: Se ocorrer um erro durante a inicialização.
    """
    logger.info("Inicializando o bot com configurações personalizadas...")
    
    try:
        # Verifica se o token está configurado
        if not hasattr(Config, 'TELEGRAM_BOT_TOKEN') or not Config.TELEGRAM_BOT_TOKEN:
            raise ValueError("Token do bot não configurado. Verifique o arquivo de configuração.")
        
        # Configuração do cliente HTTP personalizado com opções avançadas
        logger.debug("Configurando cliente HTTP personalizado...")
        request = HTTPXRequest(
            connection_pool_size=BotConfig.POOL_SIZE,
            read_timeout=BotConfig.READ_TIMEOUT,
            connect_timeout=BotConfig.CONNECTION_TIMEOUT,
            write_timeout=BotConfig.WRITE_TIMEOUT,
            pool_timeout=BotConfig.POOL_TIMEOUT,
            http_version='1.1'
        )
        
        logger.debug("Criando instância da aplicação...")
        # Cria e configura a aplicação com a instância personalizada de request
        # Os timeouts já foram configurados no HTTPXRequest
        application = (
            Application.builder()
            .token(Config.TELEGRAM_BOT_TOKEN)
            .request(request)  # Usa a instância personalizada com configurações
            .build()
        )
        
        logger.info("Aplicação do bot inicializada com sucesso.")
        return application
        
    except Exception as e:
        logger.critical(f"Falha ao inicializar o bot: {str(e)}", exc_info=True)
        raise

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

# Utilitários para manipulação de erros
def error_handler(handler):
    """Decorator para tratamento de erros em handlers."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await handler(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Erro no handler {handler.__name__}: {str(e)}", exc_info=True)
            try:
                if update and update.effective_message:
                    await update.effective_message.reply_text(
                        "❌ Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde."
                    )
            except Exception as send_error:
                logger.error(f"Erro ao enviar mensagem de erro: {send_error}")
            return ConversationHandler.END
    return wrapper

# Handlers de comando
@error_handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Inicia a conversa e mostra o menu principal.
    
    Args:
        update: Objeto Update do Telegram.
        context: Contexto da conversa.
        
    Returns:
        int: Próximo estado da conversa (MENU).
    """
    mensagem = '👋 Olá! Eu sou o Ghost Bot, seu assistente de criptomoedas.\n\nEscolha uma opção abaixo:'
    
    try:
        # Tenta obter o teclado principal
        teclado_principal = menu_principal()
        reply_markup = ReplyKeyboardMarkup(teclado_principal, resize_keyboard=True)
        
        # Tenta enviar apenas a mensagem de texto primeiro para garantir que o usuário veja algo
        try:
            await update.message.reply_text(
                mensagem,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as text_error:
            logger.error(f"Erro ao enviar mensagem de texto: {str(text_error)}")
            # Se falhar, tenta novamente sem formatação
            try:
                await update.message.reply_text(
                    "👋 Olá! Eu sou o Ghost Bot, seu assistente de criptomoedas.\n\nEscolha uma opção abaixo:",
                    reply_markup=reply_markup
                )
            except Exception as fallback_error:
                logger.error(f"Erro ao enviar mensagem de fallback: {str(fallback_error)}")
                # Se ainda assim falhar, tenta enviar sem teclado
                try:
                    await update.message.reply_text(
                        "👋 Olá! Por favor, use o comando /start novamente."
                    )
                except Exception as final_error:
                    logger.error(f"Erro crítico ao enviar mensagem: {str(final_error)}")
                return MENU
        
        # Tenta enviar a imagem separadamente para não bloquear a experiência do usuário
        try:
            imagem_path = os.path.join('images', 'ghostp2p.jpg')
            if os.path.exists(imagem_path):
                # Usa uma tarefa assíncrona para não bloquear
                asyncio.create_task(
                    _enviar_imagem_boas_vindas(update, context, imagem_path)
                )
        except Exception as img_error:
            logger.error(f"Erro ao tentar enviar imagem de boas-vindas: {str(img_error)}")
        
        return MENU
    except Exception as e:
        logger.error(f"Erro crítico no handler start: {str(e)}", exc_info=True)
        return MENU

async def _enviar_imagem_boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE, imagem_path: str):
    """
    Função auxiliar para enviar a imagem de boas-vindas de forma assíncrona.
    
    Args:
        update: Objeto Update do Telegram.
        context: Contexto da conversa.
        imagem_path: Caminho para a imagem.
    """
    try:
        with open(imagem_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption="👻 *Ghost Bot* - Seu assistente de criptomoedas",
                parse_mode='Markdown',
                reply_to_message_id=update.effective_message.message_id
            )
    except Exception as e:
        logger.error(f"Erro ao enviar imagem de boas-vindas: {str(e)}", exc_info=True)

@error_handler
async def vender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Lida com a opção de venda.
    
    Args:
        update: Objeto Update do Telegram.
        context: Contexto da conversa.
        
    Returns:
        int: Próximo estado da conversa (VENDER).
    """
    try:
        await update.message.reply_text(
            "🔹 *VENDER* 🔹\n\n"
            "Por favor, informe o valor em Bitcoin que deseja vender.",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([['🔙 Voltar']], resize_keyboard=True)
        )
        return VENDER
    except Exception as e:
        logger.error(f"Erro no handler vender: {str(e)}", exc_info=True)
        raise

@error_handler
async def servicos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Mostra os serviços disponíveis.
    
    Args:
        update: Objeto Update do Telegram.
        context: Contexto da conversa.
        
    Returns:
        int: Próximo estado da conversa (SERVICOS).
    """
    try:
        await update.message.reply_text(
            "🔧 *SERVIÇOS* 🔧\n\n"
            "Aqui estão os serviços disponíveis:\n\n"
            "• Compra e venda de criptomoedas\n"
            "• Carteira digital segura\n"
            "• Conversão entre criptomoedas",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([['🔙 Voltar']], resize_keyboard=True)
        )
        return SERVICOS
    except Exception as e:
        logger.error(f"Erro no handler servicos: {str(e)}", exc_info=True)
        raise

@error_handler
async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Mostra a ajuda e instruções de uso.
    
    Args:
        update: Objeto Update do Telegram.
        context: Contexto da conversa.
        
    Returns:
        int: Próximo estado da conversa (AJUDA).
    """
    try:
        # Importa a função obter_ajuda do módulo ajuda
        from ajuda import obter_ajuda
        
        # Obtém o texto de ajuda formatado
        ajuda_texto = obter_ajuda()
        
        # Cria o teclado com o botão de voltar
        teclado_voltar = [["🔙 Voltar"]]
        
        # Envia a mensagem com as informações de ajuda
        await update.message.reply_text(
            ajuda_texto,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(teclado_voltar, resize_keyboard=True),
            disable_web_page_preview=True
        )
        return AJUDA
    except ImportError as e:
        logger.error(f"Erro ao importar módulo ajuda: {str(e)}", exc_info=True)
        mensagem_erro = (
            "❌ *Erro ao carregar as informações de ajuda.*\n\n"
            "Desculpe, não foi possível carregar as informações de ajuda no momento. "
            "Por favor, tente novamente mais tarde."
        )
    except Exception as e:
        logger.error(f"Erro no handler ajuda: {str(e)}", exc_info=True)
        mensagem_erro = (
            "❌ *Ocorreu um erro ao carregar a ajuda.*\n\n"
            "Nossa central de ajuda está temporariamente indisponível. "
            "Por favor, tente novamente mais tarde."
        )
    
    # Se chegou aqui, houve um erro
    try:
        await update.message.reply_text(
            mensagem_erro,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([['🔙 Voltar']], resize_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Falha ao enviar mensagem de erro: {str(e)}", exc_info=True)
    
    return AJUDA

@error_handler
async def termos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Mostra os termos de uso e política de privacidade.
    
    Args:
        update: Objeto Update do Telegram.
        context: Contexto da conversa.
        
    Returns:
        int: Próximo estado da conversa (TERMOS).
    """
    try:
        # Importa a função obter_termos do módulo termos
        from termos import obter_termos
        
        # Obtém o texto dos termos formatado
        termos_texto = obter_termos()
        
        # Cria o teclado com o botão de voltar
        teclado_voltar = [["🔙 Voltar"]]
        
        # Envia a mensagem com os termos
        await update.message.reply_text(
            termos_texto,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(teclado_voltar, resize_keyboard=True)
        )
        return TERMOS
    except ImportError as e:
        logger.error(f"Erro ao importar módulo termos: {str(e)}", exc_info=True)
        mensagem_erro = (
            "❌ *Erro ao carregar os termos de uso.*\n\n"
            "Desculpe, não foi possível carregar os termos de uso no momento. "
            "Por favor, tente novamente mais tarde."
        )
    except Exception as e:
        logger.error(f"Erro no handler termos: {str(e)}", exc_info=True)
        mensagem_erro = (
            "❌ *Ocorreu um erro ao carregar os termos de uso.*\n\n"
            "Nossos termos de uso estão temporariamente indisponíveis. "
            "Por favor, tente novamente mais tarde."
        )
    
    # Se chegou aqui, houve um erro
    try:
        await update.message.reply_text(
            mensagem_erro,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([['🔙 Voltar']], resize_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Falha ao enviar mensagem de erro: {str(e)}", exc_info=True)
    
    return TERMOS

def setup_handlers(application):
    """Configura todos os handlers do bot."""
    # Limpa handlers antigos para evitar duplicação
    application.handlers = {}
    
    # Importa os handlers de conversação aqui para evitar importação circular
    from menus.menu_compra import get_compra_conversation, iniciar_compra
    from menus.menu_venda import get_venda_conversation
    
    # Adiciona os handlers de comando
    application.add_handler(CommandHandler('start', start))
    
    # Adiciona os handlers de conversação
    compra_conv = get_compra_conversation()
    venda_conv = get_venda_conversation()
    
    # Configura os handlers de conversação
    if compra_conv:
        application.add_handler(compra_conv)
    if venda_conv:
        application.add_handler(venda_conv)
    
    # Adiciona handlers para os outros menus
    application.add_handler(MessageHandler(filters.Regex('^🛒 Comprar$'), iniciar_compra))
    application.add_handler(MessageHandler(filters.Regex('^💰 Vender$'), vender))
    application.add_handler(MessageHandler(filters.Regex('^🔧 Serviços$'), servicos))
    application.add_handler(MessageHandler(filters.Regex('^❓ Ajuda$'), ajuda))
    application.add_handler(MessageHandler(filters.Regex('^📜 Termos$'), termos))
    application.add_handler(MessageHandler(filters.Regex('^🔙 Voltar$'), start))
    
    # ⚡ NOVA INTEGRAÇÃO LIGHTNING ⚡
    try:
        from handlers.lightning_integration import setup_lightning_integration
        
        # Configura a integração Lightning
        lightning_integration = setup_lightning_integration(
            application=application,
            enable_monitoring=True,  # Ativa monitoramento automático
            interval_seconds=30      # Verifica a cada 30 segundos
        )
        
        if lightning_integration:
            logger.info("✅ Integração Lightning configurada com sucesso!")
        else:
            logger.warning("⚠️ Falha ao configurar integração Lightning")
            
    except Exception as e:
        logger.error(f"❌ Erro ao configurar integração Lightning: {e}", exc_info=True)

async def signal_handler(app, signum=None, frame=None):
    """
    Manipulador de sinais para encerramento gracioso.
    
    Args:
        app: A instância da aplicação do bot
        signum: Número do sinal recebido (opcional)
        frame: Frame atual da execução (opcional)
    """
    signal_name = {getattr(signal, name): name for name in dir(signal) if name.startswith('SIG') and '_' not in name}.get(signum, str(signum))
    logger.info(f"Recebido sinal {signal_name}. Iniciando encerramento gracioso...")
    
    try:
        if app is not None:
            # Verifica se a aplicação está em execução
            if hasattr(app, 'running') and app.running:
                logger.info("Parando a aplicação...")
                await app.stop()
            
            # Encerra a aplicação
            if hasattr(app, 'shutdown'):
                logger.info("Encerrando a aplicação...")
                await app.shutdown()
            
            logger.info("Aplicação do bot encerrada com sucesso.")
    except Exception as e:
        logger.error(f"Erro durante o encerramento da aplicação: {e}", exc_info=True)
    finally:
        # Garante que o loop de eventos seja parado
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                logger.info("Parando o loop de eventos...")
                loop.stop()
            
            # Cancela todas as tarefas pendentes
            pending = [t for t in asyncio.all_tasks(loop=loop) if not t.done()]
            if pending:
                logger.info(f"Cancelando {len(pending)} tarefas pendentes...")
                for task in pending:
                    task.cancel()
                
                # Executa o loop novamente para processar os cancelamentos
                if loop.is_running():
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            
            logger.info("Limpeza concluída.")
        except Exception as e:
            logger.error(f"Erro durante a limpeza final: {e}", exc_info=True)

async def main():
    """
    Inicia o bot com tratamento de erros aprimorado e reconexão automática.
    
    Retorna:
        int: Código de saída (0 para sucesso, 1 para erro)
    """
    import time
    from datetime import datetime
    
    # Configurações de reconexão
    max_retries = BotConfig.MAX_RECONNECT_ATTEMPTS
    attempt = 0
    application = None
    last_successful_connection = None
    
    # Configura os manipuladores de sinal
    import signal
    import functools
    
    logger.info("Iniciando o bot com tratamento de erros aprimorado...")
    
    while attempt < max_retries:
        try:
            # Calcula o tempo desde a última conexão bem-sucedida
            if last_successful_connection:
                time_since_last = (datetime.now() - last_successful_connection).total_seconds()
                logger.info(f"Tempo desde a última conexão bem-sucedida: {time_since_last:.1f} segundos")
            
            # Calcula o tempo de espera com backoff exponencial
            wait_time = BotConfig.get_retry_delay(attempt)
            if attempt > 0:
                logger.info(f"Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time} segundos...")
                await asyncio.sleep(wait_time)
            
            # Inicializa a aplicação do bot
            logger.info(f"Inicializando o bot (tentativa {attempt + 1}/{max_retries})...")
            application = init_bot()
            
            # Configura os manipuladores de sinal para encerramento gracioso
            try:
                loop = asyncio.get_running_loop()
                
                # Remove manipuladores de sinal existentes, se houver
                for sig in (signal.SIGINT, signal.SIGTERM):
                    try:
                        loop.remove_signal_handler(sig)
                    except (NotImplementedError, RuntimeError):
                        # Algumas plataformas não suportam remove_signal_handler
                        pass
                
                # Adiciona os novos manipuladores de sinal
                for sig in (signal.SIGINT, signal.SIGTERM):
                    try:
                        loop.add_signal_handler(
                            sig,
                            lambda s=sig: asyncio.create_task(signal_handler(application, s, None))
                        )
                        logger.debug(f"Manipulador de sinal {sig} configurado com sucesso")
                    except (NotImplementedError, RuntimeError) as e:
                        logger.warning(f"Não foi possível configurar o manipulador para o sinal {sig}: {e}")
                    except Exception as e:
                        logger.error(f"Erro inesperado ao configurar o manipulador para o sinal {sig}: {e}", exc_info=True)
                
                logger.info("Manipuladores de sinal configurados com sucesso")
                
            except RuntimeError as e:
                logger.warning(f"Não foi possível configurar manipuladores de sinal (loop de eventos não está em execução): {e}")
            except Exception as e:
                logger.error(f"Erro inesperado ao configurar manipuladores de sinal: {e}", exc_info=True)
            
            # Inicia o bot com polling
            logger.info("Inicializando a aplicação...")
            await application.initialize()
            
            logger.info("Iniciando o bot...")
            await application.start()
            
            logger.info("Removendo webhook se existir...")
            await application.bot.delete_webhook(drop_pending_updates=BotConfig.DROP_PENDING_UPDATES)
            
            # Configura os handlers do bot
            logger.info("Configurando handlers...")
            setup_handlers(application)
            logger.info("Handlers configurados com sucesso!")
            
            last_successful_connection = datetime.now()
            logger.info(f"Bot iniciado com sucesso em {last_successful_connection.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Configura o updater para polling
            updater = application.updater
            
            # Inicia o polling com tratamento de erros robusto
            retry_attempt = 0
            
            while retry_attempt < BotConfig.MAX_POLLING_RETRIES:
                try:
                    logger.info(f"Iniciando polling (tentativa {retry_attempt + 1}/{BotConfig.MAX_POLLING_RETRIES})...")
                    
                    # Se o updater já estiver em execução, não faz nada
                    if updater.running:
                        logger.info("Updater já está em execução. Aguardando mensagens...")
                        # Mantém o bot rodando indefinidamente
                        while True:
                            await asyncio.sleep(3600)  # Dorme por 1 hora
                    else:
                        # Configura o polling com timeouts otimizados
                        logger.info("Iniciando polling...")
                        await updater.start_polling(
                            drop_pending_updates=BotConfig.DROP_PENDING_UPDATES,
                            allowed_updates=Update.ALL_TYPES,
                            timeout=BotConfig.POLLING_TIMEOUT,
                            bootstrap_retries=3
                        )
                        
                        # Se chegou aqui, o polling está funcionando
                        logger.info("Polling iniciado com sucesso!")
                        
                        # Mantém o bot rodando indefinidamente
                        while True:
                            await asyncio.sleep(3600)  # Dorme por 1 hora
                    
                except asyncio.CancelledError:
                    logger.info("Polling cancelado pelo usuário.")
                    raise
                    
                except (NetworkError, ConnectionError) as e:
                    retry_attempt += 1
                    wait_time = BotConfig.get_retry_delay(retry_attempt)
                    logger.error(f"Erro de rede no polling (tentativa {retry_attempt}/{BotConfig.MAX_POLLING_RETRIES}): {str(e)}")
                    logger.info(f"Tentando reconectar em {wait_time} segundos...")
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    retry_attempt += 1
                    wait_time = BotConfig.get_retry_delay(retry_attempt)
                    logger.error(f"Erro inesperado no polling (tentativa {retry_attempt}/{BotConfig.MAX_POLLING_RETRIES}): {str(e)}", exc_info=True)
                    logger.info(f"Tentando novamente em {wait_time} segundos...")
                    await asyncio.sleep(wait_time)
            
            # Se saiu do loop de tentativas de polling, incrementa a tentativa geral
            attempt += 1
            
        except asyncio.CancelledError:
            logger.info("Aplicação cancelada pelo usuário.")
            return 0
            
        except Exception as e:
            attempt += 1
            logger.error(f"Erro crítico na inicialização do bot (tentativa {attempt}/{max_retries}): {str(e)}", exc_info=True)
            
            # Se for um erro de rede, espera um pouco antes de tentar novamente
            if attempt < max_retries:
                wait_time = BotConfig.get_retry_delay(attempt)
                logger.info(f"Tentando novamente em {wait_time} segundos...")
                await asyncio.sleep(wait_time)
    
    # Se chegou aqui, todas as tentativas foram esgotadas
    logger.critical(f"Número máximo de tentativas de reconexão ({max_retries}) atingido. Encerrando...")
    
    # Limpeza final após o loop de tentativas
    if application is not None:
        try:
            logger.info("Iniciando limpeza final da aplicação...")
            if application.running:
                logger.info("Parando a aplicação...")
                await application.stop()
            logger.info("Encerrando a aplicação...")
            await application.shutdown()
            logger.info("Aplicação encerrada com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao encerrar a aplicação: {e}", exc_info=True)
        finally:
            # Força a coleta de lixo para liberar recursos
            import gc
            gc.collect()
    
    logger.critical("Não foi possível conectar ao Telegram após várias tentativas. Encerrando...")
    return 1

def run_bot():
    """
    Função de entrada principal para executar o bot.
    
    Returns:
        int: Código de saída (0 para sucesso, 1 para erro)
    """
    import traceback
    
    # Configura o loop de eventos
    loop = None
    try:
        # Cria um novo loop de eventos
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Configura o manipulador de exceções não capturadas
        def handle_exception(loop, context):
            # Log da exceção
            logger.critical(f"Exceção não capturada no loop de eventos: {context}")
            
            # Se houver exceção, registra o traceback
            if 'exception' in context:
                logger.critical("Traceback da exceção:", exc_info=context['exception'])
            
            # Encerra o loop de eventos
            if loop.is_running():
                loop.stop()
        
        # Configura o manipulador de exceções
        loop.set_exception_handler(handle_exception)
        
        # Executa o bot e captura o código de saída
        logger.info("Iniciando o bot...")
        exit_code = loop.run_until_complete(main())
        
        # Encerra o programa com o código de saída apropriado
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário (KeyboardInterrupt).")
        return 0
        
    except asyncio.CancelledError:
        logger.info("Operação cancelada.")
        return 0
        
    except Exception as e:
        logger.critical(f"Erro fatal na execução do bot: {str(e)}\n{traceback.format_exc()}")
        return 1
        
    finally:
        # Garante que o loop de eventos seja fechado corretamente
        if loop is not None:
            try:
                # Cancela todas as tarefas pendentes
                pending = [t for t in asyncio.all_tasks(loop=loop) if not t.done()]
                if pending:
                    logger.info(f"Cancelando {len(pending)} tarefas pendentes...")
                    for task in pending:
                        task.cancel()
                    
                    # Executa o loop novamente para processar os cancelamentos
                    if loop.is_running():
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                # Fecha o loop
                if not loop.is_closed():
                    loop.close()
                    logger.info("Loop de eventos fechado com sucesso.")
                    
            except Exception as e:
                logger.error(f"Erro durante a limpeza final: {e}", exc_info=True)
            
            # Força a coleta de lixo para liberar recursos
            import gc
            gc.collect()
            logger.info("Coleta de lixo forçada executada.")

if __name__ == '__main__':
    # Executa o bot e sai com o código de status apropriado
    sys.exit(run_bot())
