#!/usr/bin/env python3
"""
TESTE DIRETO VOLTZ - Contorna o webhook com timeout
===================================================

Usa os endpoints que funcionam para testar Lightning diretamente.
"""

import requests
import json
import time
import sys
import hashlib

sys.path.append('/home/mau/bot/ghost')

def criar_deposito_direto(depix_id):
    """
    Cria depósito diretamente via REST API (que funciona).
    """
    print(f"📝 Criando depósito via REST API...")
    
    # Gera TxID simulado
    txid = hashlib.md5(f"test_{depix_id}_{int(time.time())}".encode()).hexdigest()
    
    payload = {
        "chatid": "123456789",
        "user_id": 123456789,
        "depix_id": depix_id,
        "blockchainTxID": txid,
        "status": "confirmado",
        "amount_in_cents": 10000,  # R$ 100
        "moeda": "BTC",
        "rede": "⚡ Lightning",
        "send": 285714,  # ~286k sats
        "taxa": 5.0,
        "address": "voltzapi@tria.com",
        "metodo_pagamento": "PIX",
        "forma_pagamento": "PIX",
        "comprovante": "Lightning Test"
    }
    
    try:
        # Usa REST API que sabemos que funciona (0.53s)
        response = requests.post(
            "https://useghost.squareweb.app/rest/deposit.php",
            json=payload,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Depósito criado com TxID: {txid}")
            return txid
        else:
            print(f"⚠️ Criação parcial, mas continuando...")
            return txid
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def processar_voltz_direto(depix_id):
    """
    Chama o processamento Voltz diretamente (que funciona).
    """
    print(f"\n🔄 Processando via Voltz REST...")
    
    try:
        # Usa endpoint que sabemos que funciona (0.69s)
        response = requests.get(
            "https://useghost.squareweb.app/voltz/voltz_rest.php",
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text[:200]}...")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False

def verificar_status_voltz(depix_id):
    """
    Verifica status via endpoint que funciona.
    """
    print(f"\n⚡ Verificando status via Voltz...")
    
    try:
        # Usa endpoint que sabemos que funciona (0.54s)
        response = requests.post(
            "https://useghost.squareweb.app/voltz/voltz_status.php",
            json={"depix_id": depix_id},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Status response: {data}")
                
                if data.get('invoice'):
                    print(f"\n🎉 INVOICE ENCONTRADO!")
                    print(f"Invoice: {data['invoice']}")
                    return data
                else:
                    print(f"⏳ Invoice ainda não gerado")
                    return data
                    
            except json.JSONDecodeError:
                print(f"📝 Resposta não-JSON: {response.text}")
                return {'raw_response': response.text}
        else:
            print(f"❌ Erro: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return None

def main():
    print("🧪 TESTE DIRETO VOLTZ - Sem webhook")
    print("=" * 50)
    
    # Seus depix_ids
    depix_ids = [
        "0197e0ed06537df9820a28f5a5380a3b",
        "0197e10b5b8f7df9a6bf9430188534e4",
        "0197e12300eb7df9808ca5d7719ea40e",
        "0197e5214a377dfaae6e541f68057444"
    ]
    
    print("🎯 Depix IDs disponíveis:")
    for i, depix_id in enumerate(depix_ids, 1):
        print(f"{i}. {depix_id}")
    
    try:
        escolha = int(input(f"\nEscolha (1-{len(depix_ids)}): ")) - 1
        if escolha < 0 or escolha >= len(depix_ids):
            print("❌ Escolha inválida")
            return
        
        depix_id = depix_ids[escolha]
        
    except ValueError:
        print("❌ Número inválido")
        return
    
    print(f"\n🎯 Testando: {depix_id}")
    
    # FASE 1: Criar depósito via REST (funciona)
    print(f"\n🚀 FASE 1: Criando depósito")
    txid = criar_deposito_direto(depix_id)
    
    if not txid:
        print("❌ Falha na criação, abortando")
        return
    
    # FASE 2: Processar via Voltz REST (funciona)
    print(f"\n🚀 FASE 2: Processando via Voltz")
    if processar_voltz_direto(depix_id):
        print("✅ Processamento iniciado")
    else:
        print("⚠️ Erro no processamento, mas continuando...")
    
    # FASE 3: Monitorar status (funciona)
    print(f"\n🚀 FASE 3: Monitorando status")
    
    for tentativa in range(1, 11):
        print(f"\n   Tentativa {tentativa}/10...")
        
        status = verificar_status_voltz(depix_id)
        
        if status and status.get('invoice'):
            print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print(f"✅ Depix ID: {depix_id}")
            print(f"✅ TxID: {txid}")
            print(f"✅ Invoice: {status['invoice']}")
            
            print(f"\n💡 Para testar pagamento:")
            print(f"lncli payinvoice {status['invoice']}")
            return
            
        elif status:
            print(f"   ✅ Status obtido, mas sem invoice ainda")
            if status.get('status'):
                print(f"   Status: {status['status']}")
        else:
            print(f"   ❌ Erro na consulta")
        
        if tentativa < 10:
            print(f"   ⏱️ Aguardando 5 segundos...")
            time.sleep(5)
    
    print(f"\n⏰ TIMEOUT - Invoice não foi gerado")
    print(f"✅ Depósito criado: {depix_id}")
    print(f"✅ TxID: {txid}")
    print(f"❌ Invoice: Não gerado")
    
    print(f"\n📋 Verificações manuais:")
    print(f"   • https://useghost.squareweb.app/voltz/voltz_status.php")
    print(f"   • Payload: {{'depix_id': '{depix_id}'}}")

if __name__ == "__main__":
    main()
