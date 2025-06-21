#!/usr/bin/env python3
"""
Bot principal do Ghost Bot - Assistente de Criptomoedas
"""
import asyncio
import logging
import signal
import random
import sys
from pathlib import Path

# Configura o path para incluir o diretório raiz
sys.path.insert(0, str(Path(__file__).parent.resolve()))

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
from telegram.request import HTTPXRequest

# Importações locais
from tokens import Config
from config import BotConfig, LogConfig
from menus import setup_menus, get_compra_conversation, get_venda_conversation
from menus.menu_compra import iniciar_compra

# Cria o diretório de logs se não existir
LogConfig.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configuração do logger
logging.basicConfig(
    level=getattr(logging, LogConfig.LOG_LEVEL),
    format=LogConfig.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            LogConfig.LOG_FILE,
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT,
            encoding='utf-8'
        )
    ]
)
logger = logging.getLogger(__name__)

# Estados da conversa
MENU, COMPRAR, VENDER, SERVICOS, AJUDA, TERMOS = range(6)

# Inicialização do bot
def init_bot():
    """
    Inicializa e retorna a aplicação do bot.
    
    Retorna:
        Application: Instância da aplicação do bot
    """
    # Cria e configura a aplicação
    application = (
        Application.builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .connect_timeout(BotConfig.CONNECTION_TIMEOUT)
        .read_timeout(BotConfig.READ_TIMEOUT)
        .pool_timeout(BotConfig.POOL_TIMEOUT)
        .get_updates_http_version('1.1')
        .http_version('1.1')
        .build()
    )
    
    return application

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
def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa e mostra o menu principal."""
    reply_markup = ReplyKeyboardMarkup(menu_principal(), resize_keyboard=True)
    update.message.reply_text(
        '👋 Olá! Eu sou o Ghost Bot, seu assistente de criptomoedas.\n\n'
        'Escolha uma opção abaixo:',
        reply_markup=reply_markup
    )
    return MENU

def vender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lida com a opção de venda."""
    update.message.reply_text(
        "🔹 *VENDER* 🔹\n\n"
        "Por favor, informe o valor em Bitcoin que deseja vender.",
        parse_mode='Markdown'
    )
    return VENDER

def servicos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

def termos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

def setup_handlers(application):
    """Configura todos os handlers do bot."""
    # Limpa handlers antigos para evitar duplicação
    application.handlers = {}
    
    # Adiciona os handlers de comando
    application.add_handler(CommandHandler('start', start))
    
    # Adiciona os handlers de conversação
    application.add_handler(get_compra_conversation())
    application.add_handler(get_venda_conversation())
    
    # Adiciona handlers para os outros menus
    application.add_handler(MessageHandler(filters.Regex('^🛒 Comprar$'), iniciar_compra))
    application.add_handler(MessageHandler(filters.Regex('^🔧 Serviços$'), servicos))
    application.add_handler(MessageHandler(filters.Regex('^❓ Ajuda$'), ajuda))
    application.add_handler(MessageHandler(filters.Regex('^📜 Termos$'), termos))
    application.add_handler(MessageHandler(filters.Regex('^🔙 Voltar$'), start))

async def signal_handler(app, signum, frame):
    """
    Manipulador de sinais para encerramento gracioso.
    
    Args:
        app: A instância da aplicação do bot
        signum: Número do sinal recebido
        frame: Frame atual da execução
    """
    logger.info("Recebido sinal de desligamento. Encerrando o bot graciosamente...")
    
    try:
        if app is not None and app.running:
            await app.stop()
            await app.shutdown()
            logger.info("Aplicação do bot encerrada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao encerrar a aplicação: {e}")
    finally:
        # Garante que o loop de eventos seja parado
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()

