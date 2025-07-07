#!/bin/bash

# Script para configurar cron job de monitoramento Lightning
# Executa a cada 30 segundos verificando PIX confirmados para Lightning

# Detecta automaticamente o diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BOT_DIR="$(dirname "$SCRIPT_DIR")"
SCRIPT_PATH="$BOT_DIR/cron_lightning_monitor.py"
LOG_FILE="$BOT_DIR/logs/lightning_cron.log"
VENV_PATH="$BOT_DIR/.venv"

# Cria diretório de logs se não existir
mkdir -p "$(dirname $LOG_FILE)"

# Verifica se o ambiente virtual existe
if [ ! -d "$VENV_PATH" ]; then
    echo "ERRO: Ambiente virtual não encontrado em $VENV_PATH" >> "$LOG_FILE"
    exit 1
fi

# Ativa o ambiente virtual e executa o script Python
cd "$BOT_DIR"
source "$VENV_PATH/bin/activate"
python "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1
