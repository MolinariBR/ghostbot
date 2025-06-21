#!/usr/bin/env python3
"""
Bot principal do Ghost Bot - Assistente de Criptomoedas
"""
import logging
import signal
import random
import sys
from pathlib import Path

# Configura o path para incluir o diretório raiz
sys.path.insert(0, str(Path(__file__).parent.resolve()))

# Importações do Telegram
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler
)
from telegram.error import (
    NetworkError, 
    TelegramError, 
    RetryAfter, 
    TimedOut, 
    ChatMigrated, 
    Conflict,
    Unauthorized,
    BadRequest
)

# Importações locais
from tokens import Config
from config import BotConfig, LogConfig
from menus import setup_menus, get_compra_conversation, get_venda_conversation
from menus.menu_compra import iniciar_compra

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
    """Inicializa e retorna a instância do bot."""
    # Configurações de conexão
    request_kwargs = {
        'connect_timeout': BotConfig.CONNECTION_TIMEOUT,
        'read_timeout': BotConfig.READ_TIMEOUT,
        'pool_timeout': BotConfig.POOL_TIMEOUT,
        'retries': BotConfig.MAX_RETRIES,
    }
    
    # Inicializa o updater e dispatcher com as configurações de conexão
    updater = Updater(
        token=Config.TELEGRAM_BOT_TOKEN,
        use_context=True,
        request_kwargs=request_kwargs
    )
    
    return updater, updater.dispatcher

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

def setup_handlers(dispatcher):
    """Configura todos os handlers do bot."""
    # Limpa handlers antigos para evitar duplicação
    dispatcher.handlers = {}
    
    # Adiciona os handlers de comando
    dispatcher.add_handler(CommandHandler('start', start))
    
    # Adiciona os handlers de conversação
    dispatcher.add_handler(get_compra_conversation())
    dispatcher.add_handler(get_venda_conversation())
    
    # Adiciona handlers para os outros menus
    dispatcher.add_handler(MessageHandler(Filters.regex('^🛒 Comprar$'), iniciar_compra))
    dispatcher.add_handler(MessageHandler(Filters.regex('^🔧 Serviços$'), servicos))
    dispatcher.add_handler(MessageHandler(Filters.regex('^❓ Ajuda$'), ajuda))
    dispatcher.add_handler(MessageHandler(Filters.regex('^📜 Termos$'), termos))
    dispatcher.add_handler(MessageHandler(Filters.regex('^🔙 Voltar$'), start))

def signal_handler(updater, signum, frame):
    """Manipulador de sinais para encerramento gracioso."""
    logger.info("Recebido sinal de desligamento. Encerrando o bot graciosamente...")
    updater.stop()
    updater.is_idle = False

def main():
    """Inicia o bot com tratamento de erros e reconexão automática."""
    import time
    
    # Configurações de reconexão
    max_retries = BotConfig.MAX_RETRIES
    base_retry_delay = BotConfig.BASE_RETRY_DELAY
    
    # Inicializa o bot
    updater, dispatcher = init_bot()
    
    # Configura os handlers de sinal para um encerramento limpo
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda s, f: signal_handler(updater, s, f))
    
    attempt = 0
    while attempt < max_retries:
        try:
            # Configura os handlers
            setup_handlers(dispatcher)
            
            logger.info(f"Iniciando o bot (tentativa {attempt + 1}/{max_retries})...")
            
            # Inicia o bot com polling
            updater.start_polling(
                drop_pending_updates=BotConfig.DROP_PENDING_UPDATES,
                timeout=BotConfig.POLLING_TIMEOUT,
                read_latency=BotConfig.READ_LATENCY,
                bootstrap_retries=BotConfig.BOOTSTRAP_RETRIES
            )
            
            logger.info("Bot iniciado com sucesso!")
            
            # Mantém o bot em execução
            updater.idle()
            
            # Se chegou aqui, o bot foi parado normalmente
            logger.info("Bot parado pelo usuário.")
            return 0
            
        except RetryAfter as e:
            # O Telegram está pedindo para esperar
            wait_time = e.retry_after + 5  # Adiciona 5 segundos de margem
            logger.warning(f"Rate limit atingido. Esperando {wait_time} segundos...")
            time.sleep(wait_time)
            continue
            
        except (NetworkError, TimedOut) as e:
            attempt += 1
            logger.error(f"Erro de rede/timeout (tentativa {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                # Espera um tempo exponencial com jitter antes de tentar novamente
                wait_time = base_retry_delay * (2 ** (attempt - 1)) + random.uniform(0, 5)
                logger.info(f"Tentando reconectar em {wait_time:.1f} segundos...")
                time.sleep(wait_time)
            continue
            
        except (TelegramError, ConnectionError) as e:
            attempt += 1
            logger.error(f"Erro do Telegram (tentativa {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                time.sleep(base_retry_delay)
            continue
            
        except Exception as e:
            attempt += 1
            logger.exception(f"Erro inesperado (tentativa {attempt}/{max_retries}): {str(e)}")
            if attempt >= max_retries:
                logger.critical("Número máximo de tentativas atingido. Encerrando...")
                return 1
            time.sleep(base_retry_delay)
            continue
    
    logger.critical("Não foi possível conectar ao Telegram após várias tentativas. Encerrando...")
    return 1

if __name__ == '__main__':
    try:
        # Executa o bot e captura o código de saída
        exit_code = main()
        # Encerra o programa com o código de saída apropriado
        sys.exit(exit_code if exit_code is not None else 0)
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Erro crítico não tratado: {str(e)}", exc_info=True)
        sys.exit(1)
