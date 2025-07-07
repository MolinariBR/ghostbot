#!/usr/bin/env python3
import sqlite3

try:
    conn = sqlite3.connect('../ghostbackend/data/deposit.db')
    cursor = conn.cursor()
    
    # Exata mesma query do endpoint
    sql = """
        SELECT * FROM deposit 
        WHERE rede LIKE '%lightning%' 
        AND blockchainTxID IS NOT NULL 
        AND blockchainTxID != ''
        AND status NOT IN ('completed', 'cancelled', 'failed')
        AND depix_id IS NOT NULL 
        AND chatid IS NOT NULL
    """
    
    cursor.execute(sql)
    depositos = cursor.fetchall()
    
    print(f"🔍 Query do endpoint encontrou: {len(depositos)} depósitos")
    print("=" * 70)
    
    if depositos:
        # Mostrar apenas os primeiros 3 para debug
        for i, dep in enumerate(depositos[:3], 1):
            print(f"DEPÓSITO {i}:")
            print(f"  ID: {dep[0]}")
            print(f"  Depix ID: {dep[12]}")
            print(f"  Rede: {dep[6]}")
            print(f"  Status: {dep[10]}")
            print(f"  BlockchainTxID: {dep[1]}")
            print(f"  ChatID: {dep[2]}")
            print()
    else:
        print("❌ Nenhum depósito encontrado com a query do endpoint")
        
        # Debug: vamos ver o que há de diferente
        print("\n🔍 DEBUGANDO - Vamos ver os depósitos Lightning:")
        cursor.execute("SELECT id, blockchainTxID, status, rede, chatid, depix_id FROM deposit WHERE rede LIKE '%lightning%' ORDER BY id DESC LIMIT 5")
        debug_deps = cursor.fetchall()
        
        for dep in debug_deps:
            print(f"ID: {dep[0]}")
            print(f"  TxID: '{dep[1]}' (NULL: {dep[1] is None}, Empty: {dep[1] == ''})")
            print(f"  Status: '{dep[2]}'")
            print(f"  Rede: '{dep[3]}'")
            print(f"  ChatID: '{dep[4]}' (NULL: {dep[4] is None})")
            print(f"  DepixID: '{dep[5]}' (NULL: {dep[5] is None})")
            print()
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
