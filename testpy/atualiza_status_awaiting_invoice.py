#!/usr/bin/env python3
"""
Atualiza o status do depósito para 'awaiting_client_invoice' para liberar o fluxo Lightning no bot.
"""
import requests
import json

depix_id = "0197ea6c80bc7dfc81b1e02fe8d06954"
chat_id = "7910260237"

# Buscar dados do depósito
url_deposit = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
resp = requests.get(url_deposit, timeout=10)
data = resp.json()
deposito = data.get('deposits', [{}])[0]

if not deposito or not deposito.get('blockchainTxID'):
    print("[ERRO] Depósito não encontrado ou sem blockchainTxID!")
    exit(1)

# Atualizar status via API (ajuste conforme backend)
url_update = "https://useghost.squareweb.app/api/update_transaction.php"
payload = {
    "action": "update",
    "depix_id": depix_id,
    "chatid": chat_id,
    "status": "awaiting_client_invoice"
}

resp_update = requests.post(url_update, json=payload, timeout=10)
print("Status update:", resp_update.status_code)
try:
    print(json.dumps(resp_update.json(), indent=2, ensure_ascii=False))
except Exception:
    print(resp_update.text)

# Confirmar alteração
resp_final = requests.get(url_deposit, timeout=10)
print("\nStatus final do depósito:")
print(json.dumps(resp_final.json(), indent=2, ensure_ascii=False))

print("\nPronto! Agora execute o cron/notifier e o bot deve pedir o endereço Lightning.")
