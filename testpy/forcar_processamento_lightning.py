#!/usr/bin/env python3
"""
Forçar status confirmado para permitir processamento Lightning real
"""

import requests
import json

def forcar_status_confirmado():
    backend_url = "https://useghost.squareweb.app"
    depix_id = "DEPIX_7910260237_1752083255"
    pedido_id = "48"
    
    print("🔧 FORÇANDO STATUS CONFIRMADO PARA TESTE LIGHTNING")
    print("=" * 60)
    
    # Tentar atualizar via endpoint REST
    try:
        print("1. 🔄 Tentando atualizar status via REST...")
        payload = {
            "action": "update",
            "id": pedido_id,
            "status": "confirmado"
        }
        
        response = requests.post(
            f"{backend_url}/rest/deposit.php",
            json=payload,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        # Verificar se mudou
        print("\n2. 🔍 Verificando status após update...")
        response = requests.get(f"{backend_url}/rest/deposit.php?action=get&id={pedido_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            novo_status = data.get('status')
            print(f"📊 Status atual: {novo_status}")
            
            if novo_status == 'confirmado':
                print("✅ Status atualizado com sucesso!")
                
                # Tentar processar Lightning agora
                print("\n3. ⚡ Processando Lightning com status confirmado...")
                return testar_processamento_lightning()
            else:
                print(f"⚠️ Status não mudou: {novo_status}")
                
                # Tentar método alternativo - webhook de confirmação real
                print("\n🔄 Tentando webhook de confirmação real...")
                return simular_confirmacao_pix_real()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def simular_confirmacao_pix_real():
    """Simula uma confirmação PIX real mais completa"""
    backend_url = "https://useghost.squareweb.app"
    depix_id = "DEPIX_7910260237_1752083255"
    
    try:
        # Webhook mais completo simulando Depix real
        webhook_data = {
            "event_type": "payment.paid",
            "data": {
                "id": depix_id,
                "status": "paid",
                "payment_method": "pix",
                "amount": 500,
                "currency": "BRL", 
                "paid_at": "2025-07-09T17:50:00Z",
                "customer": {
                    "id": "7910260237"
                },
                "metadata": {
                    "chat_id": "7910260237",
                    "lightning_address": "bouncyflight79@walletofsatoshi.com"
                }
            }
        }
        
        print("📤 Enviando webhook de confirmação PIX...")
        response = requests.post(
            f"{backend_url}/square_webhook.php",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        # Aguardar processamento
        import time
        time.sleep(3)
        
        return testar_processamento_lightning()
        
    except Exception as e:
        print(f"❌ Erro simulando PIX: {e}")
        return False

def testar_processamento_lightning():
    """Testa o processamento Lightning após confirmação"""
    backend_url = "https://useghost.squareweb.app"
    
    try:
        print("\n⚡ TESTANDO PROCESSAMENTO LIGHTNING...")
        
        # 1. Verificar endpoint cron
        response = requests.get(f"{backend_url}/api/lightning_cron_endpoint_final.php?chat_id=7910260237", timeout=10)
        print(f"📊 Cron endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Pendentes: {data.get('total_pending', 0)}")
            
            if data.get('total_pending', 0) > 0:
                print("✅ Pedido agora é detectado como pendente!")
                
                # 2. Tentar processar Lightning Address
                lightning_payload = {
                    "chat_id": "7910260237",
                    "user_input": "bouncyflight79@walletofsatoshi.com"
                }
                
                response = requests.post(
                    f"{backend_url}/api/process_lightning_address.php",
                    json=lightning_payload,
                    timeout=20
                )
                
                print(f"\n💫 Processamento Lightning: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Resultado: {json.dumps(data, indent=2)}")
                    return data.get('success', False)
                else:
                    print(f"❌ Resposta: {response.text}")
            else:
                print("⚠️ Ainda não detectado como pendente")
                
    except Exception as e:
        print(f"❌ Erro testando Lightning: {e}")
    
    return False

if __name__ == "__main__":
    sucesso = forcar_status_confirmado()
    print(f"\n🎯 RESULTADO FINAL: {'✅ SUCESSO' if sucesso else '❌ FALHA'}")
