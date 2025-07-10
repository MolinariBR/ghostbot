#!/usr/bin/env python3
"""
Configurações específicas do sistema de gatilhos
"""
import os
from pathlib import Path
from enum import Enum

# Diretório base do trigger
TRIGGER_DIR = Path(__file__).parent.resolve()
BASE_DIR = TRIGGER_DIR.parent

class TriggerEvent(Enum):
    """Enumeração de eventos do sistema de gatilhos"""
    # Eventos do usuário
    USER_CLICKED_BUY = "user_clicked_buy"
    CURRENCY_SELECTED = "currency_selected"
    NETWORK_SELECTED = "network_selected"
    AMOUNT_ENTERED = "amount_entered"
    PAYMENT_METHOD_SELECTED = "payment_method_selected"
    
    # Eventos de pagamento
    PIX_PAYMENT_DETECTED = "pix_payment_detected"
    BLOCKCHAIN_TXID_RECEIVED = "blockchain_txid_received"
    PAYMENT_CONFIRMED = "payment_confirmed"
    
    # Eventos de endereço
    ADDRESS_PROVIDED = "address_provided"
    ADDRESS_VALIDATED = "address_validated"
    
    # Eventos de envio
    SEND_CRYPTO = "send_crypto"
    CRYPTO_SENT = "crypto_sent"
    TRANSACTION_COMPLETED = "transaction_completed"
    
    # Eventos de erro
    ERROR_OCCURRED = "error_occurred"
    INVALID_AMOUNT = "invalid_amount"
    INVALID_ADDRESS = "invalid_address"

class TriggerConfig:
    """Configurações do sistema de gatilhos"""
    
    # Timeouts
    DEFAULT_TIMEOUT = 30.0  # segundos
    PIX_MONITOR_INTERVAL = 5.0  # segundos
    LIGHTNING_TIMEOUT = 60.0  # segundos
    
    # Limites
    MIN_AMOUNT = 10.0  # R$ mínimo
    MAX_AMOUNT = 4999.99  # R$ máximo
    
    # Configurações de retry
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0  # segundos
    
    # Configurações de log
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = BASE_DIR / "logs" / "trigger.log"
    
    # Configurações de estado
    ACTIVE_ORDERS_TTL = 3600  # 1 hora em segundos
    
    # Configurações de rede
    SUPPORTED_CURRENCIES = ["bitcoin", "tether", "depix"]
    SUPPORTED_NETWORKS = {
        "bitcoin": ["lightning", "onchain", "liquid"],
        "tether": ["polygon", "liquid"],
        "depix": ["polygon"]
    }
    
    # Configurações de validação
    LIGHTNING_ADDRESS_REGEX = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    BITCOIN_ADDRESS_REGEX = r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$"
    
    # Configurações de webhook
    WEBHOOK_TIMEOUT = 30.0
    WEBHOOK_MAX_RETRIES = 3

class OrderStatus(Enum):
    """Status possíveis de um pedido"""
    CREATED = "created"
    CURRENCY_SELECTED = "currency_selected"
    NETWORK_SELECTED = "network_selected"
    AMOUNT_ENTERED = "amount_entered"
    PAYMENT_METHOD_SELECTED = "payment_method_selected"
    PIX_GENERATED = "pix_generated"
    PIX_PAID = "pix_paid"
    BLOCKCHAIN_TXID_RECEIVED = "blockchain_txid_received"
    ADDRESS_PROVIDED = "address_provided"
    CRYPTO_SENT = "crypto_sent"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class PaymentMethod(Enum):
    """Métodos de pagamento suportados"""
    PIX = "PIX"
    TED = "TED"
    BOLETO = "BOLETO"

# Configurações de desenvolvimento
DEV_CONFIG = {
    "debug": True,
    "mock_payments": False,
    "mock_lightning": False,
    "log_level": "DEBUG",
    "test_mode": False
}

# Configurações de produção
PROD_CONFIG = {
    "debug": False,
    "mock_payments": False,
    "mock_lightning": False,
    "log_level": "INFO",
    "test_mode": False
}

# Configuração atual (baseada na variável de ambiente)
CURRENT_CONFIG = DEV_CONFIG if os.getenv("ENVIRONMENT") == "development" else PROD_CONFIG

# Configurações de API
API_CONFIG = {
    "voltz_api_url": "https://lnvoltz.com/api/v1",
    "backend_url": "https://useghost.squareweb.app",
    "binance_api_url": "https://api.binance.com/api/v3",
    "coingecko_api_url": "https://api.coingecko.com/api/v3",
    "timeout": 30.0,
    "max_retries": 3
}

# Configurações de mensagens
MESSAGE_CONFIG = {
    "currency_selection": "💰 Escolha a criptomoeda:",
    "network_selection": "🌐 Escolha a rede:",
    "amount_request": "💵 Informe o valor da compra:",
    "payment_method": "💳 Escolha o método de pagamento:",
    "pix_generated": "📱 PIX gerado com sucesso!",
    "address_request": "📮 Informe seu endereço:",
    "transaction_completed": "🎉 Transação concluída!",
    "error_occurred": "❌ Erro:",
    "invalid_amount": "❌ Valor inválido!",
    "invalid_address": "❌ Endereço inválido!"
}

def get_config(key: str, default=None):
    """Obtém uma configuração específica"""
    return CURRENT_CONFIG.get(key, default)

def is_debug():
    """Verifica se está em modo debug"""
    return get_config("debug", False)

def is_test_mode():
    """Verifica se está em modo de teste"""
    return get_config("test_mode", False)
