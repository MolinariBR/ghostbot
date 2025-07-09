#!/usr/bin/env python3
"""
Teste direto de criação de depósito no banco
"""

import requests
import json
import time

def teste_criacao_deposito():
    """Testa criação direta de depósito"""
    
    depix_id = f"TESTE_DIRETO_{int(time.time())}"
    
    payload = {
        "chatid": "7910260237",
        "moeda": "BTC",
        "rede": "⚡ Lightning",
        "amount_in_cents": 500,
        "taxa": 5.0,
        "address": "test@walletofsatoshi.com",
        "forma_pagamento": "PIX",
        "send": 0.000014,
        "user_id": 7910260237,
        "depix_id": depix_id,
        "status": "pending",
        "comprovante": "Teste Direto"
    }
    
    print("🧪 TESTE CRIAÇÃO DE DEPÓSITO")
    print("=" * 50)
    print(f"📋 depix_id: {depix_id}")
    print(f"💰 Valor: R$ 5,00")
    print(f"⚡ Rede: Lightning")
    
    try:
        print("\n📤 Enviando requisição...")
        
        response = requests.post(
            "https://useghost.squareweb.app/rest/deposit.php",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📊 Status HTTP: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON válido: {json.dumps(data, indent=2)}")
                
                if data.get("success"):
                    print(f"🎉 Depósito criado com sucesso!")
                    print(f"📋 ID: {data.get('id')}")
                    return True
                else:
                    print(f"❌ Erro na criação: {data}")
                    
            except json.JSONDecodeError:
                print("⚠️ Resposta não é JSON válido")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    return False

if __name__ == "__main__":
    teste_criacao_deposito()
