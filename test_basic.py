print("🧪 Teste Básico Voltz")

try:
    import requests
    print("✅ Requests importado")
    
    # Teste direto do endpoint
    url = "http://localhost:8000/api/bot_register_deposit.php"
    data = {
        'chatid': 'test123',
        'userid': 'user456', 
        'amount_in_cents': 2500,
        'taxa': 0.05,
        'moeda': 'BTC',
        'rede': 'lightning',
        'address': 'voltz@mail.com',
        'forma_pagamento': 'PIX',
        'send': 45000,
        'status': 'pending',
        'depix_id': 'test_depix_123'
    }
    
    print(f"📡 Fazendo POST para: {url}")
    response = requests.post(url, json=data, timeout=10)
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Response: {response.text}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
