"""
Script para inicializar o sistema Lightning no bot Ghost
"""
import asyncio
import logging
from telegram.ext import Application
from handlers.lightning_payments import get_lightning_manager
from handlers.lightning_commands import lightning_handlers

logger = logging.getLogger(__name__)

class LightningBotIntegration:
    """Integração do sistema Lightning com o bot Ghost"""
    
    def __init__(self, application: Application):
        """
        Inicializa a integração Lightning
        
        Args:
            application: Aplicação do bot Telegram
        """
        self.application = application
        self.lightning_manager = None
        
    def setup_lightning_handlers(self):
        """Registra os handlers Lightning no bot"""
        try:
            # Adiciona todos os handlers Lightning
            for handler in lightning_handlers:
                self.application.add_handler(handler)
                
            logger.info("Handlers Lightning registrados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao registrar handlers Lightning: {e}")
            
    async def start_lightning_monitoring(self, interval_seconds: int = 30):
        """
        Inicia o monitoramento Lightning em background
        
        Args:
            interval_seconds: Intervalo entre verificações
        """
        try:
            # Obtém o bot da aplicação
            bot = self.application.bot
            
            # Inicializa o gerenciador Lightning
            self.lightning_manager = get_lightning_manager(bot)
            
            # Inicia o monitoramento em background
            asyncio.create_task(
                self.lightning_manager.start_monitoring(interval_seconds)
            )
            
            logger.info(f"Monitoramento Lightning iniciado (intervalo: {interval_seconds}s)")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar monitoramento Lightning: {e}")
            
    async def stop_lightning_monitoring(self):
        """Para o monitoramento Lightning"""
        try:
            # O monitoramento será interrompido automaticamente quando o bot parar
            logger.info("Monitoramento Lightning será finalizado com o bot")
            
        except Exception as e:
            logger.error(f"Erro ao parar monitoramento Lightning: {e}")

# Função para integrar Lightning ao bot principal
def setup_lightning_integration(application: Application, enable_monitoring: bool = True, interval_seconds: int = 30):
    """
    Configura a integração Lightning no bot
    
    Args:
        application: Aplicação do bot Telegram
        enable_monitoring: Se deve ativar monitoramento automático
        interval_seconds: Intervalo de monitoramento em segundos
        
    Returns:
        Instância da integração Lightning
    """
    try:
        # Cria a integração
        integration = LightningBotIntegration(application)
        
        # Registra os handlers
        integration.setup_lightning_handlers()
        
        # Inicia monitoramento se solicitado
        if enable_monitoring:
            # Agenda o início do monitoramento após o bot estar pronto
            async def start_monitoring():
                await integration.start_lightning_monitoring(interval_seconds)
                
            application.job_queue.run_once(
                lambda context: asyncio.create_task(start_monitoring()),
                when=5  # Aguarda 5 segundos após o bot iniciar
            )
            
        logger.info("Integração Lightning configurada com sucesso")
        return integration
        
    except Exception as e:
        logger.error(f"Erro ao configurar integração Lightning: {e}")
        return None

# Função auxiliar para testar a integração
async def test_lightning_integration():
    """Testa a integração Lightning"""
    try:
        from telegram import Bot
        from config import TELEGRAM_TOKEN
        
        # Cria bot de teste
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Testa o gerenciador Lightning
        lightning_manager = get_lightning_manager(bot)
        
        # Verifica pagamentos completados
        await lightning_manager.check_completed_payments()
        
        print("✅ Teste da integração Lightning concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste Lightning: {e}")

if __name__ == "__main__":
    # Executa teste se chamado diretamente
    asyncio.run(test_lightning_integration())
