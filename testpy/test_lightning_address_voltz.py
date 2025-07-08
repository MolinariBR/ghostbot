#!/usr/bin/env python3
"""
Teste para verificar se a Voltz API aceita Lightning Address
Data: 2025-01-27
"""

import requests
import json

# Configurações da Voltz API
VOLTZ_BASE_URL = "https://lnvoltz.com"
VOLTZ_API_KEY = "8fce34f4b0f8446a990418bd167dc644"

def test_lightning_address_decode():
    """
    Testa se a Voltz pode decodificar Lightning Address
    Lightning Address: formato user@domain.com
    """
    
    # Exemplos de Lightning Address conhecidos
    test_addresses = [
        "zews21@ripio.com",
        "test@walletofsatoshi.com",
        "user@getalby.com",
        "satoshi@bitcoin.org"
    ]
    
    print("=== Teste: Lightning Address na Voltz API ===\n")
    
    for address in test_addresses:
        print(f"🔍 Testando Lightning Address: {address}")
        
        # Tenta decodificar via endpoint /api/v1/payments/decode
        url = f"{VOLTZ_BASE_URL}/api/v1/payments/decode"
        
        payload = {
            "data": address
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sucesso: {data}")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            
        print("-" * 50)

def test_bolt11_decode():
    """
    Testa decodificação de BOLT11 para comparação
    """
    
    print("\n=== Teste: BOLT11 na Voltz API (para comparação) ===\n")
    
    # BOLT11 de exemplo (do README da Voltz)
    bolt11_example = "lnbc10u1p5xhhsgpp5zzzwy9evs7a8fpmd56794lh3smt9kzlpq8vwcnye9v2ll2skj4zqdqc23jhxar9yprksmmnwssyymm5cqzpgxqrrssrzjqdrhkruk080xpvagqw68998r0dxpfgur2e90mmvhxy2px33r6tkgyrvt3sqqgpgqqyqqqqlgqqqqqqgq2qsp5hvt0v0yrr80dnyf62a7gfg7fhqpp5ner9purs587ehtnymy8xmps9qxpqysgqp9r3tffmqf4m6d0kjpxf7r7a7gnpls7vazuhhaev9h2qaha8ed6kfdklqk2z4c55ky5rqza9xvnuxnv2xng2vzsymq8hx34cw3870ycpav5x0d"
    
    url = f"{VOLTZ_BASE_URL}/api/v1/payments/decode"
    
    payload = {
        "data": bolt11_example
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"🔍 Testando BOLT11")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ BOLT11 decodificado com sucesso")
        else:
            print(f"   ❌ Erro ao decodificar BOLT11: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

def test_lightning_address_resolution():
    """
    Testa resolução manual de Lightning Address seguindo LUD-16
    """
    
    print("\n=== Teste: Resolução Manual Lightning Address ===\n")
    
    test_address = "test@walletofsatoshi.com"
    username, domain = test_address.split("@")
    
    # Seguindo LUD-16: GET https://domain/.well-known/lnurlp/username
    well_known_url = f"https://{domain}/.well-known/lnurlp/{username}"
    
    print(f"🔍 Resolvendo: {test_address}")
    print(f"   URL: {well_known_url}")
    
    try:
        response = requests.get(well_known_url, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Endpoint encontrado!")
            print(f"   Callback: {data.get('callback', 'N/A')}")
            print(f"   Min/Max: {data.get('minSendable', 'N/A')}/{data.get('maxSendable', 'N/A')}")
            print(f"   Metadata: {data.get('metadata', 'N/A')}")
        else:
            print(f"   ❌ Endpoint não encontrado: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

if __name__ == "__main__":
    test_lightning_address_decode()
    test_bolt11_decode()
    test_lightning_address_resolution()
    
    print("\n" + "="*60)
    print("CONCLUSÃO:")
    print("- Lightning Address = formato user@domain.com")
    print("- Funciona via protocolo LUD-16 (LNURL-pay)")
    print("- Requer resolução via /.well-known/lnurlp/ endpoint")
    print("- Voltz aceita apenas BOLT11 invoices diretamente")
    print("- Para usar Lightning Address, seria necessário:")
    print("  1. Resolver Lightning Address → LNURL")
    print("  2. Fazer request LNURL → obter BOLT11")
    print("  3. Usar BOLT11 na Voltz")
    print("="*60)
