#!/usr/bin/env python3
import sys
sys.path.append('/home/mau/bot/ghost')
from api.voltz import VoltzAPI

# Teste simples
voltz = VoltzAPI(backend_url='http://localhost:8000')

print("1. Testando registro...")
result = voltz.create_deposit_request(
    chatid='7910260237',
    userid='test_user',
    amount_brl=25.0,
    amount_sats=42000,
    moeda='BTC'
)
print(f"Resultado: {result}")

if result['success']:
    depix_id = result['depix_id']
    print(f"\n2. Testando consulta de status para {depix_id}...")
    status = voltz.check_deposit_status(depix_id)
    print(f"Status: {status}")
