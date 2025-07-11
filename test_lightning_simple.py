#!/usr/bin/env python3
"""
Teste simples do Lightning Address - 10 sats
"""
import requests
import json

def test_lightning_simple():
    """Teste simples do endpoint Lightning Address"""
    print("🧪 TESTANDO LIGHTNING ADDRESS (10 sats)")
    print("=" * 50)
    
    url = "https://useghost.squareweb.app/api/process_lightning_address.php"
    
    data = {
        'chat_id': '7910260237',
        'user_input': 'test@getalby.com'
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            text = response.text
            print(f"Response Length: {len(text)}")
            
            # Extrair JSON correto
            if '}{' in text:
                parts = text.split('}{')
                json_text = '{' + parts[-1]
                print(f"JSON: {json_text}")
                
                result = json.loads(json_text)
                print(f"Success: {result.get('success')}")
                print(f"Message: {result.get('message')}")
                
                return result.get('success', False)
            else:
                result = response.json()
                print(f"Result: {result}")
                return result.get('success', False)
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_lightning_simple()
    print("=" * 50)
    print(f"RESULTADO: {'✅ SUCESSO' if success else '❌ FALHA'}")
