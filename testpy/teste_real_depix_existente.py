#!/usr/bin/env python3
"""
Teste real com depósito existente - forçar processamento do Lightning
"""
import requests
import json
import time

# Usar depósito existente que encontramos no banco
depix_id = "0197e9e7d0d17dfc9b9ee24c0c36ba2a"
chat_id = "7910260237"

def test_real_flow():
    print("\n🔍 TESTE REAL COM DEPÓSITO EXISTENTE")
    print("=" * 60)
    print(f"🎯 Depix ID: {depix_id}")
    print(f"💬 Chat ID: {chat_id}")
    print("Status esperado: awaiting_client_invoice")
    print("BlockchainTxID: teste_1751979953")
    
    print(f"\n1️⃣ VERIFICANDO DEPÓSITO NO SERVIDOR")
    print("-" * 50)
    
    try:
        url_deposit = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
        resp = requests.get(url_deposit, timeout=10)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Resposta do servidor:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            deposito = data.get('deposits', [{}])[0] if data.get('deposits') else {}
            if deposito:
                print(f"\n📊 Status atual: {deposito.get('status')}")
                print(f"🔗 BlockchainTxID: {deposito.get('blockchainTxID')}")
                print(f"💬 Chat ID: {deposito.get('chat_id')}")
            else:
                print("⚠️  Depósito não encontrado no servidor")
        else:
            print(f"❌ Erro {resp.status_code}: {resp.text}")
            
    except Exception as e:
        print(f"❌ Erro ao consultar depósito: {e}")
        return False
    
    print(f"\n2️⃣ EXECUTANDO CRON LIGHTNING")
    print("-" * 50)
    
    try:
        url_cron = f"https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php?chat_id={chat_id}"
        print(f"🔗 URL: {url_cron}")
        
        resp_cron = requests.get(url_cron, timeout=15)
        print(f"Status: {resp_cron.status_code}")
        
        if resp_cron.status_code == 200:
            try:
                cron_data = resp_cron.json()
                print("✅ Resposta do cron:")
                print(json.dumps(cron_data, indent=2, ensure_ascii=False))
                
                results = cron_data.get('results', [])
                if results:
                    print(f"\n🎯 Cron processou {len(results)} depósito(s)")
                    for result in results:
                        print(f"   - {result.get('depix_id')} - Status: {result.get('status')}")
                        if result.get('depix_id') == depix_id:
                            print(f"   ✅ Nosso depósito foi processado!")
                else:
                    print("⚠️  Cron não retornou resultados")
            except json.JSONDecodeError:
                print(f"❌ Resposta não é JSON válido: {resp_cron.text}")
        else:
            print(f"❌ Erro {resp_cron.status_code}: {resp_cron.text}")
            
    except Exception as e:
        print(f"❌ Erro ao executar cron: {e}")
    
    print(f"\n3️⃣ CHAMANDO NOTIFIER DIRETAMENTE")
    print("-" * 50)
    
    try:
        url_notifier = f"https://useghost.squareweb.app/api/lightning_notifier.php?chat_id={chat_id}"
        print(f"🔗 URL: {url_notifier}")
        
        resp_notifier = requests.get(url_notifier, timeout=10)
        print(f"Status: {resp_notifier.status_code}")
        
        if resp_notifier.status_code == 200:
            try:
                notifier_data = resp_notifier.json()
                print("✅ Resposta do notifier:")
                print(json.dumps(notifier_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(f"❌ Resposta não é JSON válido: {resp_notifier.text}")
        else:
            print(f"❌ Erro {resp_notifier.status_code}: {resp_notifier.text}")
            
    except Exception as e:
        print(f"❌ Erro ao chamar notifier: {e}")
    
    print(f"\n4️⃣ VERIFICANDO STATUS FINAL")
    print("-" * 50)
    
    try:
        time.sleep(2)  # Aguardar processamento
        resp_final = requests.get(url_deposit, timeout=10)
        
        if resp_final.status_code == 200:
            data_final = resp_final.json()
            deposito_final = data_final.get('deposits', [{}])[0] if data_final.get('deposits') else {}
            
            if deposito_final:
                print(f"📊 Status final: {deposito_final.get('status')}")
                print(f"🔔 Notified: {deposito_final.get('notified', 'N/A')}")
                print(f"⚡ Lightning Address: {deposito_final.get('lightning_address', 'N/A')}")
            else:
                print("⚠️  Depósito não encontrado na verificação final")
                
    except Exception as e:
        print(f"❌ Erro na verificação final: {e}")
    
    print(f"\n5️⃣ RESULTADO ESPERADO")
    print("-" * 50)
    print("✅ Se tudo funcionou corretamente:")
    print("   1. Cron encontrou o depósito")
    print("   2. Notifier foi executado com sucesso")
    print("   3. Bot enviou mensagem solicitando endereço Lightning")
    print("   4. Mensagem apareceu no chat do Telegram")
    print("")
    print("🔍 Para verificar:")
    print(f"   - Abra o chat {chat_id} no Telegram")
    print("   - Procure mensagem do bot solicitando endereço Lightning")
    print("   - Se não apareceu, verifique logs do bot")
    
    return True

if __name__ == "__main__":
    test_real_flow()
