#!/usr/bin/env python3
"""
Setup inicial do simulador
Configura ambiente e dependências
"""

import os
import sys
import sqlite3

def criar_banco_teste():
    """Cria banco de dados de teste local se não existir"""
    db_path = "/home/mau/bot/ghostbackend/data/deposit.db"
    
    if not os.path.exists(db_path):
        print(f"📁 Criando banco de dados em: {db_path}")
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Criar banco com schema básico
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deposit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                depix_id TEXT UNIQUE NOT NULL,
                chatid TEXT NOT NULL,
                amount_in_cents INTEGER NOT NULL,
                taxa REAL DEFAULT 0.05,
                moeda TEXT DEFAULT 'BTC',
                rede TEXT DEFAULT 'lightning',
                address TEXT DEFAULT '',
                forma_pagamento TEXT DEFAULT 'PIX',
                send INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                blockchainTxID TEXT DEFAULT '',
                comprovante TEXT DEFAULT '',
                user_id TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                lightning_status TEXT DEFAULT NULL,
                notified INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados criado com sucesso!")
    else:
        print("✅ Banco de dados já existe")

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    dependencias = ['requests', 'sqlite3']
    
    print("🔍 Verificando dependências...")
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - FALTANDO")
            return False
    
    return True

def criar_diretorio_logs():
    """Cria diretório para logs"""
    log_dir = "/home/mau/bot/ghost/simulador/logs"
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"📁 Diretório de logs criado: {log_dir}")
    else:
        print("✅ Diretório de logs já existe")

def main():
    """Setup principal"""
    print("🔧 Setup do Simulador Bot Lightning")
    print("="*40)
    
    # 1. Verificar dependências
    if not verificar_dependencias():
        print("❌ Dependências faltando. Execute: pip install requests")
        return 1
    
    # 2. Criar banco de teste
    try:
        criar_banco_teste()
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
        return 1
    
    # 3. Criar diretório de logs
    try:
        criar_diretorio_logs()
    except Exception as e:
        print(f"❌ Erro ao criar diretório de logs: {e}")
        return 1
    
    print("\n✅ Setup concluído com sucesso!")
    print("\n🚀 Para executar o simulador:")
    print("  python3 bot_simulator.py [valor_reais] [chat_id]")
    print("\n🧪 Para testar apenas o cron:")
    print("  python3 cron_tester.py [chat_id]")
    
    return 0

if __name__ == "__main__":
    exit(main())
