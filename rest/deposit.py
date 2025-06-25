import requests
import datetime

BACKEND_URL = "https://ghostp2p.squareweb.app/rest/deposit.php"

def registrar_deposito(
    chatid,
    moeda,
    rede,
    valor,
    cotacao,
    taxa,
    valor_liquido,
    valor_recebido,
    endereco_recebimento,
    metodo_pagamento,
    dados_pagamento,
    data=None
):
    """
    Envia um novo depósito para o backend via REST.
    dados_pagamento deve ser um dict (ex: {'txid': ..., 'qr_code': ..., ...})
    """
    if data is None:
        data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    payload = {
        "chatid": chatid,
        "moeda": moeda,
        "rede": rede,
        "valor": valor,
        "cotacao": cotacao,
        "taxa": taxa,
        "valor_liquido": valor_liquido,
        "valor_recebido": valor_recebido,
        "endereco_recebimento": endereco_recebimento,
        "metodo_pagamento": metodo_pagamento,
        "dados_pagamento": dados_pagamento,
        "data": data
    }
    resp = requests.post(BACKEND_URL, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

# Exemplo de uso:
# resultado = registrar_deposito(123456, 'BTC', 'On-chain', 1000, 350000, 10, 990, 0.0028, 'endereco', 'PIX', {'txid': 'abc', 'qr_code': 'url'}, None)
# print(resultado)
