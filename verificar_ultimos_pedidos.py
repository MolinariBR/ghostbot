#!/usr/bin/env python3
import requests
import json

def verificar_ultimo_pedido():
    try:
        response = requests.get('https://useghost.squareweb.app/rest/deposit.php', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'deposits' in data and len(data['deposits']) > 0:
                # Pega os últimos 3 pedidos
                for i, pedido in enumerate(data['deposits'][:3]):
                    print(f"📋 PEDIDO {i+1}:")
                    print(f"   📋 ID: {pedido.get('id')}")
                    print(f"   🆔 Depix ID: {pedido.get('depix_id')}")
                    print(f"   💰 Valor: R$ {pedido.get('amount_in_cents', 0)/100}")
                    print(f"   ⚡ Lightning: {pedido.get('address')}")
                    print(f"   📊 Status: {pedido.get('status')}")
                    print(f"   📅 Criado: {pedido.get('created_at')}")
                    print("-" * 40)
            else:
                print("❌ Nenhum depósito encontrado")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_ultimo_pedido()
