#!/usr/bin/env python3
"""
TESTE COMPLETO LIGHTNING - Criar Depósito + Simular Webhook
===========================================================

Este script cria um depósito Lightning real no banco e depois
simula o webhook do Depix para testar o fluxo completo.
"""

import requests
import json
import time
import sys
import os

# Adiciona o path do ghost
sys.path.append('/home/mau/bot/ghost')

def criar_deposito_lightning_teste(chat_id="123456789", valor_brl=100.0):
    """
    Cria um depósito Lightning de teste no backend.
    """
    from api.voltz import VoltzAPI
    
    print(f"🆕 Criando depósito Lightning de teste...")
    print(f"👤 Chat ID: {chat_id}")
    print(f"💰 Valor: R$ {valor_brl}")
    
    try:
        voltz = VoltzAPI(backend_url='https://useghost.squareweb.app')
        
        # Cria o depósito via Voltz
        result = voltz.create_deposit_request(
            chatid=str(chat_id),
            userid=str(chat_id),
            amount_in_cents=int(valor_brl * 100),
            taxa=0.05,  # 5%
            moeda="BTC",
            send_amount=int((valor_brl * 0.95) / 350000 * 100000000)  # sats (assumindo BTC a R$ 350k)
        )
        
        if result.get('depix_id'):
            depix_id = result['depix_id']
            print(f"✅ Depósito criado com sucesso!")
            print(f"🆔 Depix ID: {depix_id}")
            print(f"📝 Status: {result.get('status', 'N/A')}")
            print(f"💬 Mensagem: {result.get('message', 'N/A')}")
            return depix_id
        else:
            print(f"❌ Erro ao criar depósito: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao criar depósito: {e}")
        return None

def simular_webhook_depix(depix_id, blockchain_txid=None):
    """
    Simula o webhook do Depix enviando blockchainTxID.
    """
    if not blockchain_txid:
        # Gera um TxID realista de Bitcoin
        blockchain_txid = f"{'a1b2c3d4e5f6' * 5}{'7890abcd' * 2}"[:64]
    
    webhook_url = "https://useghost.squareweb.app/depix/webhook.php"
    
    payload = {
        "id": depix_id,
        "blockchainTxID": blockchain_txid,
        "status": "confirmado",
        "timestamp": int(time.time())
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0",
        "User-Agent": "Depix-Webhook/1.0"
    }
    
    print(f"\n🔗 Simulando webhook Depix...")
    print(f"🆔 Depix ID: {depix_id}")
    print(f"📋 TxID: {blockchain_txid}")
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Webhook enviado com sucesso!")
            return True
        else:
            print(f"❌ Erro no webhook (HTTP {response.status_code})")
            print(f"📝 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")
        return False

def monitorar_invoice_lightning(depix_id, max_tentativas=15):
    """
    Monitora a geração do invoice Lightning.
    """
    from api.voltz import VoltzAPI
    
    print(f"\n⚡ Monitorando geração do invoice Lightning...")
    
    voltz = VoltzAPI(backend_url='https://useghost.squareweb.app')
    
    for tentativa in range(1, max_tentativas + 1):
        print(f"   Tentativa {tentativa}/{max_tentativas}...")
        
        try:
            status = voltz.check_deposit_status(depix_id)
            
            if status.get('success'):
                print(f"   ✅ Status: {status.get('status')}")
                
                if status.get('invoice'):
                    print(f"\n🎉 INVOICE LIGHTNING GERADO!")
                    print(f"🆔 Depix ID: {depix_id}")
                    print(f"📱 Invoice: {status['invoice']}")
                    
                    if status.get('qr_code'):
                        print(f"📱 QR Code: {status['qr_code']}")
                    
                    return status
                else:
                    print(f"   ⏳ Aguardando geração do invoice...")
            else:
                error_msg = status.get('error', 'Erro desconhecido')
                print(f"   ❌ Erro: {error_msg}")
                
                # Se não encontrou, pode ser que ainda não foi processado
                if "not found" in error_msg.lower():
                    print(f"   ℹ️ Depósito ainda não foi processado pelo Voltz...")
        
        except Exception as e:
            print(f"   ❌ Erro na consulta: {e}")
        
        if tentativa < max_tentativas:
            print(f"   ⏱️ Aguardando 3 segundos...")
            time.sleep(3)
    
    print(f"\n⏰ Timeout - Invoice não foi gerado após {max_tentativas} tentativas")
    return None

def main():
    print("🧪 TESTE COMPLETO LIGHTNING - Criar + Webhook + Invoice")
    print("=" * 60)
    
    # Configurações do teste
    chat_id = input("Chat ID para teste (padrão: 123456789): ").strip() or "123456789"
    valor_brl = float(input("Valor em BRL (padrão: 100.0): ").strip() or "100.0")
    
    print(f"\n🚀 FASE 1: Criando depósito Lightning")
    depix_id = criar_deposito_lightning_teste(chat_id, valor_brl)
    
    if not depix_id:
        print("❌ Falha ao criar depósito, abortando teste")
        return
    
    # Aguardar um pouco para o depósito ser salvo
    print(f"\n⏱️ Aguardando 3 segundos...")
    time.sleep(3)
    
    print(f"\n🚀 FASE 2: Simulando webhook do Depix")
    webhook_success = simular_webhook_depix(depix_id)
    
    if not webhook_success:
        print("❌ Falha no webhook, mas continuando...")
    
    # Aguardar processamento
    print(f"\n⏱️ Aguardando 5 segundos para processamento...")
    time.sleep(5)
    
    print(f"\n🚀 FASE 3: Monitorando geração do invoice")
    resultado = monitorar_invoice_lightning(depix_id)
    
    if resultado and resultado.get('invoice'):
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print(f"✅ Depósito criado: {depix_id}")
        print(f"✅ Webhook processado")
        print(f"✅ Invoice Lightning gerado")
        
        print(f"\n💡 Para testar o pagamento:")
        print(f"lncli payinvoice {resultado['invoice']}")
        
        print(f"\n📋 RESUMO DO TESTE:")
        print(f"🆔 Depix ID: {depix_id}")
        print(f"💰 Valor: R$ {valor_brl}")
        print(f"👤 Chat ID: {chat_id}")
        print(f"⚡ Invoice: {resultado['invoice'][:50]}...")
        
    else:
        print(f"\n❌ TESTE FALHOU")
        print(f"✅ Depósito criado: {depix_id}")
        print(f"{'✅' if webhook_success else '❌'} Webhook: {'Enviado' if webhook_success else 'Falhou'}")
        print(f"❌ Invoice: Não gerado")
        
        print(f"\n🔍 Verificações sugeridas:")
        print(f"   • Verificar logs do Voltz")
        print(f"   • Verificar se o depósito foi salvo no banco")
        print(f"   • Verificar se o Lightning Node está online")
        print(f"   • Testar manualmente a API Voltz")

if __name__ == "__main__":
    main()
