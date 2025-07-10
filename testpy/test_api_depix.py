#!/usr/bin/env python3
"""
Script para testar diretamente a API Depix e identificar o erro do campo forma_pagamento
"""

import json
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.depix import PixAPI, PixAPIError

def teste_api_depix():
    """Testa a API Depix com um pagamento simples"""
    
    print("🧪 TESTE DIRETO DA API DEPIX")
    print("=" * 40)
    
    try:
        # Inicializa a API Depix
        pix_api = PixAPI()
        print(f"✅ API inicializada: {pix_api.api_url}")
        
        # Dados de teste
        dados_teste = {
            'valor_centavos': 5000,  # R$ 50,00
            'endereco': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
            'chatid': '123456789',
            'moeda': 'BTC',
            'rede': 'Lightning',
            'taxa': 5.0,
            'forma_pagamento': 'PIX',
            'send': 0.00014285,
            'user_id': 123456789,
            'comprovante': 'Lightning Invoice',
            'cpf': None
        }
        
        print("📦 Dados do teste:")
        for chave, valor in dados_teste.items():
            print(f"   • {chave}: {valor}")
        print()
        
        # Tenta criar o pagamento
        print("🚀 Criando pagamento...")
        resultado = pix_api.criar_pagamento(**dados_teste)
        
        print("✅ Pagamento criado com sucesso!")
        print(f"📝 Resultado: {json.dumps(resultado, indent=2)}")
        
    except PixAPIError as e:
        print(f"❌ Erro da API Depix: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

def teste_api_backend_direto():
    """Testa diretamente o endpoint do backend"""
    
    print("\n🧪 TESTE DIRETO DO BACKEND")
    print("=" * 40)
    
    # Dados de teste direto para o backend
    payload = {
        "chatid": "123456789",
        "moeda": "BTC",
        "rede": "Lightning",
        "amount_in_cents": 5000,
        "taxa": 5.0,
        "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
        "metodo_pagamento": "PIX",
        "forma_pagamento": "PIX",
        "send": 0.00014285,
        "depix_id": "TESTE_DIRETO_123",
        "status": "pending",
        "user_id": 123456789,
        "comprovante": "Lightning Invoice"
    }
    
    print("📦 Payload para o backend:")
    print(json.dumps(payload, indent=2))
    print()
    
    try:
        headers = {'Content-Type': 'application/json'}
        
        print("🚀 Enviando para o backend...")
        response = requests.post(
            "https://useghost.squareweb.app/rest/deposit.php",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status da resposta: {response.status_code}")
        print(f"📝 Resposta: {response.text}")
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                print(f"📋 JSON da resposta: {json.dumps(resp_json, indent=2)}")
            except Exception as e:
                print(f"⚠️ Erro ao decodificar JSON: {e}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    teste_api_depix()
    teste_api_backend_direto()
