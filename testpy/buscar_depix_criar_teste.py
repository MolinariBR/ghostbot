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

# Função para criar depósito de teste mesmo sem API (para quando depix_ids estão expirados)
def criar_deposito_teste_forcado():
    """Cria depósito Lightning teste com dados simulados mas realistas"""
    try:
        conn = sqlite3.connect('/home/mau/bot/ghostbackend/data/deposit.db')
        cursor = conn.cursor()
        
        timestamp = int(time.time())
        novo_depix = f"ln_teste_{timestamp}"
        
        # Dados simulados mas realistas
        dados_simulados = {
            'amount': 10000,  # R$ 100,00 em centavos
            'blockchainTxID': f"0x{timestamp:x}{'a1b2c3d4e5f6789' * 3}"[:64]  # TxID realista
        }
        
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
            dados_simulados['amount'],
            '0.005',
            'BTC',
            'lightning',
            'voltz@mail.com',
            'PIX',
            str(dados_simulados['amount']),
            'confirmed',
            dados_simulados['blockchainTxID'],
            '',  # Vazio para processar Lightning
            '7910260237'
        )
        
        cursor.execute(sql, valores)
        conn.commit()
        conn.close()
        
        print(f"✅ Criado (simulado): {novo_depix}")
        print(f"   💰 R$ {dados_simulados['amount']/100:.2f}")
        print(f"   🔗 {dados_simulados['blockchainTxID']}")
        return novo_depix
        
    except Exception as e:
        print(f"❌ Erro SQLite: {e}")
        return None

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
        conn = sqlite3.connect('/home/mau/bot/ghostbackend/data/deposit.db')
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
    
    depositos_criados = 0
    
    for depix_id in DEPIX_IDS:
        print(f"\n📋 {depix_id}")
        
        dados = buscar_depix_api(depix_id)
        if dados:
            print(f"   💰 R$ {dados.get('amount', 0)/100:.2f}")
            print(f"   🔗 {dados.get('blockchainTxID', 'N/A')}")
            
            criar_deposito_teste(dados, depix_id)
            depositos_criados += 1
        else:
            print("   ❌ Não encontrado")
        
        time.sleep(1)
    
    # Se nenhum depósito foi criado com dados reais, cria um simulado para teste
    if depositos_criados == 0:
        print(f"\n🔄 Nenhum depix_id real encontrado. Criando depósito simulado para teste...")
        criar_deposito_teste_forcado()
        depositos_criados = 1
    
    print(f"\n🚀 TESTE O CRON:")
    print("curl 'https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025'")

if __name__ == "__main__":
    main()
