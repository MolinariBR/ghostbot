import time
import requests

# Mapa para armazenar última cotação bem-sucedida e timestamp
COTACAO_MAPA = {
    "BITCOIN": {"valor": None, "timestamp": 0},
    "USDT": {"valor": None, "timestamp": 0},
    "DEPIX": {"valor": 1.0, "timestamp": 0}  # Stablecoin BRL
}

# Limite de consultas por minuto
CONSULTA_INTERVALO = 20  # segundos (3 por minuto)

# Funções de consulta

def consultar_binance(moeda: str) -> float:
    if moeda == "BITCOIN":
        symbol = "BTCBRL"
    elif moeda == "USDT":
        symbol = "USDTBRL"
    else:
        return 1.0
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return float(data["price"])
    except Exception:
        return None

def consultar_coingecko(moeda: str) -> float:
    if moeda == "BITCOIN":
        id = "bitcoin"
    elif moeda == "USDT":
        id = "tether"
    else:
        return 1.0
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=brl"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return float(data[id]["brl"])
    except Exception:
        return None

def consultar_bitfinex(moeda: str) -> float:
    if moeda == "BITCOIN":
        symbol = "tBTCBRL"
    elif moeda == "USDT":
        symbol = "tUSTBRL"
    else:
        return 1.0
    url = f"https://api-pub.bitfinex.com/v2/ticker/{symbol}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return float(data[6])  # preço último
    except Exception:
        return None

def get_cotacao(moeda: str, trigger: bool = True) -> float:
    """
    Consulta cotação da moeda escolhida, usando gatilho inteligente.
    Consulta Binance, Coingecko, Bitfinex. Se todas falharem, retorna último valor.
    """
    moeda_key = moeda.upper()
    if "BTC" in moeda_key:
        moeda_key = "BITCOIN"
    if moeda_key == "DEPIX":
        return 1.0
    agora = time.time()
    ultima = COTACAO_MAPA.get(moeda_key, {"valor": None, "timestamp": 0})
    # Sistema de gatilho: só consulta se passou o intervalo
    if trigger and (agora - ultima["timestamp"] < CONSULTA_INTERVALO) and ultima["valor"]:
        return ultima["valor"]
    # Consulta em ordem
    for consulta in [consultar_binance, consultar_coingecko, consultar_bitfinex]:
        valor = consulta(moeda_key)
        if valor:
            COTACAO_MAPA[moeda_key]["valor"] = valor
            COTACAO_MAPA[moeda_key]["timestamp"] = agora
            return valor
    # Se todas falharem, retorna último valor
    if ultima["valor"]:
        return ultima["valor"]
    raise Exception(f"Não foi possível obter cotação para {moeda_key}")

# Exemplo de uso:
if __name__ == "__main__":
    for moeda in ["Bitcoin", "USDT", "DEPIX"]:
        try:
            valor = get_cotacao(moeda)
            print(f"Cotação {moeda}: R${valor:.2f}")
        except Exception as e:
            print(f"Erro ao consultar {moeda}: {e}")
