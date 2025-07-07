#!/usr/bin/env python3
"""
Buscar blockchainTxID dos depix_ids reais via API Depix
Criar depósitos Lightning de teste
"""

import requests
import sqlite3
import time

DEPIX_IDS = [
    "0197e0ed06537df9820a28f5a5380a3b",
    "0197e10b5b8f7df9a6bf9430188534e4", 
    "0197e12300eb7df9808ca5d7719ea40e",
    "0197e5214a377dfaae6e541f68057444"
]

def buscar_depix_api(depix_id):
    """Busca dados na API Depix"""
    try:
        url = f"https://depix.eulen.app/api/deposit-status?id={depix_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', {})
        return None
    except Exception as e:
        print(f"❌ Erro API: {e}")
        return None

def criar_deposito_teste(dados, depix_id):
    """Cria depósito Lightning teste no banco"""
    try:
        conn = sqlite3.connect('../ghostbackend/data/deposit.db')
        cursor = conn.cursor()
        
        timestamp = int(time.time())
        novo_depix = f"ln_teste_{timestamp}_{depix_id[-6:]}"
        
        sql = """
        INSERT INTO deposit (
            depix_id, chatid, amount_in_cents, taxa, moeda, rede, address,
            forma_pagamento, send, status, blockchainTxID, comprovante, 
            user_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """
        
        valores = (
            novo_depix,
            '7910260237',  # Chat teste
            dados.get('amount', 1000),  # Valor padrão se não encontrar
            '0.005',
            'BTC',
            'lightning',
            'voltz@mail.com',
            'PIX',
            str(dados.get('amount', 1000)),
            'confirmed',
            dados.get('blockchainTxID', f'teste_{timestamp}'),
            '',  # Vazio para processar
            '7910260237'
        )
        
        cursor.execute(sql, valores)
        conn.commit()
        conn.close()
        
        print(f"✅ Criado: {novo_depix}")
        return novo_depix
        
    except Exception as e:
        print(f"❌ Erro SQLite: {e}")
        return None

def main():
    print("🔍 BUSCANDO DEPIX_IDS REAIS")
    
    for depix_id in DEPIX_IDS:
        print(f"\n📋 {depix_id}")
        
        dados = buscar_depix_api(depix_id)
        if dados:
            print(f"   💰 R$ {dados.get('amount', 0)/100:.2f}")
            print(f"   🔗 {dados.get('blockchainTxID', 'N/A')}")
            
            criar_deposito_teste(dados, depix_id)
        else:
            print("   ❌ Não encontrado")
        
        time.sleep(1)
    
    print(f"\n🚀 TESTE O CRON:")
    print("curl 'https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025'")

if __name__ == "__main__":
    main()
