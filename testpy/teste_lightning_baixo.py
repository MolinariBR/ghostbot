#!/usr/bin/env python3
"""
TESTE LIGHTNING - Valores Baixos (Saldo: 3378 sats)
===================================================

Teste específico para valores baixos que cabem no saldo atual.
Máximo: R$ 4,00 (~800 sats)
"""

import requests
import json
import time
import sys
import os

# Adiciona path do ghost
sys.path.append('/home/mau/bot/ghost')

def verificar_saldo_voltz():
    """
    Verifica o saldo atual da carteira Voltz.
    """
    print("💰 Verificando saldo da carteira Voltz...")
    
    try:
        # Tenta verificar via endpoint direto
        url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
        payload = {"action": "get_balance"}
        
        response = requests.post(url, json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'balance' in data:
                    balance_sats = data['balance']
                    balance_brl = balance_sats * 350000 / 100000000  # Convertendo para BRL
                    print(f"✅ Saldo: {balance_sats} sats (~R$ {balance_brl:.2f})")
                    return balance_sats
                else:
                    print("⚠️ Saldo não encontrado na resposta")
                    return 3378  # Valor conhecido
            except json.JSONDecodeError:
                print("⚠️ Resposta não é JSON")
                return 3378
        else:
            print(f"⚠️ Usando saldo conhecido: 3378 sats")
            return 3378
            
    except Exception as e:
        print(f"❌ Erro ao verificar saldo: {e}")
        print(f"⚠️ Usando saldo conhecido: 3378 sats")
        return 3378

def criar_teste_valor_baixo(depix_id, valor_sats=500):
    """
    Cria teste com valor muito baixo.
    """
    print(f"🆕 Criando teste Lightning - {valor_sats} sats...")
    
    # TxID simulado
    import hashlib
    txid = hashlib.md5(f"low_value_test_{depix_id}_{int(time.time())}".encode()).hexdigest()
    
    # Converte sats para BRL (aprox)
    valor_brl = valor_sats * 350000 / 100000000
    valor_centavos = int(valor_brl * 100)
    taxa_centavos = int(valor_centavos * 0.05)  # 5%
    
    payload = {
        "chatid": "123456789",
        "user_id": 123456789,
        "depix_id": depix_id,
        "blockchainTxID": txid,
        "status": "confirmado",
        "amount_in_cents": valor_centavos,
        "moeda": "BTC",
        "rede": "⚡ Lightning",
        "send": valor_sats,
        "taxa": taxa_centavos / 100,
        "address": "voltzapi@tria.com",
        "metodo_pagamento": "PIX",
        "forma_pagamento": "PIX",
        "comprovante": f"Lightning Test - {valor_sats} sats"
    }
    
    print(f"💰 Valor: R$ {valor_brl:.2f} ({valor_sats} sats)")
    print(f"🔗 TxID: {txid}")
    
    try:
        url = "https://useghost.squareweb.app/rest/deposit.php"
        response = requests.post(url, json=payload, timeout=15)
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Depósito criado (ID: {result.get('id')})")
                return True
        
        print(f"⚠️ Problema na criação")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def processar_lightning(depix_id):
    """
    Processa Lightning via Voltz.
    """
    print(f"\n⚡ Processando Lightning para {depix_id}...")
    
    try:
        # Método 1: Processamento específico
        url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
        payload = {
            "action": "process_deposit",
            "depix_id": depix_id
        }
        
        response = requests.post(url, json=payload, timeout=30)
        print(f"POST Status: {response.status_code}")
        print(f"POST Resposta: {response.text[:300]}...")
        
        time.sleep(2)
        
        # Método 2: Cron geral
        response = requests.get(url, timeout=30)
        print(f"GET Status: {response.status_code}")
        print(f"GET Resposta: {response.text[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False

def verificar_invoice(depix_id, max_tentativas=8):
    """
    Verifica se foi gerado invoice.
    """
    print(f"\n🔍 Verificando invoice para {depix_id}...")
    
    url = "https://useghost.squareweb.app/voltz/voltz_status.php"
    
    for tentativa in range(1, max_tentativas + 1):
        print(f"\n   Tentativa {tentativa}/{max_tentativas}...")
        
        try:
            payload = {"depix_id": depix_id}
            response = requests.post(url, json=payload, timeout=15)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   JSON: {str(data)[:200]}...")
                    
                    if data.get('invoice'):
                        print(f"\n🎉 INVOICE GERADO!")
                        print(f"⚡ Invoice: {data['invoice']}")
                        return data
                    else:
                        print(f"   ⏳ Ainda processando...")
                        
                except json.JSONDecodeError:
                    print(f"   ⚠️ Resposta não é JSON")
            else:
                print(f"   ❌ Erro HTTP: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        if tentativa < max_tentativas:
            print(f"   ⏱️ Aguardando 4 segundos...")
            time.sleep(4)
    
    print(f"\n⏰ Invoice não foi gerado após {max_tentativas} tentativas")
    return None

def teste_valor_especifico(depix_id, valor_sats):
    """
    Executa teste com valor específico.
    """
    print(f"\n🧪 TESTE: {valor_sats} sats")
    print("=" * 40)
    
    # 1. Verificar saldo antes
    saldo = verificar_saldo_voltz()
    if saldo < valor_sats:
        print(f"❌ Saldo insuficiente: {saldo} < {valor_sats}")
        return False
    
    # 2. Criar depósito
    if not criar_teste_valor_baixo(depix_id, valor_sats):
        print("❌ Falha na criação")
        return False
    
    time.sleep(3)
    
    # 3. Processar
    if not processar_lightning(depix_id):
        print("❌ Falha no processamento")
        return False
    
    time.sleep(5)
    
    # 4. Verificar invoice
    resultado = verificar_invoice(depix_id)
    
    if resultado and resultado.get('invoice'):
        print(f"\n🎉 SUCESSO! Invoice de {valor_sats} sats gerado!")
        return True
    else:
        print(f"\n❌ Falha no invoice para {valor_sats} sats")
        return False

def main():
    print("🧪 TESTE LIGHTNING - VALORES BAIXOS")
    print("=" * 40)
    print("💰 Saldo disponível: 3378 sats")
    print("🎯 Testando valores pequenos...")
    
    # Seus depix_ids
    depix_ids = [
        "0197e0ed06537df9820a28f5a5380a3b",
        "0197e10b5b8f7df9a6bf9430188534e4",
        "0197e12300eb7df9808ca5d7719ea40e",
        "0197e5214a377dfaae6e541f68057444"
    ]
    
    print(f"\n🎯 Depix IDs:")
    for i, depix_id in enumerate(depix_ids, 1):
        print(f"{i}. {depix_id}")
    
    try:
        escolha = int(input(f"\nEscolha (1-{len(depix_ids)}): ")) - 1
        if escolha < 0 or escolha >= len(depix_ids):
            print("❌ Escolha inválida")
            return
        
        depix_id = depix_ids[escolha]
        
    except ValueError:
        print("❌ Número inválido")
        return
    
    # Valores de teste (crescente)
    valores_teste = [300, 500, 800, 1000]  # sats
    
    print(f"\n🎯 Testando com depix_id: {depix_id}")
    print(f"💡 Valores de teste: {valores_teste} sats")
    
    for valor in valores_teste:
        sucesso = teste_valor_especifico(depix_id, valor)
        
        if sucesso:
            print(f"\n🎉 PRIMEIRO SUCESSO COM {valor} SATS!")
            print(f"💡 Valor mínimo funcional encontrado!")
            break
        
        print(f"\n⏭️ Tentando próximo valor...")
        time.sleep(2)
    
    print(f"\n✅ Teste concluído!")

if __name__ == "__main__":
    main()
