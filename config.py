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
    REQUEST_TIMEOUT = 60.0  # segundos
    MAX_RETRIES = 15  # Número máximo de tentativas de reconexão
    BASE_RETRY_DELAY = 5  # segundos
    
    # Configurações de polling (otimizadas para SquareCloud)
    POLLING_TIMEOUT = 60.0  # Aumentado para reduzir requests
    READ_LATENCY = 30.0     # Aumentado para menos overhead
    BOOTSTRAP_RETRIES = 3   # Tentativas de inicialização
    
    # Configurações de conexão (otimizadas)
    CONNECTION_TIMEOUT = 30.0  # Reduzido para conexões mais rápidas
    READ_TIMEOUT = 30.0        # Reduzido para menos espera
    WRITE_TIMEOUT = 30.0       # Reduzido para menos espera
    POOL_TIMEOUT = 30.0        # Reduzido para menos espera
    POOL_SIZE = 5              # Reduzido para menos conexões simultâneas
    
    # Configurações de reconexão (otimizadas)
    MAX_POLLING_RETRIES = 5    # Reduzido para menos tentativas
    MAX_RECONNECT_ATTEMPTS = 3 # Reduzido para menos tentativas
    
    # Outras configurações
    DROP_PENDING_UPDATES = True
    ALLOWED_UPDATES = ["message", "callback_query"]  # Apenas essenciais
    POLL_INTERVAL = 2.0  # Intervalo entre polls para reduzir CPU
    
    @classmethod
    def get_retry_delay(cls, attempt: int) -> float:
        """
        Retorna o tempo de espera para reconexão com backoff exponencial.
        
        Args:
            attempt: Número da tentativa atual
            
        Returns:
            float: Tempo de espera em segundos (máximo 300s/5min)
        """
        return min(cls.BASE_RETRY_DELAY * (2 ** (attempt - 1)), 300)  # Máximo 5 minutos

# Configurações de log
class LogConfig:
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = BASE_DIR / "logs" / "bot.log"
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5

# O diretório de logs será criado pelo manipulador de log no bot.py
