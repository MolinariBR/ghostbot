#!/usr/bin/env python3
"""
Criar depósitos Lightning REAIS no servidor via API - versão rápida
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

def criar_deposito_lightning_api(depix_id_base, valor_reais=2.0):
    """Cria depósito Lightning via API REST do servidor"""
    
    timestamp = int(time.time())
    depix_id = f"ln_baixo_{timestamp}_{depix_id_base[-6:]}"
    
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
        "blockchainTxID": f"pix_baixo_{timestamp}_{depix_id_base[-6:]}",
        "comprovante": "",  # Vazio para ser processado
        "user_id": "7910260237"
    }
    
    try:
        url = "https://useghost.squareweb.app/rest/deposit.php"
        print(f"🔄 Criando {depix_id} (R$ {valor_reais:.2f})...")
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Criado: {depix_id} - R$ {valor_reais:.2f}")
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar {depix_id}: {e}")
        return False

def main():
    print("🚀 CRIANDO DEPÓSITOS LIGHTNING COM VALORES BAIXOS")
    print("=" * 60)
    
    valores = [2.0, 3.0, 4.0, 5.0]  # R$ 2, 3, 4, 5
    
    for i, (depix_id_real, valor) in enumerate(zip(DEPIX_IDS_REAIS, valores), 1):
        print(f"📋 {i}/4: Baseado em {depix_id_real}")
        
        if criar_deposito_lightning_api(depix_id_real, valor):
            print("✅ Sucesso!")
        else:
            print("❌ Falhou!")
        
        print()
        time.sleep(1)  # Delay menor
    
    print("🎉 CONCLUÍDO!")
    print("\n🚀 PRÓXIMO PASSO:")
    print("Execute o cron Lightning:")
    print("curl 'https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025'")

if __name__ == "__main__":
    main()
