# Forçar git a versionar este arquivo
import requests
import sqlite3
from datetime import datetime

COTACAO_DB_PATH = 'data/cotacao.db'

# Mapa de spreads por moeda
SPREAD_MAP = {
    'btc': 1.0,
    'usdt': 1.0,
    'depix': 0.0,
}

# Mapa de IDs do CoinGecko
COINGECKO_ID_MAP = {
    'btc': 'bitcoin',
    'eth': 'ethereum',
    'ltc': 'litecoin',
    'usdt': 'tether',
    'depix': 'depix',  # se existir
}

# Função para buscar o último preço salvo no banco local

def get_last_cotacao(moeda: str) -> dict | None:
    try:
        conn = sqlite3.connect(COTACAO_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT valor, origem, data_atualizacao FROM cotacoes WHERE moeda = ? ORDER BY data_atualizacao DESC LIMIT 1', (moeda,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'valor': row[0], 'origem': row[1], 'data_atualizacao': row[2]}
    except Exception:
        pass
    return None

# Função para buscar preço em tempo real (Binance, CoinGecko, fallback local)
def get_realtime_price(symbol: str, vs: str = 'brl') -> dict:
    symbol = symbol.lower()
    vs = vs.lower()
    # Caso especial para DEPIX
    if symbol == 'depix':
        return {
            'price': 1.0,
            'source': 'fixed',
            'timestamp': datetime.now().isoformat(),
            'symbol': 'depix',
            'vs': vs
        }
    # 1. Binance
    try:
        binance_symbol = symbol.upper() + 'USDT'
        url = f'https://api.binance.com/api/v3/ticker/price?symbol={binance_symbol}'
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            price = float(data['price'])
            spread = SPREAD_MAP.get(symbol, 1.0)
            final_price = price * (1 + spread / 100)
            return {
                'price': round(final_price, 2),
                'source': 'binance',
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'vs': vs,
                'raw_price': price,
                'spread': spread
            }
    except Exception:
        pass
    # 2. CoinGecko
    try:
        coin_id = COINGECKO_ID_MAP.get(symbol, symbol)
        vs_currency = vs if vs in ('brl', 'usd') else 'usd'
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}'
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if coin_id in data and vs_currency in data[coin_id]:
                price = float(data[coin_id][vs_currency])
                return {
                    'price': price,
                    'source': 'coingecko',
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'vs': vs,
                    'coingecko_id': coin_id
                }
    except Exception:
        pass
    # 3. Fallback local
    last = get_last_cotacao(symbol)
    if last:
        return {
            'price': last['valor'],
            'source': 'local_cache',
            'timestamp': last['data_atualizacao'],
            'symbol': symbol,
            'vs': vs,
            'cached': True
        }
    return {
        'error': f'Não foi possível obter cotação para {symbol.upper()}',
        'symbol': symbol,
        'vs': vs,
        'timestamp': datetime.now().isoformat()
    } 
    #teste