async def main():
    """
    Inicia o bot com tratamento de erros e reconexão automática.
    
    Retorna:
        int: Código de saída (0 para sucesso, 1 para erro)
    """
    import time
    
    # Configurações de reconexão
    max_retries = BotConfig.MAX_RETRIES
    base_retry_delay = BotConfig.BASE_RETRY_DELAY
    
    attempt = 0
    application = None
    
    # Configura os manipuladores de sinal
    import signal
    import functools
    
    while attempt < max_retries:
        try:
            # Inicializa a aplicação do bot
            application = init_bot()
            
            # Configura os manipuladores de sinal
            try:
                loop = asyncio.get_running_loop()
                for sig in (signal.SIGINT, signal.SIGTERM):
                    loop.add_signal_handler(
                        sig,
                        lambda s=sig: asyncio.create_task(signal_handler(application, s, None))
                    )
            except RuntimeError:
                # Se não houver loop em execução, ignora
                pass
            
            logger.info(f"Iniciando o bot (tentativa {attempt + 1}/{max_retries})...")
            
            # Inicia o bot com polling
            await application.initialize()
            await application.start()
            await application.bot.delete_webhook(drop_pending_updates=BotConfig.DROP_PENDING_UPDATES)
            
            logger.info("Bot iniciado com sucesso!")
            
            # Inicia o polling
            await application.updater.start_polling(
                drop_pending_updates=BotConfig.DROP_PENDING_UPDATES,
                allowed_updates=Update.ALL_TYPES
            )
            
            # Mantém o bot em execução até receber um sinal de parada
            stop_event = asyncio.Event()
            
            # Configura os manipuladores de sinal para parar o bot corretamente
            def signal_handler(signum, frame):
                logger.info(f"Recebido sinal {signum}, encerrando o bot...")
                stop_event.set()
                
            # Configura os sinais para parar o bot
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, signal_handler, sig, None)
            
            # Aguarda até que o evento de parada seja definido
            await stop_event.wait()
            
            # Para o updater
            await application.updater.stop()
            
            # Se chegou aqui, o bot foi parado normalmente
            logger.info("Bot parado pelo usuário.")
            return 0
            
        except RetryAfter as e:
            # O Telegram está pedindo para esperar
            wait_time = e.retry_after + 5  # Adiciona 5 segundos de margem
            logger.warning(f"Rate limit atingido. Esperando {wait_time} segundos...")
            await asyncio.sleep(wait_time)
            continue
            
        except (NetworkError, TimedOut) as e:
            attempt += 1
            logger.error(f"Erro de rede/timeout (tentativa {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                # Espera um tempo exponencial com jitter antes de tentar novamente
                wait_time = base_retry_delay * (2 ** (attempt - 1)) + random.uniform(0, 5)
                logger.info(f"Tentando reconectar em {wait_time:.1f} segundos...")
                await asyncio.sleep(wait_time)
            continue
            
        except (TelegramError, ConnectionError) as e:
            attempt += 1
            logger.error(f"Erro do Telegram (tentativa {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                await asyncio.sleep(base_retry_delay)
            continue
            
        except asyncio.CancelledError:
            logger.info("Operação cancelada pelo usuário.")
            return 0
            
        except Exception as e:
            attempt += 1
            logger.exception(f"Erro inesperado (tentativa {attempt}/{max_retries}): {str(e)}")
            if attempt >= max_retries:
                logger.critical("Número máximo de tentativas atingido. Encerrando...")
                return 1
            await asyncio.sleep(base_retry_delay)
            continue
            
        finally:
            # Limpeza em caso de erro ou término normal
            if application is not None:
                try:
                    if application.running:
                        await application.stop()
                    await application.shutdown()
                except Exception as e:
                    logger.error(f"Erro ao encerrar a aplicação: {e}")
    
    logger.critical("Não foi possível conectar ao Telegram após várias tentativas. Encerrando...")
    return 1

def run_bot():
    """Função de entrada principal para executar o bot."""
    try:
        # Configura o loop de eventos
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Executa o bot e captura o código de saída
        exit_code = loop.run_until_complete(main())
        
        # Encerra o programa com o código de saída apropriado
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário.")
        return 0
    except Exception as e:
        logger.critical(f"Erro fatal: {str(e)}", exc_info=True)
        return 1
    finally:
        # Garante que o loop de eventos seja fechado corretamente
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.stop()
            
            # Cancela todas as tarefas pendentes
            pending = asyncio.all_tasks(loop=loop)
            for task in pending:
                task.cancel()
            
            # Executa o loop novamente para processar os cancelamentos
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            
            # Fecha o loop
            loop.close()
        except Exception as e:
            logger.error(f"Erro ao fechar o loop de eventos: {e}")

if __name__ == '__main__':
    # Configura o manipulador de sinais para o processo principal
    import signal
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    
    # Executa o bot e sai com o código de status apropriado
    sys.exit(run_bot())
