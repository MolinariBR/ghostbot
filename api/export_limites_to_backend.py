import sqlite3
import requests
import os

# Caminhos dos bancos do bot
LIM_DB_PATH = os.path.join(os.path.dirname(__file__), '../data/limites.db')
DEP_DB_PATH = os.path.join(os.path.dirname(__file__), '../data/deposit.db')
# URLs dos endpoints do backend
LIM_BACKEND_URL = 'https://useghost.squareweb.app/api/limites_receiver.php'
DEP_BACKEND_URL = 'https://useghost.squareweb.app/api/deposit_receiver.php'

def exportar_limites():
    conn = sqlite3.connect(LIM_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, moeda, minimo, maximo, comissao, taxa_parceiro FROM limites')
    rows = cursor.fetchall()
    conn.close()
    limites = [
        {
            'id': row[0],
            'moeda': row[1],
            'minimo': row[2],
            'maximo': row[3],
            'comissao': row[4],
            'taxa_parceiro': row[5]
        }
        for row in rows
    ]
    return limites

def exportar_depositos():
    conn = sqlite3.connect(DEP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, chatid, amount_in_cents, status, created_at FROM deposit')
    rows = cursor.fetchall()
    conn.close()
    depositos = [
        {
            'id': row[0],
            'chatid': row[1],
            'amount_in_cents': row[2],
            'status': row[3],
            'created_at': row[4]
        }
        for row in rows
    ]
    return depositos

def enviar_para_backend(url, dados, tipo):
    try:
        resp = requests.post(url, json=dados, timeout=10)
        print(f'[{tipo}] Status:', resp.status_code)
        print(f'[{tipo}] Resposta:', resp.text)
    except Exception as e:
        print(f'[{tipo}] Erro ao enviar para backend:', e)

if __name__ == '__main__':
    limites = exportar_limites()
    depositos = exportar_depositos()
    if limites:
        enviar_para_backend(LIM_BACKEND_URL, limites, 'Limites')
    else:
        print('Nenhum dado de limites encontrado no banco do bot.')
    if depositos:
        enviar_para_backend(DEP_BACKEND_URL, depositos, 'Depositos')
    else:
        print('Nenhum dado de depósito encontrado no banco do bot.')
