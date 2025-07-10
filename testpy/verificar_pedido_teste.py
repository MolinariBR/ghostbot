#!/usr/bin/env python3
"""
Verificação específica do pedido criado no teste
"""

import requests
import json

def verificar_pedido_especifico():
    backend_url = "https://useghost.squareweb.app"
    depix_id = "DEPIX_7910260237_1752083255"  # Do teste que acabou de rodar
    pedido_id = "48"
    
    print("🔍 VERIFICAÇÃO ESPECÍFICA DO PEDIDO TESTE")
    print("=" * 50)
    print(f"📋 Pedido ID: {pedido_id}")
    print(f"🆔 Depix ID: {depix_id}")
    print("=" * 50)
    
    # 1. Verificar por ID
    print("\n1. 📋 CONSULTA POR ID:")
    try:
        response = requests.get(f"{backend_url}/rest/deposit.php?action=get&id={pedido_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Encontrado por ID:")
            print(f"   Status: {data.get('status')}")
            print(f"   Address: {data.get('address')}")
            print(f"   blockchainTxID: {data.get('blockchainTxID')}")
            print(f"   Criado: {data.get('created_at')}")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 2. Verificar por Depix ID
    print("\n2. 🆔 CONSULTA POR DEPIX_ID:")
    try:
        response = requests.get(f"{backend_url}/rest/deposit.php?action=get&depix_id={depix_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Encontrado por Depix ID:")
            print(f"   Status: {data.get('status')}")
            print(f"   Address: {data.get('address')}")
            print(f"   blockchainTxID: {data.get('blockchainTxID')}")
            print(f"   Rede: {data.get('rede')}")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 3. Verificar fila de fallback
    print("\n3. 📋 CONSULTA FILA DE FALLBACK:")
    try:
        response = requests.get(f"{backend_url}/voltz/voltz_fallback.php?action=list", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('queue'):
                print(f"✅ Items na fila: {len(data['queue'])}")
                for item in data['queue']:
                    if item.get('depix_id') == depix_id:
                        print(f"   🎯 Nosso pedido encontrado na fila!")
                        print(f"      Status: {item.get('status')}")
                        print(f"      Tentativas: {item.get('attempts')}")
                        print(f"      Último erro: {item.get('last_error')}")
            else:
                print("✅ Fila vazia")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 4. Testar processamento direto via endpoint Lightning
    print("\n4. ⚡ TESTE DO ENDPOINT LIGHTNING:")
    try:
        payload = {
            "chat_id": "7910260237",
            "user_input": "bouncyflight79@walletofsatoshi.com"
        }
        response = requests.post(f"{backend_url}/api/process_lightning_address.php", json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2)}")
        else:
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_pedido_especifico()
