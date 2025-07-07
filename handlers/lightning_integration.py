"""
Integração Lightning Network - Handler para processamento automático de invoices
"""
import logging

logger = logging.getLogger(__name__)

def setup_lightning_integration(application):
    """
    Configura a integração Lightning Network.
    
    Args:
        application: A aplicação do bot Telegram
    """
    logger.info("✅ Integração Lightning configurada - usando fluxo PIX → Voltz automático")
    
    # A integração Lightning agora funciona via:
    # 1. PIX payment → Depix webhook
    # 2. Voltz cron job detecta pagamento confirmado
    # 3. Voltz gera invoice Lightning automaticamente
    # 4. fluxo_envio_invoice.py envia invoice para o usuário
    
    return True
