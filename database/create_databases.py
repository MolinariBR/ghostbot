"""
Script para criar e inicializar os bancos de dados SQLite do sistema.
"""
import sqlite3
import os
from pathlib import Path

# Diretório onde os bancos de dados serão armazenados
DB_DIR = Path(__file__).parent

# Esquema para o banco de dados de usuários (users.db)
USERS_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    currency TEXT NOT NULL,
    address TEXT,
    balance DECIMAL(20, 8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, currency)
);
"""

# Esquema para o banco de dados de depósitos (deposit.db)
DEPOSIT_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tx_hash TEXT UNIQUE NOT NULL,
    currency TEXT NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    status TEXT NOT NULL,
    confirmations INTEGER DEFAULT 0,
    required_confirmations INTEGER DEFAULT 1,
    address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS deposit_addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    currency TEXT NOT NULL,
    address TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

# Esquema para o banco de dados de serviços (servico.db)
SERVICO_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price_brl DECIMAL(10, 2) NOT NULL,
    price_depix DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    amount_brl DECIMAL(10, 2) NOT NULL,
    amount_depix DECIMAL(10, 8) NOT NULL,
    payment_tx TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);
"""

# Esquema para o banco de dados de cotações (cotacao.db)
COTACAO_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_currency TEXT NOT NULL,
    target_currency TEXT NOT NULL,
    rate DECIMAL(20, 8) NOT NULL,
    source TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rate_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_currency TEXT NOT NULL,
    target_currency TEXT NOT NULL,
    rate DECIMAL(20, 8) NOT NULL,
    source TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def create_database(db_name, schema):
    """Cria um banco de dados com o esquema fornecido."""
    db_path = DB_DIR / f"{db_name}.db"
    conn = sqlite3.connect(db_path)
    
    try:
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        print(f"Banco de dados {db_name}.db criado com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao criar o banco de dados {db_name}.db: {e}")
    finally:
        conn.close()

def init_databases():
    """Inicializa todos os bancos de dados."""
    # Cria o diretório de bancos de dados se não existir
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Cria cada banco de dados
    create_database("users", USERS_DB_SCHEMA)
    create_database("deposit", DEPOSIT_DB_SCHEMA)
    create_database("servico", SERVICO_DB_SCHEMA)
    create_database("cotacao", COTACAO_DB_SCHEMA)

if __name__ == "__main__":
    print("Inicializando bancos de dados...")
    init_databases()
    print("Inicialização concluída!")
