#!/usr/bin/env python3
"""
Main Integrator - Ponto de entrada principal para o sistema de gatilhos integrado
Coordena todos os componentes do sistema: bot, gatilhos, monitor PIX e handlers
"""
import sys
import os
import logging
from pathlib import Path

# Adicionar diretório principal ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mau/bot/ghost/logs/integrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main_integrator')

def initialize_system():
    """Inicializa todos os componentes do sistema"""
    logger.info("🚀 Iniciando sistema integrado Ghost Bot...")
    
    # Importar módulos necessários
    try:
        from sistema_gatilhos import TriggerSystem, initialize_trigger_system
        from integrador_bot_gatilhos import BotTriggerIntegrator, TriggerUIImplementation
        from smart_pix_monitor import SmartPixMonitor
        from lightning_handler import LightningHandler
        import bot
        
        logger.info("✅ Todos os módulos importados com sucesso")
        
        # Inicializar sistema de gatilhos
        logger.info("🔧 Inicializando sistema de gatilhos...")
        trigger_system = initialize_trigger_system()
        
        # Inicializar monitor PIX
        logger.info("💰 Inicializando Smart PIX Monitor...")
        pix_monitor = SmartPixMonitor()
        
        # Inicializar handler Lightning
        logger.info("⚡ Inicializando Lightning Handler...")
        lightning_handler = LightningHandler()
        
        # Integrar com bot do Telegram
        logger.info("🤖 Integrando com bot do Telegram...")
        bot_integrator = BotTriggerIntegrator(bot.bot, trigger_system)
        ui_implementation = TriggerUIImplementation(bot.bot)
        
        # Conectar componentes
        logger.info("🔗 Conectando componentes...")
        
        # Conectar monitor PIX ao sistema de gatilhos
        pix_monitor.set_trigger_system(trigger_system)
        
        # Conectar handler Lightning ao sistema de gatilhos
        lightning_handler.set_trigger_system(trigger_system)
        
        # Registrar handlers de eventos
        register_event_handlers(trigger_system, lightning_handler, pix_monitor)
        
        logger.info("✅ Sistema integrado inicializado com sucesso!")
        
        return {
            'trigger_system': trigger_system,
            'bot_integrator': bot_integrator,
            'ui_implementation': ui_implementation,
            'pix_monitor': pix_monitor,
            'lightning_handler': lightning_handler
        }
        
    except ImportError as e:
        logger.error(f"❌ Erro ao importar módulos: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        return None

def register_event_handlers(trigger_system, lightning_handler, pix_monitor):
    """Registra handlers de eventos no sistema de gatilhos"""
    logger.info("📋 Registrando handlers de eventos...")
    
    # Handlers do Lightning
    trigger_system.register_handler('ADDRESS_PROVIDED', lightning_handler.handle_address_provided)
    trigger_system.register_handler('PAYMENT_CONFIRMED', lightning_handler.handle_payment_confirmed)
    trigger_system.register_handler('SEND_CRYPTO', lightning_handler.handle_send_crypto)
    
    # Handlers do PIX Monitor
    trigger_system.register_handler('PIX_PAYMENT_DETECTED', pix_monitor.handle_pix_payment)
    trigger_system.register_handler('BLOCKCHAIN_TXID_RECEIVED', pix_monitor.handle_blockchain_txid)
    
    logger.info("✅ Handlers registrados com sucesso!")

def start_system():
    """Inicia o sistema completo"""
    logger.info("🚀 Iniciando sistema completo Ghost Bot...")
    
    # Inicializar sistema
    system = initialize_system()
    
    if not system:
        logger.error("❌ Falha na inicialização do sistema")
        return False
    
    # Iniciar componentes em background
    logger.info("🔄 Iniciando componentes em background...")
    
    try:
        # Iniciar monitor PIX
        system['pix_monitor'].start_monitoring()
        
        # Iniciar sistema de gatilhos
        system['trigger_system'].start()
        
        logger.info("✅ Sistema completo iniciado com sucesso!")
        logger.info("🎯 Sistema pronto para receber comandos!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar componentes: {e}")
        return False

def stop_system():
    """Para o sistema completo"""
    logger.info("🛑 Parando sistema Ghost Bot...")
    
    try:
        # Parar componentes específicos aqui se necessário
        logger.info("✅ Sistema parado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao parar sistema: {e}")

def main():
    """Função principal"""
    logger.info("🎯 Ghost Bot - Sistema Integrado")
    logger.info("=" * 50)
    
    try:
        # Iniciar sistema
        if start_system():
            logger.info("🎉 Sistema iniciado com sucesso!")
            logger.info("💡 Use /comprar no bot para testar o fluxo completo")
            
            # Manter o sistema rodando
            import time
            while True:
                time.sleep(60)
                logger.debug("🔄 Sistema rodando...")
                
        else:
            logger.error("❌ Falha ao iniciar sistema")
            
    except KeyboardInterrupt:
        logger.info("🛑 Interrupção do usuário detectada")
        stop_system()
        
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        stop_system()

if __name__ == "__main__":
    main()
