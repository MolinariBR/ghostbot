import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/deposit.db')

def criar_banco_depositos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deposit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chatid TEXT NOT NULL,
            amount_in_cents INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print('Banco deposit.db criado ou atualizado com sucesso.')

if __name__ == '__main__':
    criar_banco_depositos()
