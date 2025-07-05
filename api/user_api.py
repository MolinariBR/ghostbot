import requests

BACKEND_URL = "https://ghostp2p.squareweb.app/api/user_api.php"

def enviar_usuario_backend(user_id, username=None, first_name=None, last_name=None, cpf=None, num_compras=None, limite=None):
    payload = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
    }
    if cpf is not None:
        payload["cpf"] = cpf
    if num_compras is not None:
        payload["num_compras"] = num_compras
    if limite is not None:
        payload["limite"] = limite
    headers = {"Content-Type": "application/json"}
    response = requests.post(BACKEND_URL, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def consultar_usuario_backend(user_id):
    params = {"user_id": user_id}
    response = requests.get(BACKEND_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
