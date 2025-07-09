#!/usr/bin/env python3
"""
Teste do Sistema Lightning Unificado - Após limpeza do sistema antigo
"""

import requests
import json
import sqlite3
import time
from datetime import datetime

def test_unified_lightning_system():
    """Testa o sistema Lightning unificado"""
    
    print("🔄 TESTANDO SISTEMA LIGHTNING UNIFICADO")
    print("=" * 50)
    
    backend_url = "https://useghost.squareweb.app"
    chat_id = "7910260237"
    lightning_address = "bouncyflight79@walletofsatoshi.com"
    
    # 1. Criar depósito com status 'confirmado' (simulando PIX pago)
    print("\n1. 📦 Criando depósito confirmado...")
    depix_id = f"UNIFIED_TEST_{int(time.time())}"
    
    deposit_payload = {
        "chatid": chat_id,
        "moeda": "BTC",
        "rede": "⚡ Lightning", 
        "amount_in_cents": 500,  # R$ 5,00
        "taxa": 5.0,
        "address": "",  # Será preenchido pelo Lightning Address
        "forma_pagamento": "PIX",
        "send": 0.000035,  # ~3500 sats
        "user_id": int(chat_id),
        "depix_id": depix_id,
        "status": "confirmado",  # PIX já foi pago
        "comprovante": "PIX Confirmado"
    }
    
    response = requests.post(
        f"{backend_url}/rest/deposit.php",
        json=deposit_payload,
        headers={'Content-Type': 'application/json'},
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Depósito criado: ID {data.get('id')} - Status: confirmado")
    else:
        print(f"❌ Erro criando depósito: {response.status_code}")
        return False
    
    # 2. Processar Lightning Address via novo endpoint
    print("\n2. ⚡ Processando Lightning Address via sistema unificado...")
    
    lightning_payload = {
        "chat_id": chat_id,
        "user_input": lightning_address
    }
    
    response = requests.post(
        f"{backend_url}/api/process_lightning_address.php",
        json=lightning_payload,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Resposta: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("✅ Lightning Address processado com sucesso!")
                payment_hash = result.get('payment_hash')
                blockchain_tx_id = result.get('blockchain_tx_id')
                
                print(f"💎 Payment Hash: {payment_hash}")
                print(f"🔗 Blockchain TX ID: {blockchain_tx_id}")
                
                # 3. Verificar se o trigger foi executado
                print("\n3. 🎯 Verificando se trigger foi executado...")
                time.sleep(5)  # Aguardar processamento
                
                # Consultar status final do depósito
                response = requests.get(
                    f"{backend_url}/rest/deposit.php?action=get&depix_id={depix_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    final_data = response.json()
                    final_status = final_data.get('status')
                    final_blockchain_tx = final_data.get('blockchainTxID')
                    
                    print(f"📊 Status final: {final_status}")
                    print(f"🔗 blockchainTxID final: {final_blockchain_tx}")
                    
                    if final_status == 'finalizado':
                        print("🎉 SUCESSO! Sistema unificado funcionando perfeitamente!")
                        return True
                    else:
                        print(f"⚠️ Status não finalizado: {final_status}")
                else:
                    print("❌ Erro consultando status final")
                    
            else:
                print(f"❌ Erro no processamento: {result.get('message')}")
        except json.JSONDecodeError:
            print(f"❌ Resposta não é JSON válido: {response.text}")
    else:
        print(f"❌ Erro HTTP: {response.text}")
    
    return False

def check_system_status():
    """Verifica status geral do sistema"""
    print("\n🔍 VERIFICANDO STATUS DO SISTEMA")
    print("-" * 40)
    
    backend_url = "https://useghost.squareweb.app"
    
    # Verificar se endpoints antigos foram removidos
    old_endpoints = [
        "/api/lightning_cron_endpoint_final.php",
        "/api/lightning_notifier.php",
        "/api/lightning_cron_specific.php"
    ]
    
    print("Verificando remoção de endpoints antigos:")
    for endpoint in old_endpoints:
        response = requests.get(f"{backend_url}{endpoint}", timeout=5)
        status = "❌ REMOVIDO" if response.status_code == 404 else f"⚠️ AINDA EXISTE ({response.status_code})"
        print(f"  {endpoint}: {status}")
    
    # Verificar se novos endpoints estão funcionais
    new_endpoints = [
        "/api/process_lightning_address.php",
        "/api/lightning_trigger.php"
    ]
    
    print("\nVerificando endpoints novos:")
    for endpoint in new_endpoints:
        response = requests.post(f"{backend_url}{endpoint}", 
                               json={}, 
                               timeout=5)
        status = "✅ ATIVO" if response.status_code in [200, 400] else f"❌ PROBLEMA ({response.status_code})"
        print(f"  {endpoint}: {status}")

if __name__ == "__main__":
    print("🧪 TESTE DO SISTEMA LIGHTNING UNIFICADO")
    print("=" * 60)
    
    # Verificar status geral
    check_system_status()
    
    # Testar fluxo completo
    success = test_unified_lightning_system()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SISTEMA UNIFICADO: FUNCIONANDO PERFEITAMENTE!")
    else:
        print("⚠️ SISTEMA UNIFICADO: NECESSITA AJUSTES")
    print("=" * 60)
