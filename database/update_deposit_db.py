"""
Script para atualizar o esquema do banco de dados deposit.db.
"""
import sqlite3
import os
from pathlib import Path

# Diretório onde os bancos de dados estão armazenados
DB_DIR = Path(__file__).parent
DEPOSIT_DB_PATH = DB_DIR / 'deposit.db'

def atualizar_esquema():
    """Atualiza o esquema do banco de dados deposit.db."""
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(str(DEPOSIT_DB_PATH))
        cursor = conn.cursor()
        
        # Verifica se a tabela pix_transactions já existe
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='pix_transactions'
        """)
        
        if not cursor.fetchone():
            # Cria a tabela pix_transactions se não existir
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pix_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_id TEXT NOT NULL UNIQUE,
                amount_brl DECIMAL(10, 2) NOT NULL,
                amount_crypto DECIMAL(20, 8) NOT NULL,
                crypto_currency TEXT NOT NULL,
                crypto_address TEXT NOT NULL,
                qr_image_url TEXT,
                qr_copy_paste TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
            )
            """)
            
            # Cria índices para melhorar a performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pix_transactions_user_id ON pix_transactions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pix_transactions_status ON pix_transactions(status)")
            
            print("✅ Tabela 'pix_transactions' criada com sucesso!")
        else:
            print("ℹ️  A tabela 'pix_transactions' já existe.")
        
        # Atualiza a tabela deposits para incluir o campo de método de pagamento
        try:
            cursor.execute("ALTER TABLE deposits ADD COLUMN payment_method TEXT")
            print("✅ Coluna 'payment_method' adicionada à tabela 'deposits'")
        except sqlite3.OperationalError:
            # A coluna já existe
            print("ℹ️  A coluna 'payment_method' já existe na tabela 'deposits'")
        
        conn.commit()
        print("✅ Atualização do banco de dados concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar o banco de dados: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Atualizando o banco de dados deposit.db...")
    atualizar_esquema()
