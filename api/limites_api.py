from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/limites.db')

@app.route('/api/limites')
def get_limites():
    try:
        conn = sqlite3.connect(DB_PATH)
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
        return jsonify(limites)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
