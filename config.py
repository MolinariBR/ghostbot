"""
Configurações do bot e constantes globais.
"""
import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent.resolve()

# Configurações do bot
class BotConfig:
    # Timeouts e tentativas
    REQUEST_TIMEOUT = 30.0  # segundos
    MAX_RETRIES = 5
    BASE_RETRY_DELAY = 5  # segundos
    
    # Configurações de polling
    POLLING_TIMEOUT = 30  # segundos
    READ_LATENCY = 2.0  # segundos
    BOOTSTRAP_RETRIES = 3
    
    # Configurações de conexão
    CONNECTION_TIMEOUT = 30.0
    READ_TIMEOUT = 30.0
    POOL_TIMEOUT = 30.0
    MAX_RETRIES = 3
    
    # Outras configurações
    DROP_PENDING_UPDATES = True

# Configurações de log
class LogConfig:
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = BASE_DIR / "logs" / "bot.log"
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5

# O diretório de logs será criado pelo manipulador de log no bot.py
