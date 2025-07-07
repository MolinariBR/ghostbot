#!/usr/bin/env python3
"""
Criar depósitos Lightning para teste usando depix_ids reais
Puxa dados da API real e cria registros para teste do fluxo completo
"""

import requests
import sqlite3
import json
import time

# Depix IDs reais para teste
DEPIX_IDS_REAIS = [
    "0197e0ed06537df9820a28f5a5380a3b"
    # "0197e10b5b8f7df9a6bf9430188534e4", 
    # "0197e12300eb7df9808ca5d7719ea40e",
    # "0197e5214a377dfaae6e541f68057444"
]

def buscar_dados_depix_real(depix_id):
    """Busca dados do depix_id real na API"""
    try:
        url = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('deposits') and len(data['deposits']) > 0:
                return data['deposits'][0]
        
        print(f"❌ Depix {depix_id} não encontrado na API")
        return None
        
    except Exception as e:
        print(f"❌ Erro ao buscar {depix_id}: {e}")
        return None

def criar_deposito_teste_local(dados_real, chat_id_teste="7910260237"):
    """Cria depósito Lightning para teste baseado em dados reais"""
    
    # Gerar novo depix_id para teste
    timestamp = int(time.time())
    depix_id_teste = f"teste_real_{timestamp}_{dados_real['depix_id'][-6:]}"
    
    dados_teste = {
        'depix_id': depix_id_teste,
        'chatid': chat_id_teste,
        'amount_in_cents': dados_real['amount_in_cents'],
        'taxa': dados_real['taxa'],
        'moeda': 'BTC',
        'rede': 'lightning',
        'address': 'voltz@mail.com',
        'forma_pagamento': 'PIX',
        'send': dados_real['send'],
        'status': 'pending',  # Manter pending para teste
        'blockchainTxID': dados_real.get('blockchainTxID') or f"teste_txid_{timestamp}",
        'comprovante': f"Teste Lightning baseado em {dados_real['depix_id']}",
        'user_id': chat_id_teste
    }
    
    return dados_teste, depix_id_teste

def inserir_via_api_backend(dados_teste):
    """Insere depósito via API do backend"""
    try:
        url = "https://useghost.squareweb.app/rest/deposit.php"
        
        payload = {
            "depix_id": dados_teste['depix_id'],
            "chatid": dados_teste['chatid'],
            "amount_in_cents": dados_teste['amount_in_cents'],
            "taxa": dados_teste['taxa'],
            "moeda": dados_teste['moeda'],
            "rede": dados_teste['rede'],
            "address": dados_teste['address'],
            "forma_pagamento": dados_teste['forma_pagamento'],
            "send": dados_teste['send'],
            "status": dados_teste['status'],
            "comprovante": dados_teste['comprovante'],
            "user_id": dados_teste['user_id']
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Depósito {dados_teste['depix_id']} criado via API")
            return True
        else:
            print(f"❌ Erro API {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao inserir via API: {e}")
        return False

def simular_webhook_confirmacao(depix_id_teste, blockchain_txid):
    """Simula webhook de confirmação PIX"""
    try:
        url = "https://useghost.squareweb.app/rest/webhook_depix.php"
        
        payload = {
            "depix_id": depix_id_teste,
            "blockchainTxID": blockchain_txid,
            "status": "confirmed"
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Webhook confirmação PIX enviado para {depix_id_teste}")
            return True
        else:
            print(f"⚠️ Webhook response {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return False

def main():
    print("🧪 CRIANDO DEPÓSITOS LIGHTNING PARA TESTE")
    print("=" * 50)
    
    depositos_criados = []
    
    for depix_id_real in DEPIX_IDS_REAIS:
        print(f"\n🔍 Processando {depix_id_real}...")
        
        # Buscar dados reais
        dados_real = buscar_dados_depix_real(depix_id_real)
        if not dados_real:
            continue
            
        print(f"✅ Dados encontrados: R$ {dados_real['amount_in_cents']/100:.2f}")
        
        # Criar dados de teste
        dados_teste, depix_id_teste = criar_deposito_teste_local(dados_real)
        
        # Inserir via API
        if inserir_via_api_backend(dados_teste):
            # Simular confirmação PIX
            time.sleep(2)
            if simular_webhook_confirmacao(depix_id_teste, dados_teste['blockchainTxID']):
                depositos_criados.append({
                    'depix_id': depix_id_teste,
                    'valor': dados_real['amount_in_cents']/100,
                    'blockchainTxID': dados_teste['blockchainTxID'],
                    'chatid': dados_teste['chatid']
                })
            time.sleep(1)
    
    print(f"\n🎉 RESUMO - {len(depositos_criados)} depósitos criados:")
    print("=" * 50)
    
    for dep in depositos_criados:
        print(f"✅ {dep['depix_id']}")
        print(f"   💰 R$ {dep['valor']:.2f}")
        print(f"   🔗 {dep['blockchainTxID']}")
        print(f"   💬 Chat: {dep['chatid']}")
        print()
    
    if depositos_criados:
        print("🚀 PRÓXIMOS PASSOS:")
        print("1. Execute o endpoint cron Lightning para detectar os depósitos")
        print("2. O bot deve solicitar invoice Lightning via Telegram")
        print("3. Teste enviando um invoice Lightning no chat")
        print(f"\n🔗 Teste o cron: https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025")

if __name__ == "__main__":
    main()
