#!/usr/bin/env python3
"""
DIAGNÓSTICO VOLTZ - Teste direto dos endpoints Lightning
========================================================

Script para diagnosticar problemas específicos no Voltz Lightning.
"""

import requests
import json
import time
import sys

def testar_conectividade():
    """Testa conectividade básica com o backend."""
    print("🌐 TESTE DE CONECTIVIDADE")
    print("=" * 40)
    
    endpoints = [
        "https://useghost.squareweb.app/ping",
        "https://useghost.squareweb.app/voltz/",
        "https://useghost.squareweb.app/voltz/voltz_rest.php",
        "https://useghost.squareweb.app/voltz/voltz_status.php"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"📡 Testando: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:100]}...")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        print("-" * 30)

def testar_voltz_rest():
    """Testa o endpoint voltz_rest.php com diferentes ações."""
    print("\n⚡ TESTE VOLTZ REST")
    print("=" * 40)
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    
    # Teste 1: GET simples
    print("1️⃣ Teste GET simples...")
    try:
        response = requests.get(url, timeout=15)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 2: POST com action=check_balance
    print("\n2️⃣ Teste verificação de saldo...")
    try:
        payload = {"action": "check_balance"}
        response = requests.post(url, json=payload, timeout=15)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 3: POST com action=process_deposits (geral)
    print("\n3️⃣ Teste processamento geral...")
    try:
        payload = {"action": "process_deposits"}
        response = requests.post(url, json=payload, timeout=20)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def testar_voltz_status():
    """Testa o endpoint voltz_status.php."""
    print("\n📊 TESTE VOLTZ STATUS")
    print("=" * 40)
    
    url = "https://useghost.squareweb.app/voltz/voltz_status.php"
    
    # Teste 1: GET simples
    print("1️⃣ Teste GET simples...")
    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 2: POST com depix_id de teste
    print("\n2️⃣ Teste status com depix_id...")
    try:
        payload = {"depix_id": "0197e0ed06537df9820a28f5a5380a3b"}
        response = requests.post(url, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def testar_deposit_api():
    """Testa o endpoint deposit.php para verificar depósitos."""
    print("\n💰 TESTE DEPOSIT API")
    print("=" * 40)
    
    # Teste busca por chat_id
    url = "https://useghost.squareweb.app/rest/deposit.php"
    chatid = "7910260237"
    
    print("1️⃣ Buscando depósitos por chat_id...")
    try:
        response = requests.get(f"{url}?chatid={chatid}", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            deposits = data.get('deposits', [])
            print(f"   📊 Depósitos encontrados: {len(deposits)}")
            
            # Mostra os 3 primeiros depósitos
            for i, dep in enumerate(deposits[:3]):
                print(f"   {i+1}. {dep.get('depix_id')} - {dep.get('status')} - R${dep.get('amount_in_cents', 0)/100:.2f}")
        else:
            print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def testar_criar_deposito_simples():
    """Cria um depósito simples para teste Lightning."""
    print("\n🆕 TESTE CRIAÇÃO DEPÓSITO SIMPLES")
    print("=" * 40)
    
    url = "https://useghost.squareweb.app/rest/deposit.php"
    
    # Dados mínimos para Lightning
    payload = {
        "chatid": "7910260237",
        "user_id": 7910260237,
        "depix_id": f"test_lightning_{int(time.time())}",
        "status": "confirmado",
        "amount_in_cents": 200,  # R$ 2,00 - valor muito baixo
        "moeda": "BTC", 
        "rede": "⚡ Lightning",
        "send": 400,  # 400 sats (~R$ 2,00)
        "taxa": 0.10,  # R$ 0,10
        "address": "voltzapi@tria.com",
        "blockchainTxID": f"lightning_test_{int(time.time())}",
        "metodo_pagamento": "PIX",
        "forma_pagamento": "PIX",
        "comprovante": "Teste Lightning - Valor baixo",
        "action": "create"
    }
    
    print(f"📝 Criando depósito de R$ 2,00 (400 sats)...")
    print(f"🆔 Depix ID: {payload['depix_id']}")
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Depósito criado: {result}")
            return payload['depix_id']
        else:
            print(f"   ❌ Erro: {response.text[:200]}...")
            return None
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def processar_deposito_lightning(depix_id):
    """Processa um depósito específico via Lightning."""
    print(f"\n⚡ PROCESSAMENTO LIGHTNING")
    print("=" * 40)
    print(f"🎯 Depix ID: {depix_id}")
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    
    # Teste processamento específico
    payload = {
        "action": "process_deposit",
        "depix_id": depix_id
    }
    
    print("🔄 Disparando processamento...")
    try:
        response = requests.post(url, json=payload, timeout=20)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def verificar_status_lightning(depix_id, max_tentativas=5):
    """Verifica status Lightning de um depósito."""
    print(f"\n🔍 VERIFICAÇÃO STATUS LIGHTNING")
    print("=" * 40)
    print(f"🎯 Depix ID: {depix_id}")
    
    url = "https://useghost.squareweb.app/voltz/voltz_status.php"
    
    for tentativa in range(1, max_tentativas + 1):
        print(f"\n📡 Tentativa {tentativa}/{max_tentativas}...")
        
        try:
            payload = {"depix_id": depix_id}
            response = requests.post(url, json=payload, timeout=15)
            
            print(f"   Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📄 Resposta JSON: {json.dumps(data, indent=2)}")
                    
                    if data.get('invoice'):
                        print(f"   ⚡ INVOICE ENCONTRADO!")
                        return data
                    else:
                        print(f"   ⏳ Invoice ainda não gerado...")
                except json.JSONDecodeError:
                    print(f"   📄 Resposta texto: {response.text}")
            else:
                print(f"   ❌ Erro HTTP: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        if tentativa < max_tentativas:
            print("   ⏱️ Aguardando 3 segundos...")
            time.sleep(3)
    
    print("⏰ Timeout - Invoice não gerado")
    return None

def main():
    print("🔍 DIAGNÓSTICO COMPLETO VOLTZ LIGHTNING")
    print("=" * 50)
    
    # 1. Testar conectividade básica
    testar_conectividade()
    
    # 2. Testar endpoints Voltz
    testar_voltz_rest()
    testar_voltz_status()
    
    # 3. Testar API de depósitos
    testar_deposit_api()
    
    # 4. Criar depósito de teste
    print("\n" + "="*50)
    print("🧪 TESTE COMPLETO - CRIAÇÃO E PROCESSAMENTO")
    print("="*50)
    
    depix_id = testar_criar_deposito_simples()
    
    if depix_id:
        print(f"\n✅ Depósito criado com sucesso: {depix_id}")
        
        # Aguardar um pouco
        print("⏱️ Aguardando 5 segundos...")
        time.sleep(5)
        
        # Processar Lightning
        if processar_deposito_lightning(depix_id):
            print("✅ Processamento Lightning iniciado")
            
            # Aguardar processamento
            print("⏱️ Aguardando 8 segundos para processamento...")
            time.sleep(8)
            
            # Verificar status
            resultado = verificar_status_lightning(depix_id)
            
            if resultado and resultado.get('invoice'):
                print(f"\n🎉 SUCESSO! Invoice Lightning gerado:")
                print(f"⚡ Invoice: {resultado['invoice']}")
                if resultado.get('qr_code'):
                    print(f"📱 QR Code: {resultado['qr_code']}")
            else:
                print(f"\n❌ FALHA: Invoice não foi gerado")
        else:
            print("❌ Falha no processamento Lightning")
    else:
        print("❌ Falha na criação do depósito")
    
    print(f"\n✅ Diagnóstico concluído")

if __name__ == "__main__":
    main()
