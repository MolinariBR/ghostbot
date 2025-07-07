#!/usr/bin/env python3
"""
TESTE ESPECÍFICO LIGHTNING - Processamento direto via voltz_rest.php
===================================================================

Script para testar especificamente o processamento Lightning após correções.
"""

import requests
import json
import time

def criar_deposito_lightning_limpo():
    """Cria um depósito Lightning sem blockchainTxID para forçar processamento."""
    print("🆕 CRIANDO DEPÓSITO LIGHTNING LIMPO")
    print("=" * 40)
    
    url = "https://useghost.squareweb.app/rest/deposit.php"
    depix_id = f"clean_lightning_{int(time.time())}"
    
    # Dados mínimos sem blockchainTxID para forçar processamento
    payload = {
        "chatid": "7910260237",
        "user_id": 7910260237,
        "depix_id": depix_id,
        "status": "confirmado",
        "amount_in_cents": 300,  # R$ 3,00
        "moeda": "BTC", 
        "rede": "⚡ Lightning",
        "send": 600,  # 600 sats
        "taxa": 0.15,  # R$ 0,15
        "address": "voltzapi@tria.com",
        # NÃO incluir blockchainTxID para forçar processamento
        "metodo_pagamento": "PIX",
        "forma_pagamento": "PIX",
        "comprovante": "Teste Lightning Limpo - 600 sats",
        "action": "create"
    }
    
    print(f"📝 Depix ID: {depix_id}")
    print(f"💰 Valor: R$ 3,00 (600 sats)")
    print(f"🔗 SEM blockchainTxID (forçar processamento)")
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Depósito criado: {result}")
            return depix_id
        else:
            print(f"   ❌ Erro: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def testar_voltz_rest_detalhado(depix_id):
    """Testa o voltz_rest.php com logs detalhados."""
    print(f"\n⚡ TESTE VOLTZ REST DETALHADO")
    print("=" * 40)
    print(f"🎯 Depix ID: {depix_id}")
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    
    # Teste 1: GET simples
    print("\n1️⃣ Teste GET (processar todos)...")
    try:
        response = requests.get(url, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Resposta: {response.text}")
        
        if response.text.strip():
            try:
                data = json.loads(response.text)
                print(f"   📄 JSON: {json.dumps(data, indent=2)}")
            except:
                print(f"   📄 Texto: {repr(response.text)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 2: POST específico
    print(f"\n2️⃣ Teste POST específico para {depix_id}...")
    try:
        payload = {
            "action": "process_deposit",
            "depix_id": depix_id
        }
        
        response = requests.post(url, json=payload, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Resposta: {response.text}")
        
        if response.text.strip():
            try:
                data = json.loads(response.text)
                print(f"   📄 JSON: {json.dumps(data, indent=2)}")
                return data
            except:
                print(f"   📄 Texto: {repr(response.text)}")
        else:
            print("   ⚠️ Resposta vazia - possível erro no PHP")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    return None

def testar_check_balance():
    """Testa verificação de saldo do nó Lightning."""
    print(f"\n💰 TESTE CHECK BALANCE")
    print("=" * 40)
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    payload = {"action": "check_balance"}
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
        if response.text.strip():
            try:
                data = json.loads(response.text)
                print(f"   📄 Saldo: {json.dumps(data, indent=2)}")
                return data
            except:
                print(f"   📄 Texto: {repr(response.text)}")
        else:
            print("   ⚠️ Resposta vazia")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    return None

def verificar_logs_php():
    """Verifica logs PHP se disponíveis."""
    print(f"\n📋 VERIFICAÇÃO LOGS PHP")
    print("=" * 40)
    
    # Tentar acessar logs PHP
    log_urls = [
        "https://useghost.squareweb.app/voltz/error.log",
        "https://useghost.squareweb.app/logs/php_errors.log",
        "https://useghost.squareweb.app/logs/voltz_errors.log"
    ]
    
    for log_url in log_urls:
        try:
            print(f"   📡 Testando: {log_url}")
            response = requests.get(log_url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ Log encontrado: {response.text[-500:]}")  # Últimas 500 chars
            else:
                print(f"   📊 Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def main():
    print("🧪 TESTE ESPECÍFICO LIGHTNING - VOLTZ REST")
    print("=" * 50)
    
    # 1. Verificar saldo do nó primeiro
    balance_data = testar_check_balance()
    
    # 2. Criar depósito limpo
    depix_id = criar_deposito_lightning_limpo()
    
    if not depix_id:
        print("❌ Falha na criação do depósito - encerrando teste")
        return
    
    print(f"\n✅ Depósito criado: {depix_id}")
    
    # 3. Aguardar e processar
    print("\n⏱️ Aguardando 3 segundos...")
    time.sleep(3)
    
    # 4. Testar processamento detalhado
    result = testar_voltz_rest_detalhado(depix_id)
    
    # 5. Verificar logs se houver erro
    if not result or not result.get('success'):
        verificar_logs_php()
    
    # 6. Verificar status final
    print(f"\n🔍 VERIFICAÇÃO STATUS FINAL")
    print("=" * 40)
    
    try:
        status_url = "https://useghost.squareweb.app/voltz/voltz_status.php"
        payload = {"depix_id": depix_id}
        
        response = requests.post(status_url, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📄 Status: {data.get('status')}")
            
            if data.get('deposit', {}).get('blockchainTxID'):
                blockchainTxID = data['deposit']['blockchainTxID']
                print(f"   📋 TxID/Invoice: {blockchainTxID}")
                
                # Verificar se é um invoice Lightning válido
                if blockchainTxID.startswith('lnbc') or blockchainTxID.startswith('lntb'):
                    print(f"   ⚡ INVOICE LIGHTNING VÁLIDO ENCONTRADO!")
                    return True
                else:
                    print(f"   ⚠️ TxID não é invoice Lightning: {blockchainTxID}")
            else:
                print(f"   ❌ Nenhum TxID/Invoice encontrado")
        else:
            print(f"   ❌ Erro no status: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print(f"\n❌ Teste falhou - Invoice Lightning não foi gerado")
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 SUCESSO! Sistema Lightning funcionando corretamente")
    else:
        print(f"\n❌ FALHA: Sistema Lightning precisa de ajustes")
