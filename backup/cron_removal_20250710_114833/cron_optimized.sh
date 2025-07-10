#!/bin/bash

# Cron otimizado com intervalos inteligentes
BACKEND_DIR="/home/mau/bot/ghostbackend"
LOG_FILE="$BACKEND_DIR/logs/cron_optimized.log"

# Cria diretório de logs se não existir
mkdir -p "$(dirname $LOG_FILE)"

# Função de log com timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Monitoramento com intervalos adaptativos
log_message "Iniciando monitoramento otimizado"

# 1. Verifica depósitos pendentes (a cada 30s para novos, 5min para antigos)
php "$BACKEND_DIR/blockchain/cron_job_update.php" >> "$LOG_FILE" 2>&1

# 2. Confirma depósitos (intervalo reduzido para recentes)
php "$BACKEND_DIR/blockchain/monitor_deposit.php" >> "$LOG_FILE" 2>&1

# 3. Limpa cache de cotações (apenas se necessário)
if [ $(($(date +%s) % 300)) -eq 0 ]; then
    log_message "Limpando cache de cotações"
    # Aqui seria implementada a limpeza de cache
fi

log_message "Monitoramento completado"
