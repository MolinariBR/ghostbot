#!/usr/bin/env python3
"""
Setup de Produção - Sistema de Gatilhos Ghost Bot
Configura e ativa o sistema completo de gatilhos para produção
"""
import sys
import os
import logging
from pathlib import Path

# Adicionar diretório principal ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar logging específico para produção
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mau/bot/ghost/logs/production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('production_setup')

def setup_production_environment():
    """Configura o ambiente de produção para o sistema de gatilhos"""
    logger.info("🚀 Configurando ambiente de produção...")
    
    try:
        # Importar todos os módulos necessários
        from trigger import trigger_system, TriggerEvent, OrderStatus
        from trigger.integrador_bot_gatilhos import BotTriggerIntegrator, TriggerUIImplementation
        from trigger.smart_pix_monitor import SmartPixMonitor
        from trigger.lightning_handler import LightningHandler
        from trigger.production_integration import setup_trigger_integration
        
        logger.info("✅ Todos os módulos importados com sucesso")
        
        # Retornar configuração de produção
        return {
            'trigger_system': trigger_system,
            'TriggerEvent': TriggerEvent,
            'OrderStatus': OrderStatus,
            'BotTriggerIntegrator': BotTriggerIntegrator,
            'TriggerUIImplementation': TriggerUIImplementation,
            'SmartPixMonitor': SmartPixMonitor,
            'LightningHandler': LightningHandler,
            'setup_trigger_integration': setup_trigger_integration
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar ambiente de produção: {e}", exc_info=True)
        raise

def activate_production_system(application):
    """Ativa o sistema de gatilhos em produção"""
    logger.info("⚡ Ativando sistema de gatilhos em produção...")
    
    try:
        # Configurar ambiente
        production_config = setup_production_environment()
        
        # Configurar integração
        setup_trigger_integration = production_config['setup_trigger_integration']
        integrator = setup_trigger_integration(application)
        
        if integrator:
            logger.info("✅ Sistema de gatilhos ativado com sucesso em produção!")
            return integrator
        else:
            logger.error("❌ Falha ao ativar sistema de gatilhos")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao ativar sistema de produção: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    # Teste do setup de produção
    logger.info("🧪 Testando setup de produção...")
    
    try:
        config = setup_production_environment()
        logger.info("✅ Setup de produção funcionando corretamente!")
        logger.info(f"Trigger System: {config['trigger_system']}")
        logger.info(f"Eventos: {len(list(config['TriggerEvent']))}")
        logger.info(f"Status: {len(list(config['OrderStatus']))}")
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de produção: {e}", exc_info=True)
        sys.exit(1)
