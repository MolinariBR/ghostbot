# API Unificada de Depósitos

Utilize apenas o endpoint REST:

- **Registro de depósito (POST):**
  - `POST /rest/deposit.php`
  - Aceita JSON com os campos: chatid, moeda, rede, amount_in_cents, taxa, address, forma_pagamento, send, blockchainTxID (opcional), depix_id (opcional), status (opcional), created_at (opcional)

- **Consulta de depósitos (GET):**
  - `GET /rest/deposit.php`
  - Parâmetro opcional: `chatid`

Exemplo de payload para registro:
```json
{
  "chatid": "123456",
  "moeda": "BTC",
  "rede": "On-chain",
  "amount_in_cents": 10000,
  "taxa": 0.01,
  "address": "endereco_btc",
  "forma_pagamento": "PIX",
  "send": 0.0028
}
```

Todos os clientes/bots/scripts devem usar este endpoint.
