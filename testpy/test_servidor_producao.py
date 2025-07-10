#!/usr/bin/env python3
"""
Script para testar diretamente no servidor de produção
"""

import json
import requests
import time

def testar_servidor_producao():
    """Testa se o servidor de produção está salvando e exibindo os registros"""
    
    print("🌐 TESTE NO SERVIDOR DE PRODUÇÃO")
    print("=" * 50)
    
    chat_id = f"TESTE_PROD_{int(time.time())}"
    
    payload = {
        "chatid": chat_id,
        "moeda": "BTC",
        "rede": "lightning",  # Formato simples que deveria aparecer
        "amount_in_cents": 10000,  # R$ 100,00
        "taxa": 5.0,
        "address": "voltzapi@tria.com",
        "forma_pagamento": "PIX",
        "send": 0.000285,
        "user_id": int(time.time()),
        "depix_id": f"DEPIX_{chat_id}",
        "status": "pending",
        "comprovante": "Lightning Invoice"
    }
    
    print(f"📤 Enviando para o servidor de produção...")
    print(f"📦 Chat ID: {chat_id}")
    print(f"📦 Rede: {payload['rede']}")
    print()
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "https://useghost.squareweb.app/rest/deposit.php",
            json=payload,
            headers=headers,
            timeout=15
        )
        
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                if resp_json.get('success'):
                    deposit_id = resp_json.get('id')
                    print(f"✅ Pedido criado com sucesso! ID: {deposit_id}")
                    
                    # Aguarda e consulta de volta
                    print("\n⏳ Aguardando 3 segundos...")
                    time.sleep(3)
                    
                    print("🔍 Consultando pedido via API...")
                    consulta_resp = requests.get(
                        f"https://useghost.squareweb.app/rest/deposit.php?chatid={chat_id}",
                        timeout=10
                    )
                    
                    if consulta_resp.status_code == 200:
                        consulta_data = consulta_resp.json()
                        deposits = consulta_data.get('deposits', [])
                        
                        if deposits:
                            print(f"✅ Pedido encontrado via API!")
                            deposit = deposits[0]
                            print(f"   • ID: {deposit.get('id')}")
                            print(f"   • Chat ID: {deposit.get('chatid')}")
                            print(f"   • Rede: '{deposit.get('rede')}'")
                            print(f"   • Status: {deposit.get('status')}")
                            print()
                            
                            print("🎯 AGORA VERIFIQUE NA INTERFACE:")
                            print("   1. Acesse: https://useghost.squareweb.app/login.php")
                            print("   2. Login: admin@mail.com / 123456")
                            print("   3. Vá para: https://useghost.squareweb.app/transacoes.php")
                            print(f"   4. Procure pelo Chat ID: {chat_id}")
                            print(f"   5. Ou pelo ID do depósito: {deposit.get('id')}")
                            
                        else:
                            print("❌ Pedido não encontrado na consulta!")
                    else:
                        print(f"❌ Erro na consulta: {consulta_resp.status_code}")
                        
                else:
                    print(f"❌ Erro na resposta: {resp_json}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"📄 Resposta bruta: {response.text}")
                
        else:
            print(f"❌ Erro HTTP: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção: {e}")

if __name__ == "__main__":
    testar_servidor_producao()
