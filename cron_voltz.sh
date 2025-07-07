#!/bin/bash

# Script para executar o processamento Voltz via cron job
# Para servidor: https://useghost.squareweb.app/

echo "[$(date)] Iniciando processamento Voltz..." >> /tmp/voltz_cron.log

# Executar o processamento via URL
curl -s -X GET "https://useghost.squareweb.app/voltz/voltz_rest.php" >> /tmp/voltz_cron.log 2>&1

echo "[$(date)] Processamento Voltz finalizado" >> /tmp/voltz_cron.log
