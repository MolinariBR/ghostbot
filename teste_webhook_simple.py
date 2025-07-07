#!/usr/bin/env python3

import requests
import json
import sys
import os

# Adiciona path do ghost
sys.path.append('/home/mau/bot/ghost')

def main():
    print("🧪 TESTE SIMPLES - Webhook + Status")
    print("=" * 40)
    
    # Depix ID criado anteriormente
    depix_id = "voltz_1751906690_6349"
    blockchain_txid = "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
    
    print(f"🆔 Depix ID: {depix_id}")
    print(f"📋 TxID: {blockchain_txid}")
    
    # 1. Enviar webhook
    print(f"\n🔗 Enviando webhook...")
    webhook_url = "https://useghost.squareweb.app/depix/webhook.php"
    payload = {
        "id": depix_id,
        "blockchainTxID": blockchain_txid,
        "status": "confirmado"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0"
    }
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        webhook_ok = response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        webhook_ok = False
    
    # 2. Aguardar processamento
    if webhook_ok:
        print(f"\n⏱️ Aguardando 5 segundos...")
        import time
        time.sleep(5)
        
        # 3. Verificar status via Voltz
        print(f"\n⚡ Verificando status via Voltz...")
        try:
            from api.voltz import VoltzAPI
            voltz = VoltzAPI(backend_url='https://useghost.squareweb.app')
            
            status = voltz.check_deposit_status(depix_id)
            print(f"Status Voltz: {status}")
            
            if status.get('invoice'):
                print(f"\n🎉 SUCESSO! Invoice gerado:")
                print(f"Invoice: {status['invoice']}")
            else:
                print(f"\n⏳ Invoice ainda não gerado")
                
        except Exception as e:
            print(f"Erro ao verificar status: {e}")
    
    print(f"\n✅ Teste concluído!")

if __name__ == "__main__":
    main()
