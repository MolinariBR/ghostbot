#!/usr/bin/env python3
"""
SIMULADOR DE WEBHOOK DEPIX - Teste Lightning Voltz
==================================================

Este script simula o webhook do Depix enviando blockchainTxID para 
disparar automaticamente o processamento Lightning via Voltz.
"""

import requests
import json
import time
import sys
import os

def simular_webhook_depix(depix_id, blockchain_txid=None):
    """
    Simula o webhook do Depix enviando blockchainTxID para o backend.
    Isso vai disparar automaticamente o processamento Lightning.
    """
    if not blockchain_txid:
        # Gera um TxID simulado realista
        blockchain_txid = f"0x{''.join([f'{i:02x}' for i in range(32)])}"
    
    # URL do webhook
    webhook_url = "https://useghost.squareweb.app/depix/webhook.php"
    
    # Payload que simula o webhook do Depix
    payload = {
        "id": depix_id,
        "blockchainTxID": blockchain_txid,
        "status": "confirmado",
        "timestamp": int(time.time())
    }
    
    # Headers necessários (precisa do token de autorização)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0",
        "User-Agent": "Depix-Webhook/1.0"
    }
    
    print(f"🔗 Simulando webhook Depix para {depix_id}...")
    print(f"📋 TxID: {blockchain_txid}")
    print(f"🎯 URL: {webhook_url}")
    
    try:
        response = requests.post(
            webhook_url, 
            json=payload, 
            headers=headers, 
            timeout=15
        )
        
        if response.status_code == 200:
            print(f"✅ Webhook enviado com sucesso!")
            print(f"📝 Resposta: {response.text}")
            return True
        else:
            print(f"❌ Erro no webhook (HTTP {response.status_code})")
            print(f"📝 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")
        return False

def verificar_processamento_lightning(depix_id, max_tentativas=10):
    """
    Monitora o processamento Lightning após o webhook.
    """
    print(f"\n🔍 Monitorando processamento Lightning para {depix_id}...")
    
    # Importa a API Voltz
    sys.path.append('/home/mau/bot/ghost')
    from api.voltz import VoltzAPI
    
    voltz = VoltzAPI(backend_url='https://useghost.squareweb.app')
    
    for tentativa in range(1, max_tentativas + 1):
        print(f"   Tentativa {tentativa}/{max_tentativas}...")
        
        try:
            status = voltz.check_deposit_status(depix_id)
            
            if status.get('success'):
                print(f"   ✅ Status: {status.get('status')}")
                
                if status.get('invoice'):
                    print(f"\n⚡ INVOICE LIGHTNING GERADO!")
                    print(f"🆔 Depix ID: {depix_id}")
                    print(f"📱 Invoice: {status['invoice']}")
                    
                    if status.get('qr_code'):
                        print(f"📱 QR Code: {status['qr_code']}")
                    
                    return status
                else:
                    print(f"   ⏳ Aguardando geração do invoice...")
            else:
                print(f"   ❌ Erro: {status.get('error', 'Erro desconhecido')}")
        
        except Exception as e:
            print(f"   ❌ Erro na consulta: {e}")
        
        if tentativa < max_tentativas:
            print(f"   ⏱️ Aguardando 3 segundos...")
            time.sleep(3)
    
    print(f"\n⏰ Timeout - Invoice não foi gerado após {max_tentativas} tentativas")
    return None

def main():
    print("🧪 SIMULADOR DE WEBHOOK DEPIX")
    print("=" * 50)
    
    # IDs fornecidos pelo usuário
    depix_ids_teste = [
        "0197e0ed06537df9820a28f5a5380a3b",
        "0197e10b5b8f7df9a6bf9430188534e4", 
        "0197e12300eb7df9808ca5d7719ea40e",
        "0197e5214a377dfaae6e541f68057444"
    ]
    
    print("🎯 Depix IDs disponíveis para teste:")
    print("-" * 40)
    for i, depix_id in enumerate(depix_ids_teste, 1):
        print(f"{i}. {depix_id}")
    
    print(f"{len(depix_ids_teste) + 1}. Usar outro depix_id")
    
    try:
        escolha = int(input(f"\nEscolha uma opção (1-{len(depix_ids_teste) + 1}): "))
        
        if escolha <= len(depix_ids_teste):
            depix_id = depix_ids_teste[escolha - 1]
        elif escolha == len(depix_ids_teste) + 1:
            depix_id = input("Digite o depix_id: ").strip()
            if not depix_id:
                print("❌ Depix ID inválido")
                return
        else:
            print("❌ Opção inválida")
            return
            
    except ValueError:
        print("❌ Número inválido")
        return
    
    print(f"\n🎯 Testando depix_id: {depix_id}")
    
    # Opção para usar TxID customizado
    txid_personalizado = input("TxID personalizado (Enter para gerar automaticamente): ").strip()
    
    # 1. Simular webhook do Depix
    print(f"\n🚀 FASE 1: Simulando webhook do Depix")
    webhook_success = simular_webhook_depix(depix_id, txid_personalizado or None)
    
    if not webhook_success:
        print("❌ Falha no webhook, abortando teste")
        return
    
    # 2. Aguardar processamento
    print(f"\n⏱️ Aguardando 5 segundos para processamento...")
    time.sleep(5)
    
    # 3. Monitorar geração do invoice
    print(f"\n🚀 FASE 2: Monitorando geração do invoice Lightning")
    resultado = verificar_processamento_lightning(depix_id)
    
    if resultado and resultado.get('invoice'):
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print(f"✅ O webhook disparou o processamento Lightning")
        print(f"⚡ Invoice foi gerado automaticamente")
        
        # Comando para testar pagamento
        print(f"\n💡 Para testar o pagamento:")
        print(f"lncli payinvoice {resultado['invoice']}")
        
    else:
        print(f"\n❌ TESTE FALHOU")
        print(f"❌ Invoice não foi gerado")
        print(f"📋 Possíveis causas:")
        print(f"   • Token de autorização inválido")
        print(f"   • Depix ID não existe no banco")
        print(f"   • Erro no processamento Voltz")
        print(f"   • Rede Lightning indisponível")

def testar_webhook_direto():
    """Função para testar webhook diretamente sem menu."""
    depix_id = "0197e0ed06537df9820a28f5a5380a3b"  # Primeiro ID da lista
    
    print(f"🧪 TESTE RÁPIDO - Webhook para {depix_id}")
    print("=" * 50)
    
    # Simular webhook
    webhook_success = simular_webhook_depix(depix_id)
    
    if webhook_success:
        print(f"\n⏱️ Aguardando processamento...")
        time.sleep(5)
        
        # Verificar resultado
        resultado = verificar_processamento_lightning(depix_id, max_tentativas=5)
        
        if resultado and resultado.get('invoice'):
            print(f"\n🎉 SUCESSO! Invoice gerado: {resultado['invoice'][:50]}...")
        else:
            print(f"\n❌ Invoice não foi gerado")
    else:
        print(f"\n❌ Falha no webhook")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        testar_webhook_direto()
    else:
        main()
