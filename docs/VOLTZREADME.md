# Voltz API - Documentação Completa

## 🔧 Configuração
- **Base URL:** `https://lnvoltz.com`
- **API Key:** `8fce34f4b0f8446a990418bd167dc644`
- **Carteira ID:** `f3c366b7fb6f43fa9467c4dccedaf824`

## 📝 Endpoints Disponíveis

### 1. 🏦 GET /api/v1/wallet
**Consulta informações da carteira**

**Headers:**
```json
{"X-Api-Key": "8fce34f4b0f8446a990418bd167dc644"}
```

**Returns:** 200 OK (application/json)
```json
{
  "id": "f3c366b7fb6f43fa9467c4dccedaf824",
  "name": "Voltz Wallet", 
  "balance": 0
}
```

**Curl Example:**
```bash
curl https://lnvoltz.com/api/v1/wallet -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644"
```

### 2. 💰 POST /api/v1/payments (Criar Invoice)
**Cria um novo invoice para recebimento**

**Headers:**
```json
{"X-Api-Key": "8fce34f4b0f8446a990418bd167dc644", "Content-Type": "application/json"}
```

**Body (application/json):**
```json
{
  "out": false,
  "amount": 1000,
  "memo": "Descrição do pagamento",
  "expiry": 3600,
  "unit": "sat",
  "webhook": "https://seusite.com/webhook.php",
  "internal": false
}
```

**Returns:** 201 CREATED (application/json)
```json
{
  "checking_id": "1084e2172c87ba74876da6bc5afef186d65b0be101d8ec4c992b15ffaa169544",
  "payment_hash": "1084e2172c87ba74876da6bc5afef186d65b0be101d8ec4c992b15ffaa169544",
  "wallet_id": "f3c366b7fb6f43fa9467c4dccedaf824",
  "amount": 1000000,
  "fee": 0,
  "bolt11": "lnbc10u1p5xhhsgpp5zzzwy9evs7a8fpmd56794lh3smt9kzlpq8vwcnye9v2ll2skj4zqdqc23jhxar9yprksmmnwssyymm5cqzpgxqrrssrzjqdrhkruk080xpvagqw68998r0dxpfgur2e90mmvhxy2px33r6tkgyrvt3sqqgpgqqyqqqqlgqqqqqqgq2qsp5hvt0v0yrr80dnyf62a7gfg7fhqpp5ner9purs587ehtnymy8xmps9qxpqysgqp9r3tffmqf4m6d0kjpxf7r7a7gnpls7vazuhhaev9h2qaha8ed6kfdklqk2z4c55ky5rqza9xvnuxnv2xng2vzsymq8hx34cw3870ycpav5x0d",
  "status": "pending",
  "memo": "Descrição do pagamento",
  "expiry": "2025-07-07T15:47:36",
  "webhook": "https://seusite.com/webhook.php",
  "webhook_status": null,
  "preimage": "fda3f947bbfbd41ceb02654010b20e74a61549ad0654d5d7124064fecab4afa1",
  "tag": null,
  "extension": null,
  "time": "2025-07-07T14:47:36.469493+00:00",
  "created_at": "2025-07-07T14:47:36.469499+00:00",
  "updated_at": "2025-07-07T14:47:36.469501+00:00",
  "extra": {
    "wallet_fiat_currency": "BRL",
    "wallet_fiat_amount": 5.912,
    "wallet_fiat_rate": 169.13421440092102,
    "wallet_btc_rate": 591246.4273074688
  }
}
```

**Curl Example:**
```bash
curl -X POST https://lnvoltz.com/api/v1/payments \
  -d '{"out": false, "amount": 1000, "memo": "Teste Ghost Bot", "expiry": 3600, "unit": "sat"}' \
  -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644" \
  -H "Content-type: application/json"
```

### 3. 💸 POST /api/v1/payments (Pagar Invoice)
**Paga um invoice existente**

**Headers:**
```json
{"X-Api-Key": "8fce34f4b0f8446a990418bd167dc644", "Content-Type": "application/json"}
```

**Body (application/json):**
```json
{"out": true, "bolt11": "<bolt11_string>"}
```

