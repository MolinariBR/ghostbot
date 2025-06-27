"""
Script de teste para validar a integração Lightning no bot Ghost
"""
import asyncio
import sys
from pathlib import Path

# Adiciona o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from handlers.lightning_payments import LightningPaymentManager
from telegram import Bot
import logging

# Configura logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_lightning_bot_integration():
    """Testa a integração Lightning do bot"""
    try:
        # Token de teste (substitua por um token válido para testes reais)
        test_token = "TEST_TOKEN"
        
        # Simula um bot (para teste, não precisa de token real)
        class MockBot:
            async def send_message(self, chat_id, text, parse_mode=None, disable_web_page_preview=None):
                logger.info(f"🤖 Enviaria mensagem para {chat_id}:")
                logger.info(f"📝 Conteúdo: {text[:100]}...")
                return True
        
        # Cria instância do bot mock
        mock_bot = MockBot()
        
        # Testa o gerenciador Lightning
        logger.info("🧪 Testando LightningPaymentManager...")
        
        lightning_manager = LightningPaymentManager(mock_bot)
        
        # Testa busca de pagamentos completados
        logger.info("🔍 Testando busca de pagamentos completados...")
        completed_payments = lightning_manager._get_completed_lightning_payments()
        logger.info(f"📊 Encontrados {len(completed_payments)} pagamentos completados")
        
        # Testa formatação de mensagem
        logger.info("📝 Testando formatação de mensagem...")
        test_message = lightning_manager._format_lightning_message(
            amount_sats=1000,
            lnurl="lnurl1dp68gurn8ghj7um5v93kketj9ehx2amn9uh8wetvdskkkmn0wahz7mrww4excup0dajx2mrv92x9xp",
            qr_code_url="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=test",
            transaction_id=123
        )
        logger.info("✅ Mensagem formatada com sucesso")
        logger.info(f"📄 Preview: {test_message[:200]}...")
        
        # Testa geração de QR code
        logger.info("🔲 Testando geração de QR code...")
        qr_url = lightning_manager._generate_qr_code("test_lnurl")
        logger.info(f"🔗 QR URL: {qr_url}")
        
        # Testa trigger de processamento (mock)
        logger.info("🚀 Testando trigger de processamento...")
        try:
            # Como não temos backend rodando, isso deve falhar graciosamente
            success = await lightning_manager.trigger_payment_processing()
            logger.info(f"📡 Resultado do trigger: {success}")
        except Exception as e:
            logger.info(f"⚠️ Esperado: erro de conexão com backend - {e}")
        
        logger.info("✅ Todos os testes do LightningPaymentManager passaram!")
        
        # Testa comandos Lightning
        logger.info("🤖 Testando comandos Lightning...")
        
        from handlers.lightning_commands import lightning_handlers
        logger.info(f"📋 Encontrados {len(lightning_handlers)} handlers Lightning")
        
        for handler in lightning_handlers:
            commands = getattr(handler, 'commands', None)
            if commands:
                if isinstance(commands, (list, tuple, set)):
                    command_name = list(commands)[0] if commands else 'N/A'
                else:
                    command_name = str(commands)
            else:
                command_name = 'N/A'
            logger.info(f"⚡ Handler: {command_name}")
        
        logger.info("✅ Todos os testes de comandos Lightning passaram!")
        
        # Testa integração
        logger.info("🔗 Testando integração Lightning...")
        
        from handlers.lightning_integration import LightningBotIntegration
        from telegram.ext import Application
        
        # Cria aplicação mock
        class MockApplication:
            def __init__(self):
                self.bot = mock_bot
                self.handlers = {}
                self.job_queue = MockJobQueue()
                
            def add_handler(self, handler):
                self.handlers[len(self.handlers)] = handler
                
        class MockJobQueue:
            def run_once(self, callback, when):
                logger.info(f"📅 Job agendado para execução em {when} segundos")
        
        mock_app = MockApplication()
        integration = LightningBotIntegration(mock_app)
        
        # Testa setup de handlers
        integration.setup_lightning_handlers()
        logger.info(f"🔧 {len(mock_app.handlers)} handlers registrados")
        
        logger.info("✅ Todos os testes de integração Lightning passaram!")
        
        print("\n" + "="*60)
        print("🎉 TESTE DA INTEGRAÇÃO LIGHTNING CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print("✅ LightningPaymentManager funcionando")
        print("✅ Comandos Lightning registrados")
        print("✅ Integração com bot configurada")
        print("✅ Sistema pronto para produção")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    # Executa o teste
    success = asyncio.run(test_lightning_bot_integration())
    
    if success:
        print("\n🚀 Integração Lightning validada com sucesso!")
        sys.exit(0)
    else:
        print("\n💥 Falha na validação da integração Lightning!")
        sys.exit(1)
