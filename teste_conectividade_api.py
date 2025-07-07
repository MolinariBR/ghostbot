#!/usr/bin/env python3
"""
Teste básico de conectividade com a API
"""

import requests

def teste_buscar_depix():
    """Teste básico para buscar um depix_id"""
    depix_id = "0197e0ed06537df9820a28f5a5380a3b"
    
    try:
        print(f"🔍 Testando conectividade com API...")
        url = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida: {len(data.get('deposits', []))} depósitos")
            if data.get('deposits'):
                dep = data['deposits'][0]
                print(f"💰 Valor: R$ {dep['amount_in_cents']/100:.2f}")
                print(f"🔗 TxID: {dep.get('blockchainTxID', 'N/A')}")
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    teste_buscar_depix()
