#!/usr/bin/env python3
"""
Teste específico do novo endpoint process_lightning_address.php
"""

import requests
import json
import time

def test_lightning_address_endpoint():
    """Testa o endpoint de processamento Lightning Address"""
    
    backend_url = "https://useghost.squareweb.app"
    endpoint = f"{backend_url}/api/process_lightning_address.php"
    
    print("🧪 TESTANDO ENDPOINT PROCESS_LIGHTNING_ADDRESS.PHP")
    print("=" * 60)
    
    # Teste 1: Lightning Address válido
    print("\n1. Testando Lightning Address válido...")
    payload1 = {
        "chat_id": "7910260237",
        "user_input": "bouncyflight79@walletofsatoshi.com"
    }
    
    try:
        response = requests.post(endpoint, json=payload1, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "-" * 40)
    
    # Teste 2: BOLT11 invoice válido (simulado)
    print("\n2. Testando BOLT11 invoice...")
    payload2 = {
        "chat_id": "7910260237", 
        "user_input": "lnbc35u1p5xafm7pp53at096yvk5x0synw5qpsgy4s72nqwn2gg9wa2p77l4"
    }
    
    try:
        response = requests.post(endpoint, json=payload2, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "-" * 40)
    
    # Teste 3: Input inválido
    print("\n3. Testando input inválido...")
    payload3 = {
        "chat_id": "7910260237",
        "user_input": "texto_invalido"
    }
    
    try:
        response = requests.post(endpoint, json=payload3, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "-" * 40)
    
    # Teste 4: Chat ID sem depósitos pendentes
    print("\n4. Testando chat ID sem depósitos...")
    payload4 = {
        "chat_id": "999999999",
        "user_input": "test@walletofsatoshi.com"
    }
    
    try:
        response = requests.post(endpoint, json=payload4, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_lightning_address_endpoint()
