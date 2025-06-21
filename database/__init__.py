"""
Módulo para gerenciamento dos bancos de dados SQLite.
"""
from pathlib import Path
import sqlite3
from typing import Optional, Dict, Any, List, Union
from contextlib import contextmanager

# Diretório base dos bancos de dados
DB_DIR = Path(__file__).parent
DATABASES = {
    'users': DB_DIR / 'users.db',
    'deposit': DB_DIR / 'deposit.db',
    'servico': DB_DIR / 'servico.db',
    'cotacao': DB_DIR / 'cotacao.db'
}

@contextmanager
def get_connection(db_name: str) -> sqlite3.Connection:
    """Retorna uma conexão com o banco de dados especificado.
    
    Args:
        db_name: Nome do banco de dados ('users', 'deposit', 'servico', 'cotacao')
        
    Yields:
        sqlite3.Connection: Conexão com o banco de dados
        
    Raises:
        ValueError: Se o nome do banco de dados for inválido
    """
    if db_name not in DATABASES:
        raise ValueError(f"Banco de dados inválido: {db_name}")
    
    conn = sqlite3.connect(DATABASES[db_name])
    conn.row_factory = sqlite3.Row  # Permite acesso aos campos por nome
    
    try:
        yield conn
    finally:
        conn.close()

def execute_query(db_name: str, query: str, params: tuple = (), fetch: str = 'all') -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
    """Executa uma consulta no banco de dados especificado.
    
    Args:
        db_name: Nome do banco de dados
        query: Consulta SQL a ser executada
        params: Parâmetros para a consulta
        fetch: Tipo de retorno ('all', 'one' ou 'none')
        
    Returns:
        List[Dict] ou Dict ou None: Resultado da consulta
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch == 'all':
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
        elif fetch == 'one':
            row = cursor.fetchone()
            return dict(row) if row else None
        else:  # 'none'
            conn.commit()
            return None

def execute_many(db_name: str, query: str, params_list: list):
    """Executa uma consulta com múltiplos conjuntos de parâmetros.
    
    Args:
        db_name: Nome do banco de dados
        query: Consulta SQL a ser executada
        params_list: Lista de tuplas de parâmetros
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()

def execute_script(db_name: str, script: str):
    """Executa um script SQL no banco de dados especificado.
    
    Args:
        db_name: Nome do banco de dados
        script: Script SQL a ser executado
    """
    with get_connection(db_name) as conn:
        conn.executescript(script)
        conn.commit()

# Funções auxiliares para operações comuns
def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Obtém um usuário pelo ID do Telegram."""
    return execute_query(
        'users',
        'SELECT * FROM users WHERE telegram_id = ?',
        (telegram_id,),
        'one'
    )

def create_user(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> int:
    """Cria um novo usuário."""
    with get_connection('users') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (telegram_id, username, first_name, last_name) VALUES (?, ?, ?, ?)',
            (telegram_id, username, first_name, last_name)
        )
        conn.commit()
        return cursor.lastrowid

def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> Dict[str, Any]:
    """Obtém um usuário existente ou cria um novo se não existir."""
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        user_id = create_user(telegram_id, username, first_name, last_name)
        user = get_user_by_telegram_id(telegram_id)
    return user
