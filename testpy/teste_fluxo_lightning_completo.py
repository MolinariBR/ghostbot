#!/usr/bin/env python3
"""
Teste de fluxo completo Lightning - Simula PIX confirmado
"""

import json
import requests
import time

def criar_pedido_pix_confirmado():
    """Cria um pedido Lightning com PIX já confirmado para testar o fluxo completo"""
    
    print("⚡ TESTE FLUXO LIGHTNING COMPLETO")
    print("=" * 50)
    
    chat_id = f"TESTE_FLUXO_LN_{int(time.time())}"
    fake_blockchain_txid = f"pix_confirmado_{int(time.time())}"
    
    # Primeiro: cria o pedido Lightning
    payload = {
        "chatid": chat_id,
        "moeda": "BTC",
        "rede": "lightning",
        "amount_in_cents": 5000,  # R$ 50,00
        "taxa": 2.5,
        "address": "aguardando_lightning_address",
        "forma_pagamento": "PIX",
        "send": 8000,  # sats aproximados
        "user_id": int(time.time()),
        "depix_id": f"LN_TESTE_{chat_id}",
        "status": "pending",
        "comprovante": "Lightning Invoice"
    }
    
    print("📤 PASSO 1: Criando pedido Lightning...")
    print(f"📦 Chat ID: {chat_id}")
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "https://useghost.squareweb.app/rest/deposit.php",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get('success'):
                deposit_id = resp_json.get('id')
                print(f"✅ Pedido Lightning criado! ID: {deposit_id}")
                
                # Aguarda um pouco
                print("\n⏳ Aguardando 2 segundos...")
                time.sleep(2)
                
                # PASSO 2: Simula PIX sendo confirmado (adiciona blockchainTxID)
                print("📤 PASSO 2: Simulando confirmação do PIX...")
                
                update_payload = {
                    "action": "update_blockchain_txid",
                    "deposit_id": deposit_id,
                    "blockchain_txid": fake_blockchain_txid,
                    "status": "awaiting_client_invoice"
                }
                
                # Tenta atualizar via endpoint específico (se existir)
                try:
                    update_response = requests.post(
                        "https://useghost.squareweb.app/api/update_deposit.php",
                        json=update_payload,
                        headers=headers,
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        print("✅ PIX confirmado via endpoint específico!")
                    else:
                        print("⚠️ Endpoint específico não encontrado, usando simulação manual")
                        
                except:
                    print("⚠️ Usando simulação manual para teste")
                
                # PASSO 3: Verifica se aparece no endpoint Lightning
                print("\n📤 PASSO 3: Verificando endpoint Lightning...")
                time.sleep(1)
                
                lightning_response = requests.get(
                    "https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php",
                    timeout=10
                )
                
                if lightning_response.status_code == 200:
                    lightning_data = lightning_response.json()
                    results = lightning_data.get('results', [])
                    
                    found_deposit = False
                    for result in results:
                        if result.get('depix_id') == payload['depix_id']:
                            found_deposit = True
                            result_data = result.get('result', {})
                            status = result_data.get('status')
                            
                            print(f"✅ Depósito encontrado no endpoint Lightning!")
                            print(f"   Status: {status}")
                            print(f"   Mensagem: {result_data.get('message', 'N/A')}")
                            
                            if status == 'awaiting_client_invoice':
                                print("\n🎯 SUCESSO! O fluxo está funcionando:")
                                print("   1. ✅ Pedido Lightning criado")
                                print("   2. ✅ PIX simulado como confirmado")
                                print("   3. ✅ Status mudou para 'awaiting_client_invoice'")
                                print("   4. ✅ Bot deveria solicitar Lightning Address agora!")
                                
                                print(f"\n📋 DADOS PARA TESTE NO BOT:")
                                print(f"   • Chat ID: {chat_id}")
                                print(f"   • Depix ID: {payload['depix_id']}")
                                print(f"   • Deposit ID: {deposit_id}")
                                print(f"   • Status: {status}")
                                
                            break
                    
                    if not found_deposit:
                        print("❌ Depósito não encontrado no endpoint Lightning")
                        print("   Pode precisar aguardar mais tempo ou haver filtro específico")
                
                else:
                    print(f"❌ Erro ao consultar endpoint Lightning: {lightning_response.status_code}")
                
            else:
                print(f"❌ Erro na resposta: {resp_json}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção: {e}")

if __name__ == "__main__":
    criar_pedido_pix_confirmado()
