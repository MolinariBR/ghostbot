#!/usr/bin/env python3
"""
Debug do fluxo Lightning: verifica cada etapa e mostra onde pode estar o problema para o bot não pedir o endereço Lightning.
"""
import requests
import json
import time

depix_id = "0197ea6c80bc7dfc81b1e02fe8d06954"
chat_id = "7910260237"

print("\n=== [1] Consultando depósito na API ===")
url_deposit = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
resp = requests.get(url_deposit, timeout=10)
print(f"Status: {resp.status_code}")
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

data = resp.json()
deposito = data.get('deposits', [{}])[0]

blockchainTxID = deposito.get('blockchainTxID')
if not blockchainTxID:
    print("[ERRO] blockchainTxID não encontrado! O fluxo não irá avançar.")
else:
    print(f"blockchainTxID: {blockchainTxID}")

print("\n=== [2] Consultando endpoint robusto (cron) ===")
url_cron = f"https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php?chat_id={chat_id}"
resp_cron = requests.get(url_cron, timeout=10)
print(f"Status: {resp_cron.status_code}")
try:
    print(json.dumps(resp_cron.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Erro JSON: {e}")
    print(f"Resposta bruta: {resp_cron.text}")

print("\n=== [3] Chamando notifier manualmente ===")
url_notifier = f"https://useghost.squareweb.app/api/lightning_notifier.php?chat_id={chat_id}"
resp_notifier = requests.get(url_notifier, timeout=10)
print(f"Status: {resp_notifier.status_code}")
try:
    print(json.dumps(resp_notifier.json(), indent=2, ensure_ascii=False))
except Exception:
    print(resp_notifier.text)

print("\n=== [4] Status final do depósito ===")
resp_final = requests.get(url_deposit, timeout=10)
print(json.dumps(resp_final.json(), indent=2, ensure_ascii=False))

print("\n=== [5] Dicas de debug ===")
print("- O depósito deve ter blockchainTxID preenchido e status 'awaiting_client_invoice'.")
print("- O endpoint cron deve retornar o depósito em 'results'.")
print("- O notifier deve retornar 'success' e 'notified'.")
print("- Se tudo OK, o bot deve exibir a solicitação de endereço Lightning para o chat_id.")
print("- Se não aparecer, verifique logs do bot e se o chat_id está correto.")

print("\n=== [6] Rodando o endpoint cron para disparar o bot ===")
resp_cron_final = requests.get(url_cron, timeout=10)
print(f"Status: {resp_cron_final.status_code}")
try:
    print(json.dumps(resp_cron_final.json(), indent=2, ensure_ascii=False))
except Exception:
    print(resp_cron_final.text)
