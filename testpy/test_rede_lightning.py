#!/usr/bin/env python3
"""
Script para testar especificamente o campo 'rede' e verificar se aparece na interface
"""

import json
import requests
import time

def testar_diferentes_redes():
    """Testa diferentes valores para o campo 'rede' para ver qual aparece na interface"""
    
    print("🧪 TESTE DE CAMPO REDE PARA INTERFACE")
    print("=" * 60)
    
    # Testa diferentes valores de rede que deveriam aparecer na interface
    redes_teste = [
        "lightning",          # Valor simples
        "⚡ Lightning",       # Com emoji (como no bot)
        "Lightning",          # Capitalizado
        "⚡Lightning",        # Emoji sem espaço
    ]
    
    for i, rede in enumerate(redes_teste, 1):
        print(f"\n🔧 TESTE {i}/{len(redes_teste)}: rede = '{rede}'")
        print("-" * 40)
        
        chat_id = f"TESTE_REDE_{i}_{int(time.time())}"
        
        payload = {
            "chatid": chat_id,
            "moeda": "BTC",
            "rede": rede,  # Campo sendo testado
            "amount_in_cents": 5000,  # R$ 50,00
            "taxa": 2.5,
            "address": "voltzapi@tria.com",
            "forma_pagamento": "PIX",
            "send": 0.000142,
            "user_id": int(time.time()) + i,
            "depix_id": f"DEPIX_{chat_id}",
            "status": "pending",
            "comprovante": "Lightning Invoice Test"
        }
        
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
                    print(f"   Chat ID: {chat_id}")
                    print(f"   Rede: '{rede}'")
                else:
                    print(f"❌ Erro: {resp_json}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Exceção: {e}")
        
        # Pausa entre testes
        if i < len(redes_teste):
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🎯 AGORA VERIFIQUE A INTERFACE:")
    print("   https://useghost.squareweb.app/transacoes.php")
    print("=" * 60)
    print("\n📋 CHAT IDs CRIADOS PARA VERIFICAÇÃO:")
    
    # Lista os chat IDs criados para facilitar a verificação
    base_time = int(time.time())
    for i, rede in enumerate(redes_teste, 1):
        chat_id = f"TESTE_REDE_{i}_{base_time}"
        print(f"   • {rede}: {chat_id}")

if __name__ == "__main__":
    testar_diferentes_redes()
