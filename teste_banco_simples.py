#!/usr/bin/env python3
"""
Teste simples para verificar acesso ao banco SQLite
"""

import sqlite3

def testar_banco():
    try:
        print("🔍 Testando conexão com deposit.db...")
        conn = sqlite3.connect('data/deposit.db')
        cursor = conn.cursor()
        
        # Verificar se tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='deposit';")
        tabela = cursor.fetchone()
        
        if tabela:
            print("✅ Tabela 'deposit' encontrada")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM deposit")
            count = cursor.fetchone()[0]
            print(f"📊 Total de registros: {count}")
            
            # Listar últimos 5 depix_ids
            cursor.execute("SELECT depix_id, amount_in_cents, blockchainTxID FROM deposit ORDER BY id DESC LIMIT 5")
            registros = cursor.fetchall()
            
            if registros:
                print("\n📋 Últimos 5 registros:")
                for reg in registros:
                    print(f"   • {reg[0]} - R$ {reg[1]/100:.2f} - TxID: {reg[2] or 'N/A'}")
            else:
                print("❌ Nenhum registro encontrado")
                
        else:
            print("❌ Tabela 'deposit' não encontrada")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    testar_banco()