**Returns:** 201 CREATED (application/json)
```json
{"payment_hash": "<string>"}
```

**Curl Example:**
```bash
curl -X POST https://lnvoltz.com/api/v1/payments \
  -d '{"out": true, "bolt11": "lnbc10u1p5xhhsgpp5..."}' \
  -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644" \
  -H "Content-type: application/json"
```

### 4. 🔍 GET /api/v1/payments/<payment_hash>
**Consulta status de um pagamento**

**Headers:**
```json
{"X-Api-Key": "8fce34f4b0f8446a990418bd167dc644"}
```

**Returns:** 200 OK (application/json)
```json
{
  "paid": false,
  "status": "pending",
  "preimage": "fda3f947bbfbd41ceb02654010b20e74a61549ad0654d5d7124064fecab4afa1",
  "details": {
    "checking_id": "1084e2172c87ba74876da6bc5afef186d65b0be101d8ec4c992b15ffaa169544",
    "payment_hash": "1084e2172c87ba74876da6bc5afef186d65b0be101d8ec4c992b15ffaa169544",
    "wallet_id": "f3c366b7fb6f43fa9467c4dccedaf824",
    "amount": 1000000,
    "fee": 0,
    "bolt11": "lnbc10u1p5xhhsgpp5...",
    "status": "pending",
    "memo": "Teste Ghost Bot",
    "expiry": "2025-07-07T15:47:36",
    "webhook": "https://seusite.com/webhook.php",
    "webhook_status": null,
    "preimage": "fda3f947bbfbd41ceb02654010b20e74a61549ad0654d5d7124064fecab4afa1",
    "extra": {
      "wallet_fiat_currency": "BRL",
      "wallet_fiat_amount": 5.912,
      "wallet_fiat_rate": 169.13421440092102,
      "wallet_btc_rate": 591246.4273074688
    }
  }
}
```

**Curl Example:**
```bash
curl -X GET https://lnvoltz.com/api/v1/payments/1084e2172c87ba74876da6bc5afef186d65b0be101d8ec4c992b15ffaa169544 \
  -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644" \
  -H "Content-type: application/json"
```

### 5. 🔧 POST /api/v1/payments/decode
**Decodifica um BOLT11 ou LNURL**

**Body (application/json):**
```json
{"data": "<bolt11_or_lnurl_string>"}
```

**Returns:** 200 OK (application/json)

**Curl Example:**
```bash
curl -X POST https://lnvoltz.com/api/v1/payments/decode \
  -d '{"data": "lnbc10u1p5xhhsgpp5..."}' \
  -H "Content-type: application/json"
```

### 6. 🔗 WS /api/v1/ws/<invoice_key>
**WebSocket para monitoramento em tempo real**

**WebSocket Example:**
```bash
wscat -c ws://lnvoltz.com/api/v1/ws/8fce34f4b0f8446a990418bd167dc644
```

**Returns:** (application/json)
```json
{"balance": 0, "payment": {}}
```

## 📊 Status de Pagamentos
- `pending` - Aguardando pagamento
- `paid` - Pagamento confirmado
- `expired` - Invoice expirado
- `cancelled` - Pagamento cancelado

## 💡 Exemplos de Uso

### Criar Invoice de 1000 sats:
```php
$payload = [
    'out' => false,
    'amount' => 1000,
    'memo' => 'Pagamento Ghost Bot',
    'expiry' => 3600,
    'unit' => 'sat'
];
```

### Verificar se foi pago:
```php
$status = GET /api/v1/payments/{payment_hash}
if ($status['paid'] === true) {
    // Pagamento confirmado!
}
```

## ⚡ URLs Lightning para Carteiras Móveis
Para facilitar o pagamento em carteiras móveis, use o prefixo `lightning:`:
```
lightning:lnbc10u1p5xhhsgpp5zzzwy9evs7a8fpmd56794lh3smt9...
```

## 🔗 QR Codes
Gere QR Codes usando:
- API online: `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=<bolt11>`
- Biblioteca local: Endroid QR Code (PHP)

---
**Última atualização:** 7 de julho de 2025  
**Testado e funcionando:** ✅ Todos os endpoints validados