#!/usr/bin/env python3
"""
Simulador de confirmação PIX - dispara fluxo Lightning para depósito real
Simula webhook de confirmação do PIX para continuar o fluxo Lightning
"""
import requests
import json
import time

# Dados do depósito real criado
depix_id = "0197eae225117dfc85fe31ea03c518a4"
chat_id = "7910260237"

def simulate_pix_confirmation():
    """Simula confirmação do PIX via webhook para disparar fluxo Lightning"""
    
    print("\n🚀 SIMULADOR DE CONFIRMAÇÃO PIX")
    print("=" * 60)
    print(f"🎯 Depix ID: {depix_id}")
    print(f"💬 Chat ID: {chat_id}")
    print(f"💰 Valor: R$ 5,00")
    
    # 1. Primeiro verificar o status atual
    print(f"\n1️⃣ VERIFICANDO STATUS ATUAL")
    print("-" * 40)
    
    try:
        url_check = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
        resp = requests.get(url_check, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('deposits'):
                deposit = data['deposits'][0]
                print(f"📊 Status atual: {deposit.get('status')}")
                print(f"🔗 BlockchainTxID: {deposit.get('blockchainTxID')}")
                print(f"💬 Chat ID: {deposit.get('chatid')}")
            else:
                print("❌ Depósito não encontrado")
                return False
        else:
            print(f"❌ Erro ao consultar: {resp.status_code}")
            
    except Exception as e:
        print(f"⚠️  Erro na consulta (servidor pode estar instável): {e}")
        print("Continuando com simulação...")
    
    # 2. Simular webhook de confirmação PIX
    print(f"\n2️⃣ SIMULANDO WEBHOOK DE CONFIRMAÇÃO PIX")
    print("-" * 40)
    
    # Dados para simular confirmação PIX
    webhook_data = {
        "event": "payment_confirmed",
        "transaction_id": depix_id,
        "status": "confirmed",
        "amount": 500,  # R$ 5,00 em centavos
        "currency": "BRL",
        "payment_method": "PIX",
        "confirmed_at": int(time.time()),
        "blockchain_txid": f"pix_confirmed_{int(time.time())}"
    }
    
    print(f"📤 Dados do webhook:")
    print(json.dumps(webhook_data, indent=2))
    
    try:
        # Simular webhook
        webhook_url = "https://useghost.squareweb.app/depix/webhook.php"
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PixWebhook/1.0'
        }
        
        print(f"\n📤 Enviando webhook para: {webhook_url}")
        resp_webhook = requests.post(webhook_url, 
                                   json=webhook_data, 
                                   headers=headers, 
                                   timeout=15)
        
        print(f"📊 Status webhook: {resp_webhook.status_code}")
        
        if resp_webhook.status_code == 200:
            print("✅ Webhook enviado com sucesso")
            
            try:
                response_data = resp_webhook.json()
                print(f"📋 Resposta: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📋 Resposta: {resp_webhook.text}")
        else:
            print(f"❌ Erro no webhook: {resp_webhook.text}")
            
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")
        print("💡 Tentando método alternativo...")
        
        # Método alternativo: atualizar diretamente via API
        try:
            update_url = f"https://useghost.squareweb.app/api/confirm_deposit.php"
            update_data = {
                "depix_id": depix_id,
                "blockchain_txid": f"pix_confirmed_{int(time.time())}",
                "status": "confirmed"
            }
            
            resp_update = requests.post(update_url, json=update_data, timeout=10)
            print(f"📊 Status update: {resp_update.status_code}")
            
        except Exception as e2:
            print(f"❌ Erro no método alternativo: {e2}")
    
    # 3. Aguardar processamento
    print(f"\n3️⃣ AGUARDANDO PROCESSAMENTO")
    print("-" * 40)
    print("⏳ Aguardando 5 segundos para processamento...")
    time.sleep(5)
    
    # 4. Disparar cron Lightning
    print(f"\n4️⃣ DISPARANDO CRON LIGHTNING")
    print("-" * 40)
    
    try:
        cron_url = f"https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php?chat_id={chat_id}"
        print(f"🔗 URL do cron: {cron_url}")
        
        resp_cron = requests.get(cron_url, timeout=15)
        print(f"📊 Status cron: {resp_cron.status_code}")
        
        if resp_cron.status_code == 200:
            try:
                cron_data = resp_cron.json()
                print("✅ Resposta do cron:")
                print(json.dumps(cron_data, indent=2))
                
                results = cron_data.get('results', [])
                if results:
                    print(f"🎯 Cron encontrou {len(results)} depósito(s) para processar")
                    for result in results:
                        if result.get('depix_id') == depix_id:
                            print(f"✅ Nosso depósito {depix_id} foi encontrado!")
                else:
                    print("⚠️  Cron não encontrou depósitos para processar")
                    
            except:
                print(f"📋 Resposta do cron: {resp_cron.text}")
        else:
            print(f"❌ Erro no cron: {resp_cron.text}")
            
    except Exception as e:
        print(f"❌ Erro no cron: {e}")
    
    # 5. Disparar notifier
    print(f"\n5️⃣ DISPARANDO NOTIFIER LIGHTNING")
    print("-" * 40)
    
    try:
        notifier_url = f"https://useghost.squareweb.app/api/lightning_notifier.php?chat_id={chat_id}"
        print(f"🔗 URL do notifier: {notifier_url}")
        
        resp_notifier = requests.get(notifier_url, timeout=10)
        print(f"📊 Status notifier: {resp_notifier.status_code}")
        
        if resp_notifier.status_code == 200:
            try:
                notifier_data = resp_notifier.json()
                print("✅ Resposta do notifier:")
                print(json.dumps(notifier_data, indent=2))
            except:
                print(f"📋 Resposta do notifier: {resp_notifier.text}")
        else:
            print(f"❌ Erro no notifier: {resp_notifier.text}")
            
    except Exception as e:
        print(f"❌ Erro no notifier: {e}")
    
    # 6. Verificar status final
    print(f"\n6️⃣ VERIFICANDO STATUS FINAL")
    print("-" * 40)
    
    try:
        time.sleep(3)
        resp_final = requests.get(url_check, timeout=10)
        
        if resp_final.status_code == 200:
            data_final = resp_final.json()
            if data_final.get('deposits'):
                deposit_final = data_final['deposits'][0]
                print(f"📊 Status final: {deposit_final.get('status')}")
                print(f"🔗 BlockchainTxID: {deposit_final.get('blockchainTxID')}")
                print(f"🔔 Notified: {deposit_final.get('notified', 'N/A')}")
            else:
                print("❌ Depósito não encontrado na verificação final")
                
    except Exception as e:
        print(f"❌ Erro na verificação final: {e}")
    
    print(f"\n🎯 RESULTADO ESPERADO")
    print("-" * 40)
    print("Se tudo funcionou:")
    print("✅ 1. PIX foi confirmado via webhook")
    print("✅ 2. Cron processou o depósito")
    print("✅ 3. Notifier disparou mensagem no bot")
    print("✅ 4. Bot solicitou endereço Lightning no Telegram")
    print("")
    print(f"📱 Verifique o Telegram no chat {chat_id}")
    print("Você deve receber uma mensagem solicitando endereço Lightning!")
    
    return True

if __name__ == "__main__":
    simulate_pix_confirmation()
