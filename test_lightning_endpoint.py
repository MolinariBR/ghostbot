#!/usr/bin/env python3
"""
Teste específico do endpoint process_lightning_address.php
Valida se o backend processa corretamente o Lightning Address digitado pelo usuário
"""
import requests
import json
import time

def test_process_lightning_address():
    """Testa o endpoint process_lightning_address.php"""
    
    print("🧪 TESTE: Endpoint process_lightning_address.php")
    print("=" * 60)
    
    backend_url = "https://useghost.squareweb.app"
    endpoint = f"{backend_url}/api/process_lightning_address.php"
    
    # Dados de teste
    chat_id = "7910260237"
    lightning_address = "bouncyflight79@walletofsatoshi.com"
    
    print(f"🌐 Endpoint: {endpoint}")
    print(f"👤 Chat ID: {chat_id}")
    print(f"⚡ Lightning Address: {lightning_address}")
    
    # Payload para teste
    payload = {
        "chat_id": chat_id,
        "user_input": lightning_address
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"\n🔄 Enviando requisição...")
        print(f"📤 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📨 RESPOSTA:")
        print(f"   🌐 Status: {response.status_code}")
        print(f"   📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ JSON: {json.dumps(data, indent=2)}")
                
                if data.get('success'):
                    print(f"\n🎉 SUCESSO: Lightning Address processado!")
                    if 'payment_hash' in data:
                        print(f"   🔑 Payment Hash: {data['payment_hash']}")
                    if 'amount_paid_sats' in data:
                        print(f"   💰 Sats enviados: {data['amount_paid_sats']}")
                    return True
                else:
                    print(f"\n❌ ERRO: {data.get('error', 'Erro desconhecido')}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"   ❌ Resposta não é JSON válido: {response.text}")
                return False
        
        elif response.status_code == 404:
            print(f"\n❌ ENDPOINT NÃO ENCONTRADO")
            print(f"💡 Verifique se o arquivo existe: {endpoint}")
            return False
            
        elif response.status_code == 500:
            print(f"\n❌ ERRO INTERNO DO SERVIDOR")
            print(f"📋 Resposta: {response.text}")
            return False
            
        else:
            print(f"\n❌ HTTP {response.status_code}")
            print(f"📋 Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERRO DE CONEXÃO")
        print(f"💡 Servidor pode estar offline ou URL incorreta")
        return False
        
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT")
        print(f"💡 Servidor demorou mais de 30s para responder")
        return False
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        return False

def test_endpoint_availability():
    """Testa se o endpoint está acessível"""
    
    print("\n🔍 TESTE: Disponibilidade do endpoint")
    print("-" * 40)
    
    backend_url = "https://useghost.squareweb.app"
    
    # Lista de endpoints para testar
    endpoints = [
        f"{backend_url}/api/process_lightning_address.php",
        f"{backend_url}/rest/deposit.php",
        f"{backend_url}/square_webhook.php",
        f"{backend_url}/depix/webhook.php"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testando: {endpoint}")
            
            # Para endpoints POST, usa OPTIONS primeiro
            response = requests.options(endpoint, timeout=10)
            
            if response.status_code in [200, 204, 405]:  # 405 = Method Not Allowed é OK
                print(f"   ✅ Endpoint acessível (HTTP {response.status_code})")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erro de conexão")
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 TESTE DO BACKEND - LIGHTNING ADDRESS")
    print("=" * 70)
    
    # 1. Testa disponibilidade geral
    test_endpoint_availability()
    
    # 2. Testa endpoint específico
    print("\n" + "=" * 70)
    success = test_process_lightning_address()
    
    # 3. Resultado final
    print("\n" + "=" * 70)
    print("🎯 RESULTADO FINAL:")
    
    if success:
        print("✅ Endpoint process_lightning_address.php funcionando!")
        print("🔄 Lightning Address Handler pode ser integrado ao bot")
    else:
        print("❌ Endpoint com problemas")
        print("🔧 Verificar implementação no backend")
        
    print("=" * 70)
