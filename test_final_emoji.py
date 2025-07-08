#!/usr/bin/env python3
"""
Teste final: criar pedido com rede '⚡ Lightning' para verificar na interface
"""

import json
import requests
import time

def teste_final_emoji():
    """Testa pedido com emoji para verificar se aparece na interface"""
    
    print("⚡ TESTE FINAL: REDE COM EMOJI")
    print("=" * 40)
    
    chat_id = f"TESTE_EMOJI_{int(time.time())}"
    
    payload = {
        "chatid": chat_id,
        "moeda": "BTC",
        "rede": "⚡ Lightning",  # Com emoji, como vem do bot
        "amount_in_cents": 15000,  # R$ 150,00
        "taxa": 7.5,
        "address": "voltzapi@tria.com",
        "forma_pagamento": "PIX",
        "send": 0.000428,
        "user_id": int(time.time()),
        "depix_id": f"DEPIX_{chat_id}",
        "status": "pending",
        "comprovante": "Lightning Invoice"
    }
    
    print(f"📤 Criando pedido com rede: '{payload['rede']}'")
    print(f"📦 Chat ID: {chat_id}")
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "https://useghost.squareweb.app/rest/deposit.php",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get('success'):
                deposit_id = resp_json.get('id')
                print(f"✅ Pedido criado! ID: {deposit_id}")
                print(f"🔍 Chat ID para buscar: {chat_id}")
                print(f"🆔 ID do depósito: {deposit_id}")
                
                print("\n🎯 VERIFICAÇÃO FINAL:")
                print("1. Acesse a interface: https://useghost.squareweb.app/transacoes.php")
                print("2. Verifique se aparecem os pedidos:")
                print(f"   • ID 63 (rede: 'lightning')")
                print(f"   • ID {deposit_id} (rede: '⚡ Lightning')")
                print("\n✅ Se ambos aparecerem, a integração está funcionando!")
                print("❌ Se apenas um aparecer, há filtro na interface!")
                
            else:
                print(f"❌ Erro: {resp_json}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exceção: {e}")

if __name__ == "__main__":
    teste_final_emoji()
