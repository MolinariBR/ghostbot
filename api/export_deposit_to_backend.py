import sqlite3
import requests
import os

# Caminho do banco de depósitos do bot
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/deposit.db')
# URL do endpoint do backend
BACKEND_URL = 'https://useghost.squareweb.app/api/deposit_receiver.php'

def exportar_depositos():
    conn = sqlite3.connect(DB_PATH)
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

def enviar_para_backend(depositos):
    try:
        resp = requests.post(BACKEND_URL, json=depositos, timeout=10)
        print('Status:', resp.status_code)
        print('Resposta:', resp.text)
    except Exception as e:
        print('Erro ao enviar para backend:', e)

if __name__ == '__main__':
    depositos = exportar_depositos()
    if depositos:
        enviar_para_backend(depositos)
    else:
        print('Nenhum dado de depósito encontrado no banco do bot.')
