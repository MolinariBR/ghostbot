#!/usr/bin/env python3
"""
Simular confirmação PIX para depósitos Lightning de teste
Adiciona blockchainTxID para depósitos Lightning que estão com null
"""

import sqlite3
import time

def conectar_banco():
    """Conecta ao banco SQLite do backend"""
    try:
        conn = sqlite3.connect('../ghostbackend/data/deposit.db')
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar banco: {e}")
        return None

def atualizar_depositos_lightning():
    """Atualiza depósitos Lightning com blockchainTxID simulado"""
    
    conn = conectar_banco()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Buscar depósitos Lightning sem blockchainTxID
        cursor.execute("""
            SELECT id, depix_id, chatid, amount_in_cents 
            FROM deposit 
            WHERE rede LIKE '%lightning%' 
            AND (blockchainTxID IS NULL OR blockchainTxID = '')
            AND status = 'pending'
            ORDER BY id DESC
        """)
        
        depositos = cursor.fetchall()
        
        print(f"🔍 Encontrados {len(depositos)} depósitos Lightning sem PIX confirmado")
        
        if not depositos:
            print("✅ Não há depósitos para atualizar")
            return
        
        for deposito in depositos:
            deposit_id, depix_id, chatid, amount_cents = deposito
            
            # Gerar blockchainTxID simulado
            timestamp = int(time.time())
            blockchain_txid = f"pix_confirmado_{timestamp}_{deposit_id}"
            
            # Atualizar o depósito
            cursor.execute("""
                UPDATE deposit 
                SET blockchainTxID = ?, status = 'confirmed'
                WHERE id = ?
            """, (blockchain_txid, deposit_id))
            
            print(f"✅ Depósito {depix_id} (ID: {deposit_id})")
            print(f"   💰 R$ {amount_cents/100:.2f}")
            print(f"   🔗 TxID: {blockchain_txid}")
            print(f"   💬 Chat: {chatid}")
            print()
        
        conn.commit()
        print(f"🎉 {len(depositos)} depósitos atualizados com PIX confirmado!")
        print()
        print("🚀 PRÓXIMO PASSO:")
        print("O cron Lightning deve detectar esses depósitos na próxima execução")
        print("e solicitar invoice Lightning via Telegram!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🧪 SIMULANDO CONFIRMAÇÃO PIX PARA LIGHTNING")
    print("=" * 50)
    atualizar_depositos_lightning()
