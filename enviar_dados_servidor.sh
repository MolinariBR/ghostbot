#!/bin/bash

# Script para enviar dados do banco local para o servidor de produção
BACKEND_URL="https://useghost.squareweb.app/api/registrar_transacao.php"
DB_PATH="data/deposit.db"
LOG_FILE="logs/envio_servidor.log"

echo "🚀 Iniciando envio de dados para o servidor de produção..."
echo "📊 URL do servidor: $BACKEND_URL"
echo "📁 Banco de dados local: $DB_PATH"

# Verificar se o banco existe
if [ ! -f "$DB_PATH" ]; then
    echo "❌ Erro: Banco de dados não encontrado em $DB_PATH"
    exit 1
fi

# Criar diretório de logs se não existir
mkdir -p logs

# Função para log
log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_msg "=== INÍCIO DO ENVIO PARA O SERVIDOR ==="

# Contar total de transações
TOTAL=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM pedidos_bot;")
log_msg "📊 Total de transações no banco local: $TOTAL"

# Exportar transações para JSON
log_msg "📤 Exportando transações para JSON..."
sqlite3 "$DB_PATH" "SELECT json_object(
    'gtxid', gtxid,
    'chatid', chatid,
    'moeda', moeda,
    'rede', rede,
    'valor', valor,
    'comissao', comissao,
    'parceiro', parceiro,
    'cotacao', cotacao,
    'recebe', recebe,
    'forma_pagamento', forma_pagamento,
    'depix_id', COALESCE(depix_id, ''),
    'blockchainTxID', COALESCE(blockchainTxID, ''),
    'status', COALESCE(status, 'novo'),
    'pagamento_verificado', COALESCE(pagamento_verificado, 0),
    'tentativas_verificacao', COALESCE(tentativas_verificacao, 0),
    'criado_em', COALESCE(criado_em, datetime('now')),
    'atualizado_em', COALESCE(atualizado_em, datetime('now'))
) FROM pedidos_bot;" > transacoes_servidor.json

# Contar linhas no arquivo JSON
LINES=$(wc -l < transacoes_servidor.json)
log_msg "📄 Arquivo JSON criado com $LINES linhas"

# Enviar cada transação individualmente para o servidor
SUCCESS=0
ERROR=0

while IFS= read -r line; do
    if [ -n "$line" ]; then
        log_msg "📤 Enviando transação para servidor: $line"
        
        # Enviar via curl para o servidor
        RESPONSE=$(curl -s -w "%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$line" \
            "$BACKEND_URL")
        
        HTTP_CODE="${RESPONSE: -3}"
        BODY="${RESPONSE%???}"
        
        if [ "$HTTP_CODE" = "200" ]; then
            log_msg "✅ Sucesso (HTTP $HTTP_CODE): $BODY"
            ((SUCCESS++))
        else
            log_msg "❌ Erro (HTTP $HTTP_CODE): $BODY"
            ((ERROR++))
        fi
        
        # Pequena pausa para não sobrecarregar o servidor
        sleep 1
    fi
done < transacoes_servidor.json

# Limpar arquivo temporário
rm -f transacoes_servidor.json

# Resumo final
log_msg "=== RESUMO DO ENVIO PARA O SERVIDOR ==="
log_msg "✅ Transações enviadas com sucesso: $SUCCESS"
log_msg "❌ Transações com erro: $ERROR"
log_msg "📊 Total processado: $((SUCCESS + ERROR))"
log_msg "=== FIM DO ENVIO PARA O SERVIDOR ==="

echo ""
echo "🎉 Envio para o servidor concluído!"
echo "✅ Sucessos: $SUCCESS"
echo "❌ Erros: $ERROR"
echo "📋 Log completo em: $LOG_FILE"

if [ "$SUCCESS" -eq "$TOTAL" ]; then
    echo "✅ Todas as transações foram enviadas com sucesso!"
else
    echo "⚠️  Algumas transações falharam. Verifique o log para detalhes."
fi 