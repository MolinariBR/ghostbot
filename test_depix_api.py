#!/usr/bin/env python3
"""
Script para testar o polling direto na API Depix
"""
import sys
import os
import requests
import uuid
sys.path.append('/home/mau/bot/ghost')

def test_depix_api():
    """Testa a API Depix diretamente"""
    try:
        print("🔍 Testando API Depix diretamente...")
        
        # Dados do PIX atual
        depix_id = '0197f7083e627dfe8532dfb32d576171'
        
        # Configuração da API
        api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0"
        
        headers = {
            "api_key": api_key,
            "Authorization": f"Bearer {api_key}",
            "X-Nonce": str(uuid.uuid4())
        }
        
        url = f"https://depix.eulen.app/api/deposit-status?id={depix_id}"
        
        print(f"📡 URL: {url}")
        print(f"🔑 Headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📝 Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Corrigir acesso aos dados - eles estão em 'response'
            response_data = data.get('response', data)
            status = response_data.get('status')
            blockchain_txid = response_data.get('blockchainTxID')
            
            print(f"✅ Status: {status}")
            print(f"🔗 Blockchain TxID: {blockchain_txid}")
            
            if status == 'depix_sent' and blockchain_txid:
                print("🎉 Condição atendida! O PIX deveria ter disparado o gatilho.")
                return True
            else:
                print("⚠️ Condição não atendida.")
                return False
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 Testando API Depix diretamente...")
    result = test_depix_api()
    print(f"✅ Resultado: {result}")
    return result

if __name__ == "__main__":
    main()
