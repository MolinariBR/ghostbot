#!/usr/bin/env python3
"""
Script para testar se os pedidos estão sendo salvos na tabela deposit do servidor
"""

import json
import requests
import sys
import os
from datetime import datetime
import time

def testar_cadastro_servidor():
    """Testa se o pedido é salvo corretamente no servidor"""
    
    print("🧪 TESTE DE CADASTRO NO SERVIDOR")
    print("=" * 50)
    
    chat_id = f"TESTE_{int(time.time())}"  # ID único baseado no timestamp
    
    # Payload completo com todos os campos obrigatórios
    payload = {
        "chatid": chat_id,
        "moeda": "BTC",
        "rede": "Lightning", 
        "amount_in_cents": 10000,  # R$ 100,00
        "taxa": 5.0,
        "address": "voltzapi@tria.com",
        "forma_pagamento": "PIX",  # Campo obrigatório
        "send": 0.000285,
        "user_id": int(chat_id.replace('TESTE_', '')),
        "depix_id": f"DEPIX_{chat_id}",
        "status": "pending",
        "comprovante": "Lightning Invoice"
    }
    
    print("📤 Enviando pedido para o servidor...")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        # Envia para o servidor
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "https://useghost.squareweb.app/rest/deposit.php",
            json=payload,
            headers=headers,
            timeout=15
        )
        
        print(f"📊 Status HTTP: {response.status_code}")
        print(f"📝 Resposta: {response.text}")
        print()
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                if resp_json.get('success'):
                    deposit_id = resp_json.get('id')
                    print(f"✅ Pedido criado com sucesso! ID: {deposit_id}")
                    
                    # Aguarda um pouco e consulta de volta
                    print("\n⏳ Aguardando 2 segundos...")
                    time.sleep(2)
                    
                    # Consulta o pedido criado
                    print("🔍 Consultando pedido criado...")
                    consulta_resp = requests.get(
                        f"https://useghost.squareweb.app/rest/deposit.php?chatid={chat_id}",
                        timeout=10
                    )
                    
                    if consulta_resp.status_code == 200:
                        consulta_data = consulta_resp.json()
                        deposits = consulta_data.get('deposits', [])
                        
                        if deposits:
                            print(f"✅ Pedido encontrado na consulta!")
                            for deposit in deposits:
                                print(f"   • ID: {deposit.get('id')}")
                                print(f"   • Chat ID: {deposit.get('chatid')}")
                                print(f"   • Valor: R$ {float(deposit.get('amount_in_cents', 0))/100:.2f}")
                                print(f"   • Moeda: {deposit.get('moeda')}")
                                print(f"   • Status: {deposit.get('status')}")
                                print(f"   • Criado: {deposit.get('created_at')}")
                                print()
                            
                            print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
                            print("✅ O pedido foi salvo e consultado corretamente no servidor.")
                        else:
                            print("❌ Pedido não encontrado na consulta!")
                    else:
                        print(f"❌ Erro na consulta: {consulta_resp.status_code}")
                        
                else:
                    print(f"❌ Erro na resposta: {resp_json}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON da resposta: {e}")
                print(f"📄 Resposta bruta: {response.text}")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def consultar_ultimos_pedidos():
    """Consulta os últimos pedidos no servidor"""
    
    print("🔍 CONSULTANDO ÚLTIMOS PEDIDOS NO SERVIDOR")
    print("=" * 50)
    
    try:
        response = requests.get(
            "https://useghost.squareweb.app/rest/deposit.php",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            deposits = data.get('deposits', [])
            
            print(f"📊 Total de pedidos encontrados: {len(deposits)}")
            print()
            
            if deposits:
                print("📋 Últimos 5 pedidos:")
                for i, deposit in enumerate(deposits[:5], 1):
                    print(f"\n💰 Pedido #{i}:")
                    print(f"   • ID: {deposit.get('id')}")
                    print(f"   • Chat ID: {deposit.get('chatid')}")
                    print(f"   • Valor: R$ {float(deposit.get('amount_in_cents', 0))/100:.2f}")
                    print(f"   • Moeda: {deposit.get('moeda')}")
                    print(f"   • Rede: {deposit.get('rede')}")
                    print(f"   • Status: {deposit.get('status')}")
                    print(f"   • Forma Pgto: {deposit.get('forma_pagamento')}")
                    print(f"   • Criado: {deposit.get('created_at')}")
            else:
                print("📝 Nenhum pedido encontrado.")
                
        else:
            print(f"❌ Erro na consulta: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")

if __name__ == "__main__":
    try:
        consultar_ultimos_pedidos()
        print()
        testar_cadastro_servidor()
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
