#!/usr/bin/env python3
"""
Corrigir status do pedido para testar processamento Lightning
"""

import requests
import json

def corrigir_status_pedido():
    backend_url = "https://useghost.squareweb.app"
    depix_id = "DEPIX_7910260237_1752083255"
    
    print("🔧 CORRIGINDO STATUS DO PEDIDO PARA TESTE")
    print("=" * 50)
    
    # Tentar atualizar status para "confirmado"
    try:
        # Método 1: Via webhook Depix (simulando confirmação PIX real)
        print("1. 📋 Simulando confirmação PIX via webhook...")
        webhook_payload = {
            "id": depix_id,
            "status": "paid",
            "payment_method": "pix",
            "amount": 500,  # R$ 5.00
            "currency": "BRL"
        }
        
        response = requests.post(
            f"{backend_url}/square_webhook.php",
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Status webhook: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        # Aguardar um pouco
        import time
        time.sleep(5)
        
        # Verificar se o status mudou
        print("\n2. 🔍 Verificando status após webhook...")
        response = requests.get(f"{backend_url}/rest/deposit.php?action=get&depix_id={depix_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status atual: {data.get('status')}")
            
            # Se mudou para "confirmado", tentar processar Lightning
            if data.get('status') in ['confirmado', 'confirmed', 'paid']:
                print("\n3. ⚡ Tentando processar Lightning agora...")
                lightning_payload = {
                    "chat_id": "7910260237",
                    "user_input": "bouncyflight79@walletofsatoshi.com"
                }
                
                response = requests.post(
                    f"{backend_url}/api/process_lightning_address.php",
                    json=lightning_payload,
                    timeout=15
                )
                
                print(f"Status Lightning: {response.status_code}")
                print(f"Resposta: {response.text}")
            else:
                print(f"⚠️ Status ainda é: {data.get('status')}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    corrigir_status_pedido()
