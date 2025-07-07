#!/usr/bin/env python3
"""
Criar depósitos Lightning REAIS no servidor via API
Usando os depix_ids reais fornecidos pelo usuário
"""

import requests
import time
import json

# Depix IDs reais fornecidos pelo usuário
DEPIX_IDS_REAIS = [
    "0197e0ed06537df9820a28f5a5380a3b",
    "0197e10b5b8f7df9a6bf9430188534e4", 
    "0197e12300eb7df9808ca5d7719ea40e",
    "0197e5214a377dfaae6e541f68057444"
]

def criar_deposito_lightning_api(depix_id_base, valor_reais=25.0):
    """Cria depósito Lightning via API REST do servidor"""
    
    timestamp = int(time.time())
    depix_id = f"ln_real_{timestamp}_{depix_id_base[-6:]}"
    
    payload = {
        "depix_id": depix_id,
        "chatid": "7910260237",  # Seu chat ID real
        "amount_in_cents": int(valor_reais * 100),
        "taxa": "0.02",
        "moeda": "BTC",
        "rede": "⚡ Lightning",
        "address": "lightning@voltz.app",
        "forma_pagamento": "PIX",
        "send": str(int(valor_reais * 100)),
        "status": "confirmed",  # PIX já confirmado
        "blockchainTxID": f"pix_real_{timestamp}_{depix_id_base[-6:]}",
        "comprovante": "",  # Vazio para ser processado
        "user_id": "7910260237"
    }
    
    try:
        url = "https://useghost.squareweb.app/rest/deposit.php"
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Depósito criado: {depix_id}")
            print(f"   💰 R$ {valor_reais:.2f}")
            print(f"   🔗 TxID: {payload['blockchainTxID']}")
            print(f"   🔗 Base: {depix_id_base}")
            return True
        else:
            print(f"❌ Erro API {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar {depix_id}: {e}")
        return False

def main():
    print("🚀 CRIANDO DEPÓSITOS LIGHTNING REAIS NO SERVIDOR")
    print("=" * 60)
    print("📋 Usando depix_ids reais fornecidos pelo usuário")
    print()
    
    depositos_criados = []
    
    for i, depix_id_real in enumerate(DEPIX_IDS_REAIS, 1):
        print(f"🔹 Criando depósito {i}/{len(DEPIX_IDS_REAIS)} baseado em {depix_id_real}...")
        
        valor = 1.0 + (i * 1)  # R$ 2, 3, 4, 5 (valores baixos para saldo de 2975 sats)
        
        if criar_deposito_lightning_api(depix_id_real, valor):
            depositos_criados.append(depix_id_real)
            time.sleep(2)  # Aguardar entre requisições
        
        print()
    
    print(f"🎉 RESUMO: {len(depositos_criados)}/{len(DEPIX_IDS_REAIS)} depósitos criados")
    
    if depositos_criados:
        print()
        print("🚀 PRÓXIMOS PASSOS:")
        print("1. Os depósitos foram criados no servidor com PIX confirmado")
        print("2. Execute o cron Lightning para detectá-los:")
        print("   curl 'https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025'")
        print("3. O bot deve solicitar invoice Lightning no Telegram")

if __name__ == "__main__":
    main()
