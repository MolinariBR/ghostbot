#!/usr/bin/env python3
import sqlite3

try:
    conn = sqlite3.connect('../ghostbackend/data/deposit.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, depix_id, rede, blockchainTxID, status, comprovante, chatid
        FROM deposit 
        WHERE rede LIKE '%lightning%' 
        ORDER BY id DESC LIMIT 10
    """)
    
    depositos = cursor.fetchall()
    
    print(f"🔍 Últimos {len(depositos)} depósitos Lightning:")
    print("=" * 70)
    
    for dep in depositos:
        print(f"ID: {dep[0]} | Depix: {dep[1]}")
        print(f"Rede: {dep[2]}")
        print(f"TxID: {dep[3]}")
        print(f"Status: {dep[4]}")
        print(f"Chat: {dep[6]}")
        print(f"Comprovante: {dep[5] or 'VAZIO'}")
        print("-" * 50)
    
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
