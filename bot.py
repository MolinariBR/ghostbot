#!/usr/bin/env python3
"""
Bot principal do Ghost Bot - Assistente de Criptomoedas
"""
import asyncio
import logging
import os
import random
import sys
import signal
from datetime import datetime
from pathlib import Path

# Configura o path para incluir o diretório raiz
sys.path.insert(0, str(Path(__file__).parent.resolve()))

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
    # Configurações do bot
    class BotConfig:
        # Timeouts e tentativas
        REQUEST_TIMEOUT = 45.0  # Aumentado para 45 segundos
        MAX_RETRIES = 10  # Aumentado o número de tentativas
        BASE_RETRY_DELAY = 10  # Aumentado para 10 segundos
        
        # Configurações de polling
        POLLING_TIMEOUT = 45.0  # Aumentado para 45 segundos
        READ_LATENCY = 5.0  # Aumentado para 5 segundos
        
        # Configurações de conexão
        CONNECTION_TIMEOUT = 90.0  # Aumentado para 90 segundos
        READ_TIMEOUT = 90.0  # Aumentado para 90 segundos
        WRITE_TIMEOUT = 90.0  # Adicionado timeout para escrita
        POOL_TIMEOUT = 90.0  # Aumentado para 90 segundos
        MAX_RETRY_ATTEMPTS = 10  # Aumentado o número de tentativas
        
        # Tamanho do pool de conexões
        POOL_SIZE = 16  # Aumentado o tamanho do pool
        
        # Outras configurações
        DROP_PENDING_UPDATES = True
        
        # Configurações adicionais
        
        @classmethod
        def get_retry_delay(cls, attempt: int) -> float:
            """Calcula o tempo de espera para reconexão com backoff exponencial."""
            return min(cls.BASE_RETRY_DELAY * (2 ** (attempt - 1)), 600)  # Máximo 10 minutos

    # Configuração do cliente HTTP personalizado com opções avançadas
    request = HTTPXRequest(
        connection_pool_size=BotConfig.POOL_SIZE,
        read_timeout=BotConfig.READ_TIMEOUT,
        write_timeout=BotConfig.WRITE_TIMEOUT,
        connect_timeout=BotConfig.CONNECTION_TIMEOUT,
        pool_timeout=BotConfig.POOL_TIMEOUT,
        http_version='1.1',
        socket_options=[
            # Habilita keepalive
            ('keepalive', 1),
            # Tempo em segundos até enviar a primeira sonda
            ('tcp_keepidle', 60),
            # Intervalo entre sondas em segundos
            ('tcp_keepintvl', 30),
            # Número de tentativas de sondagem
            ('tcp_keepcnt', 5)
        ]
    )
    
    # Cria e configura a aplicação com a instância personalizada de request
    # Os timeouts já estão configurados no objeto request
    application = (
        Application.builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .request(request)  # Usa a instância personalizada com configurações
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa e mostra o menu principal."""
    reply_markup = ReplyKeyboardMarkup(menu_principal(), resize_keyboard=True)
    await update.message.reply_text(
        '👋 Olá! Eu sou o Ghost Bot, seu assistente de criptomoedas.\n\n'
        'Escolha uma opção abaixo:',
        reply_markup=reply_markup
    )
    return MENU

async def vender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lida com a opção de venda."""
    await update.message.reply_text(
        "🔹 *VENDER* 🔹\n\n"
        "Por favor, informe o valor em Bitcoin que deseja vender.",
        parse_mode='Markdown'
    )
    return VENDER

async def servicos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra os serviços disponíveis."""
    await update.message.reply_text(
        "🔧 *SERVIÇOS* 🔧\n\n"
        "Aqui estão os serviços disponíveis:\n\n"
        "• Compra e venda de criptomoedas\n"
        "• Carteira digital segura\n"
        "• Conversão entre criptomoedas\n\n"
        "Voltar ao menu: /start",
        parse_mode='Markdown'
    )
    return SERVICOS

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra a ajuda."""
    await update.message.reply_text(
        "❓ *AJUDA* ❓\n\n"
        "Como posso te ajudar?\n\n"
        "• Para começar, use /start\n"
        "• Para comprar criptomoedas, toque em *Comprar*\n"
        "• Para vender criptomoedas, toque em *Vender*\n"
        "• Dúvidas? Entre em contato com nosso suporte\n\n"
        "Voltar ao menu: /start",
        parse_mode='Markdown'
    )
    return AJUDA

async def termos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra os termos de uso."""
    await update.message.reply_text(
        "📜 *TERMOS DE USO* 📜\n\n"
        "Ao usar este bot, você concorda com nossos termos de uso:\n\n"
        "1. Não use para atividades ilegais\n"
        "2. Mantenha suas credenciais em segredo\n"
        "3. Esteja ciente dos riscos do mercado de criptomoedas\n\n"
        "Voltar ao menu: /start",
        parse_mode='Markdown'
    )
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
            
            # Configura os handlers do bot
            setup_handlers(application)
            logger.info("Handlers configurados com sucesso!")
            
            logger.info("Bot iniciado com sucesso!")
            
            # Configura o updater
            updater = application.updater
            
            # Inicia o polling com tratamento de erros robusto
            max_retry_attempts = 10
            retry_attempt = 0
            base_delay = 5  # segundos
            
            while retry_attempt < max_retry_attempts:
                try:
                    logger.info(f"Iniciando polling (tentativa {retry_attempt + 1}/{max_retry_attempts})...")
                    
                    # Configura o polling com timeouts otimizados
                    await updater.start_polling(
                        drop_pending_updates=BotConfig.DROP_PENDING_UPDATES,
                        allowed_updates=Update.ALL_TYPES,
                        timeout=BotConfig.POLLING_TIMEOUT,
                        read_latency=BotConfig.READ_LATENCY,
                        bootstrap_retries=3,  # Reduzido para evitar tentativas muito longas
                        close_loop=False,  # Impede que o loop seja fechado em caso de erro
                        http_version='1.1',
                        pool_timeout=BotConfig.POOL_TIMEOUT,
                        connect_timeout=BotConfig.CONNECTION_TIMEOUT,
                        read_timeout=BotConfig.READ_TIMEOUT,
                        write_timeout=BotConfig.WRITE_TIMEOUT
                    )
                    
                    logger.info("Polling iniciado com sucesso!")
                    break  # Sai do loop se o polling for bem-sucedido
                    
                except asyncio.CancelledError:
                    logger.info("Polling cancelado pelo usuário.")
                    raise
                    
                except (NetworkError, ConnectionError) as e:
                    retry_attempt += 1
                    wait_time = min(base_delay * (2 ** (retry_attempt - 1)), 300)  # Exponencial backoff com máximo de 5 minutos
                    logger.error(f"Erro de rede no polling (tentativa {retry_attempt}/{max_retry_attempts}): {str(e)}")
                    logger.info(f"Tentando reconectar em {wait_time} segundos...")
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    retry_attempt += 1
                    wait_time = min(base_delay * (2 ** (retry_attempt - 1)), 300)  # Exponencial backoff com máximo de 5 minutos
                    logger.error(f"Erro inesperado no polling (tentativa {retry_attempt}/{max_retry_attempts}): {str(e)}")
                    logger.info(f"Tentando novamente em {wait_time} segundos...")
                    await asyncio.sleep(wait_time)
            
            if retry_attempt >= max_retry_attempts:
                logger.error(f"Número máximo de tentativas de reconexão ({max_retry_attempts}) atingido. Encerrando...")
                return 1  # Código de erro
            
            # Mantém o bot em execução até receber um sinal de parada
            stop_event = asyncio.Event()
            
            # Configura os manipuladores de sinal para parar o bot corretamente
            def signal_handler(signum, frame):
                logger.info(f"Recebido sinal {signum}, encerrando o bot...")
                stop_event.set()
                
            # Configura os sinais para parar o bot
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                try:
                    loop.add_signal_handler(sig, signal_handler, sig, None)
                except (NotImplementedError, RuntimeError) as e:
                    logger.warning(f"Não foi possível adicionar manipulador para sinal {sig}: {e}")
            
            try:
                # Aguarda até que o evento de parada seja definido
                await stop_event.wait()
                
                # Se chegou aqui, o bot foi parado normalmente
                logger.info("Bot parado pelo usuário.")
                return 0
                
            except asyncio.CancelledError:
                logger.info("Operação cancelada pelo usuário.")
                return 0
                
            except Exception as e:
                logger.error(f"Erro durante a execução do bot: {e}", exc_info=True)
                return 1
                
            finally:
                # Para o updater de forma segura
                try:
                    if updater and hasattr(updater, 'running') and updater.running:
                        logger.info("Parando o updater...")
                        await updater.stop()
                        logger.info("Updater parado com sucesso.")
                except Exception as e:
                    logger.error(f"Erro ao parar o updater: {e}", exc_info=True)
                
                # Garante que a aplicação seja parada corretamente
                try:
                    if application and application.running:
                        logger.info("Parando a aplicação...")
                        await application.stop()
                        logger.info("Aplicação parada com sucesso.")
                except Exception as e:
                    logger.error(f"Erro ao parar a aplicação: {e}", exc_info=True)
            
        except RetryAfter as e:
            # O Telegram está pedindo para esperar
            wait_time = e.retry_after + 10  # Adiciona 10 segundos de margem
            logger.warning(f"Rate limit atingido. Esperando {wait_time} segundos...")
            await asyncio.sleep(wait_time)
            continue
            
        except (NetworkError, ConnectionError, TimedOut) as e:
            attempt += 1
            wait_time = min(BotConfig.BASE_RETRY_DELAY * (2 ** (attempt - 1)), 300)  # Exponencial backoff
            logger.error(f"Erro de rede/timeout (tentativa {attempt}/{max_retries}): {str(e)}")
            logger.info(f"Tentando novamente em {wait_time} segundos...")
            if attempt < max_retries:
                await asyncio.sleep(wait_time)  # Aguarda antes de tentar novamente
                continue
            else:
                logger.critical("Número máximo de tentativas de reconexão atingido. Encerrando...")
                return 1
            
        except (TelegramError, ConnectionError) as e:
            attempt += 1
            wait_time = min(BotConfig.BASE_RETRY_DELAY * (2 ** (attempt - 1)), 300)  # Exponencial backoff
            logger.error(f"Erro do Telegram (tentativa {attempt}/{max_retries}): {str(e)}")
            logger.info(f"Tentando novamente em {wait_time} segundos...")
            if attempt < max_retries:
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.critical("Número máximo de tentativas de conexão atingido. Encerrando...")
                return 1
            
        except Exception as e:
            attempt += 1
            wait_time = min(BotConfig.BASE_RETRY_DELAY * (2 ** (attempt - 1)), 300)  # Exponencial backoff
            logger.error(f"Erro inesperado (tentativa {attempt}/{max_retries}): {str(e)}", exc_info=True)
            logger.info(f"Tentando novamente em {wait_time} segundos...")
            if attempt < max_retries:
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.critical("Número máximo de tentativas atingido. Encerrando...")
                return 1
    
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
