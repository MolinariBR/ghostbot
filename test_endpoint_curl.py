#!/usr/bin/env python3
"""
Teste simples via Python para verificar se o endpoint está funcionando
"""
import requests
import json
import time

def test_endpoint():
    print("🧪 Testando endpoint Lightning Address via Python...")
    
    url = "https://useghost.squareweb.app/api/process_lightning_address.php"
    
    data = {
        'chat_id': '7910260237',
        'user_input': 'test@getalby.com'
    }
    
    try:
        print(f"📡 Fazendo requisição para: {url}")
        print(f"📋 Data: {data}")
        
        start_time = time.time()
        response = requests.post(url, json=data, timeout=15)
        end_time = time.time()
        
        print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f}s")
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ JSON válido: {result}")
            except:
                print("❌ JSON inválido")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - Endpoint demorou mais que 15s")
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_endpoint()
