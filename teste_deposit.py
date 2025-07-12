import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data/deposit.db')

# Dados de teste compatíveis com o schema local
deposito_teste = {
    "depix_id": "test123",
    "chatid": "999999",
    "amount_in_cents": 5000,
    "send": 0.0001,
    "rede": "lightning",
    "status": "pending",
    "created_at": datetime.now().isoformat(),
    "blockchainTxID": "txid_test_abc"
}

def inserir_deposito():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO deposit (
            depix_id, chatid, amount_in_cents, send, rede, status, created_at, blockchainTxID
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        deposito_teste["depix_id"],
        deposito_teste["chatid"],
        deposito_teste["amount_in_cents"],
        deposito_teste["send"],
        deposito_teste["rede"],
        deposito_teste["status"],
        deposito_teste["created_at"],
        deposito_teste["blockchainTxID"]
    ))
    conn.commit()
    conn.close()
    print("Depósito inserido com sucesso!")

def consultar_depositos():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM deposit WHERE depix_id = ?", (deposito_teste["depix_id"],))
    resultado = cur.fetchone()
    conn.close()
    print("Resultado da consulta:")
    print(resultado)

if __name__ == "__main__":
    inserir_deposito()
    consultar_depositos()
