import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/limites.db')

LIMITES_ESCADA = [500.0, 850.0, 1000.0, 1500.0, 2000.0, 2500.0, 3000.0, 3500.0, 4000.0, 4999.99]
LIMITE_MAXIMO = 4999.99
LIMITE_ATENDENTE = 5000.0

# Inicializa banco de dados

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS limites (
        chatid TEXT,
        data TEXT,
        compras INTEGER,
        valor_total REAL
    )''')
    conn.commit()
    conn.close()

init_db()

# Função para obter limite do usuário

def get_limite(chatid: str) -> float:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hoje = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT compras FROM limites WHERE chatid=? AND data=?', (chatid, hoje))
    row = c.fetchone()
    compras = row[0] if row else 0
    limite = LIMITES_ESCADA[min(compras, len(LIMITES_ESCADA)-1)]
    conn.close()
    return limite

# Função para registrar compra

def registrar_compra(chatid: str, valor: float):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hoje = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT compras, valor_total FROM limites WHERE chatid=? AND data=?', (chatid, hoje))
    row = c.fetchone()
    if row:
        compras, valor_total = row
        compras += 1
        valor_total += valor
        c.execute('UPDATE limites SET compras=?, valor_total=? WHERE chatid=? AND data=?', (compras, valor_total, chatid, hoje))
    else:
        compras = 1
        valor_total = valor
        c.execute('INSERT INTO limites (chatid, data, compras, valor_total) VALUES (?, ?, ?, ?)', (chatid, hoje, compras, valor_total))
    conn.commit()
    conn.close()
    return compras, valor_total

# Função para verificar se precisa de CPF

def precisa_cpf(chatid: str, valor: float) -> bool:
    limite = get_limite(chatid)
    return valor > limite

# Função para verificar se precisa falar com atendente

def precisa_atendente(valor: float) -> bool:
    return valor >= LIMITE_ATENDENTE

# Mensagens
MENSAGEM_CPF = "Compras acima do limite diário, você precisa fornecer seu CPF."
MENSAGEM_ATENDENTE = "Para compras acima de R$5.000,00 fale com o atendente: @GhosttP2P"

# Exemplo de uso
if __name__ == "__main__":
    chatid = "123456"
    for valor in [400, 600, 900, 1200, 5000, 6000]:
        limite = get_limite(chatid)
        print(f"Limite atual: R${limite:.2f}")
        if precisa_atendente(valor):
            print(MENSAGEM_ATENDENTE)
        elif precisa_cpf(chatid, valor):
            print(MENSAGEM_CPF)
        else:
            print(f"Compra permitida: R${valor:.2f}")
        registrar_compra(chatid, valor)
