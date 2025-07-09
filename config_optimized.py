#!/usr/bin/env python3
"""
Otimizações para Polling - Reduz sobrecarga do servidor
Melhorias no bot.py para usar menos recursos com polling.
"""

# Configurações otimizadas para polling
class OptimizedBotConfig:
    # Timeouts otimizados
    POLLING_TIMEOUT = 60.0  # Aumentado para reduzir requests
    READ_LATENCY = 30.0     # Aumentado para menos overhead
    
    # Conexões otimizadas
    CONNECTION_TIMEOUT = 30.0
    READ_TIMEOUT = 30.0
    WRITE_TIMEOUT = 30.0
    POOL_SIZE = 5           # Reduzido para menos conexões
    
    # Polling otimizado
    POLL_INTERVAL = 2.0     # Intervalo entre polls
    MAX_RETRIES = 5         # Menos tentativas
    
    # Updates otimizados
    ALLOWED_UPDATES = ["message", "callback_query"]  # Apenas essenciais
    DROP_PENDING_UPDATES = True  # Ignora mensagens antigas
    
    # Configurações de economia
    ENABLE_PERSISTENCE = False  # Desabilita persistência se não necessária
    WRITE_TIMEOUT_REDUCED = 20.0
    CONNECT_TIMEOUT_REDUCED = 20.0

# Exemplo de uso no bot.py
"""
# Substituir as configurações atuais por estas otimizadas
from config_optimized import OptimizedBotConfig as BotConfig

# No main() do bot.py
await updater.start_polling(
    drop_pending_updates=BotConfig.DROP_PENDING_UPDATES,
    allowed_updates=BotConfig.ALLOWED_UPDATES,
    timeout=BotConfig.POLLING_TIMEOUT,
    bootstrap_retries=3,
    read_latency=BotConfig.READ_LATENCY,
    poll_interval=BotConfig.POLL_INTERVAL
)
"""
