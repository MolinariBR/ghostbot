#!/bin/bash

echo "🧪 Teste Completo da Integração Voltz via cURL"
echo "=============================================="

# Gerar ID único
DEPIX_ID="voltz_$(date +%s)_$RANDOM"
echo "🆔 ID do depósito: $DEPIX_ID"

echo ""
echo "1. 📝 Registrando depósito..."
REGISTER_RESULT=$(curl -s -X POST http://localhost:8000/rest/deposit.php \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"7910260237\",
    \"chatid\": \"test_chat_123\",
    \"amount_in_cents\": 2500,
    \"taxa\": 0.05,
    \"moeda\": \"BTC\",
    \"rede\": \"lightning\",
    \"address\": \"voltz@mail.com\",
    \"forma_pagamento\": \"PIX\",
    \"send\": 45000,
    \"status\": \"pending\",
    \"depix_id\": \"$DEPIX_ID\"
  }")

echo "📊 Resultado do registro: $REGISTER_RESULT"

# Verificar se foi bem-sucedido
if echo "$REGISTER_RESULT" | grep -q '"success":true'; then
    echo "✅ Depósito registrado com sucesso!"
    
    echo ""
    echo "2. ⏳ Aguardando processamento (10 segundos)..."
    sleep 10
    
    echo ""
    echo "3. 🔍 Verificando status do depósito..."
    STATUS_RESULT=$(curl -s "http://localhost:8000/api/bot_update_status.php?depix_id=$DEPIX_ID")
    echo "📊 Status: $STATUS_RESULT"
    
    if echo "$STATUS_RESULT" | grep -q '"invoice"'; then
        echo "⚡ Invoice encontrado no status!"
        
        # Extrair invoice se existir
        INVOICE=$(echo "$STATUS_RESULT" | sed -n 's/.*"invoice":"\([^"]*\)".*/\1/p')
        if [ ! -z "$INVOICE" ]; then
            echo ""
            echo "🎉 SUCESSO! Invoice Lightning gerado:"
            echo "⚡ $INVOICE"
            echo ""
            echo "✅ INTEGRAÇÃO FUNCIONANDO PERFEITAMENTE!"
        fi
    else
        echo "⏳ Invoice ainda não gerado. Status atual:"
        echo "$STATUS_RESULT"
    fi
    
else
    echo "❌ Falha no registro do depósito"
    echo "Resposta: $REGISTER_RESULT"
fi

echo ""
echo "🏁 Teste finalizado."
