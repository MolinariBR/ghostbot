import requests
import datetime

BACKEND_URL = "https://useghost.squareweb.app/rest/deposit.php"

def registrar_deposito(
    chatid,
    moeda,
    rede,
    valor_brl,
    taxa,
    address,
    forma_pagamento,
    send,
    blockchainTxID=None,
    depix_id=None,
    status=None,
    created_at=None
):
    """
    Envia um novo depósito para o backend via REST, compatível com a tabela deposit.
    - valor_brl: valor em reais (float ou int)
    - taxa: valor da taxa (float)
    - send: valor em cripto a ser enviado (float)
    - address: endereço de recebimento
    - forma_pagamento: ex: 'PIX', 'TED', etc
    - blockchainTxID, depix_id, status, created_at: opcionais
    """
    payload = {
        "chatid": chatid,
        "amount_in_cents": int(round(valor_brl * 100)),
        "taxa": float(taxa),
        "moeda": moeda,
        "rede": rede,
        "address": address,
        "forma_pagamento": forma_pagamento,
        "send": float(send)
    }
    if blockchainTxID:
        payload["blockchainTxID"] = blockchainTxID
    if depix_id:
        payload["depix_id"] = depix_id
    if status:
        payload["status"] = status
    if created_at:
        payload["created_at"] = created_at
    resp = requests.post(BACKEND_URL, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

# Exemplo de uso:
# resultado = registrar_deposito(123456, 'BTC', 'On-chain', 1000, 10, 'endereco', 'PIX', 0.0028)
# print(resultado)
