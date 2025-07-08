#!/bin/bash

echo "🎯 TESTE FINAL - Integração Voltz Completa"
echo "=========================================="

# Gerar ID único
DEPIX_ID="teste_final_$(date +%s)"
echo "🆔 ID do depósito: $DEPIX_ID"

echo ""
echo "1. 📝 Registrando depósito via REST API..."
REGISTER_RESULT=$(curl -s -X POST http://localhost:8000/rest/deposit.php \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"7910260237\",
    \"chatid\": \"test_final\",
    \"amount_in_cents\": 5000,
    \"taxa\": 0.05,
    \"moeda\": \"BTC\",
    \"rede\": \"lightning\",
    \"address\": \"voltz@mail.com\",
    \"forma_pagamento\": \"PIX\",
    \"send\": 90000,
    \"status\": \"pending\",
    \"depix_id\": \"$DEPIX_ID\"
  }")

echo "📊 Resultado: $REGISTER_RESULT"

if echo "$REGISTER_RESULT" | grep -q '"success":true'; then
    echo "✅ Depósito registrado com sucesso!"
    
    echo ""
    echo "2. 🔍 Consultando todos os depósitos para verificar..."
    DEPOSITS=$(curl -s "http://localhost:8000/rest/deposit.php")
    
    if echo "$DEPOSITS" | grep -q "\"$DEPIX_ID\""; then
        echo "✅ Depósito encontrado na base de dados!"
        
        # Extrair dados do depósito
        echo "📋 Dados do depósito:"
        echo "$DEPOSITS" | jq -r ".deposits[] | select(.depix_id == \"$DEPIX_ID\") | \"  • Status: \(.status)\", \"  • Valor: R$ \(.amount_in_cents/100)\", \"  • Sats: \(.send)\", \"  • Criado em: \(.created_at)\""
        
        echo ""
        echo "3. 🔧 Simulando processamento do backend Voltz..."
        echo "   (Em produção, o voltz_rest.php processaria automaticamente)"
        
        echo ""
        echo "🎊 TESTE CONCLUÍDO COM SUCESSO!"
        echo "✅ Bot pode registrar depósitos"
        echo "✅ Backend pode consultar depósitos"
        echo "✅ Fluxo de dados está correto"
        echo ""
        echo "📌 Próximos passos para produção:"
        echo "   1. Configurar cron job para voltz_rest.php"
        echo "   2. Testar geração real de invoices Lightning"
        echo "   3. Configurar webhook de notificação"
        
    else
        echo "❌ Depósito não encontrado na consulta"
    fi
    
else
    echo "❌ Falha no registro do depósito"
    echo "Detalhes: $REGISTER_RESULT"
fi
