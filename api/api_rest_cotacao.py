import requests
from config.config import BASE_URL

def get_cotacao_rest(moeda: str, vs: str = "brl", valor: float = 0.0, chatid: str = None, compras: int = 0, metodo: str = "pix") -> dict:
    params = {
        "moeda": moeda,
        "vs": vs,
        "valor": valor,
        "chatid": chatid or "",
        "compras": compras,
        "metodo": metodo
    }
    url = f"{BASE_URL}/api/api_cotacao.php"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Exemplo de uso
if __name__ == "__main__":
    print(get_cotacao_rest("bitcoin", valor=1000, chatid="12345", compras=2, metodo="pix"))
    print(get_cotacao_rest("usdt", valor=500, chatid="12345", compras=0, metodo="pix"))
    print(get_cotacao_rest("depix", valor=50, chatid="12345", compras=1, metodo="pix"))
