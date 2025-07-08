#!/usr/bin/env python3
"""
Criar depósitos Lightning de teste com valores realistas
"""

import sqlite3
import time

def criar_deposito_teste():
    """Cria depósitos Lightning teste"""
    try:
        conn = sqlite3.connect('../ghostbackend/data/deposit.db')
        cursor = conn.cursor()
        
        depositos = [
            {'valor': 1000, 'txid': 'bc1q123abc456def789', 'base': '380a3b'},
            {'valor': 500, 'txid': 'bc1q456def789abc123', 'base': '8534e4'},
            {'valor': 1500, 'txid': 'bc1q789abc123def456', 'base': '9ea40e'},
            {'valor': 2000, 'txid': 'bc1qabc123def456789', 'base': '057444'}
        ]
        
        timestamp = int(time.time())
        
        for i, dep in enumerate(depositos):
            depix_id = f"ln_teste_{timestamp}_{i}_{dep['base']}"
            
            sql = """
            INSERT INTO deposit (
                depix_id, chatid, amount_in_cents, taxa, moeda, rede, address,
                forma_pagamento, send, status, blockchainTxID, comprovante, 
                user_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """
            
            valores = (
                depix_id,
                '7910260237',
                dep['valor'],
                '0.005',
                'BTC',
                'lightning',
                'voltz@mail.com',
                'PIX',
                str(dep['valor']),
                'confirmed',
                dep['txid'],
                '',
                '7910260237'
            )
            
            cursor.execute(sql, valores)
            print(f"✅ {depix_id} - R$ {dep['valor']/100:.2f}")
        
        conn.commit()
        conn.close()
        print(f"\n🚀 TESTE:")
        print("curl 'https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025'")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    criar_deposito_teste()
