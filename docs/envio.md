# 📤 Voltz API - Sistema de Envio (LNURL-withdraw)

**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** 📋 Documentação Completa  

## 📋 Visão Geral

O sistema de envio da Voltz API permite criar **links de saque LNURL-withdraw** que facilitam o envio de Bitcoin via Lightning Network. Usuários podem sacar fundos através de QR codes ou links, sem precisar gerar invoices manualmente.

### 🎯 **Use Cases**
- **Saques automáticos** do bot Ghost para usuários
- **Links de presente** com Bitcoin
- **Reembolsos** e devoluções
- **Distribuição de fundos** em massa

---

## 🔑 **Autenticação**

A Voltz API usa dois tipos de chaves:

```bash
# Chave Admin (operações CRUD)
X-Api-Key: 8fce34f4b0f8446a990418bd167dc644

# Chave Invoice (consultas)  
X-Api-Key: b2f68df91c8848f6a1db26f2e403321f
```

---

## 📊 **Endpoints Disponíveis**

### 1. 📋 **Listar Links de Saque**
**Consulta todos os links de saque criados**

```http
GET /withdraw/api/v1/links
```

**Headers:**
```json
{
  "X-Api-Key": "b2f68df91c8848f6a1db26f2e403321f"
}
```

**Response:** `200 OK`
```json
[
  {
    "id": "abc123",
    "title": "Saque Ghost Bot",
    "lnurl": "lnurl1dp68gurn8ghj7...",
    "min_withdrawable": 1000,
    "max_withdrawable": 100000,
    "uses": 1,
    "wait_time": 0,
    "is_unique": true,
    "created_at": "2025-01-27T10:00:00Z"
  }
]
```

**Exemplo cURL:**
```bash
curl -X GET https://lnvoltz.com/withdraw/api/v1/links \
  -H "X-Api-Key: b2f68df91c8848f6a1db26f2e403321f"
```

---

### 2. 🔍 **Obter Link Específico**
**Recupera dados de um link de saque específico**

```http
GET /withdraw/api/v1/links/<withdraw_id>
```

**Headers:**
```json
{
  "X-Api-Key": "b2f68df91c8848f6a1db26f2e403321f"
}
```

**Response:** `200 OK`
```json
{
  "lnurl": "lnurl1dp68gurn8ghj7um5v93kketj9ehx2amn9uh8wetvdskkkmn0wahz7mrww4excup0..."
}
```

**Exemplo cURL:**
```bash
curl -X GET https://lnvoltz.com/withdraw/api/v1/links/abc123 \
  -H "X-Api-Key: b2f68df91c8848f6a1db26f2e403321f"
```

---

### 3. ➕ **Criar Link de Saque**
**Cria um novo link LNURL-withdraw para saques**

```http
POST /withdraw/api/v1/links
```

**Headers:**
```json
{
  "X-Api-Key": "8fce34f4b0f8446a990418bd167dc644",
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "title": "Saque Ghost Bot #12345",           // Título identificador
  "min_withdrawable": 1000,                  // Mínimo em msat (1 sat = 1000 msat)
  "max_withdrawable": 100000,                // Máximo em msat 
  "uses": 1,                                 // Quantas vezes pode ser usado
  "wait_time": 0,                            // Tempo de espera entre usos (seg)
  "is_unique": true,                         // Se cada uso gera novo invoice
  "webhook_url": "https://ghostbot.com/webhook" // URL para notificações
}
```

**Response:** `201 CREATED`
```json
{
  "lnurl": "lnurl1dp68gurn8ghj7um5v93kketj9ehx2amn9uh8wetvdskkkmn0wahz7mrww4excup0..."
}
```

**Exemplo cURL:**
```bash
curl -X POST https://lnvoltz.com/withdraw/api/v1/links \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644" \
  -d '{
    "title": "Saque Ghost Bot #12345",
    "min_withdrawable": 10000,
    "max_withdrawable": 1000000,
    "uses": 1,
    "wait_time": 0,
    "is_unique": true,
    "webhook_url": "https://useghost.squareweb.app/webhook"
  }'
```

---

### 4. ✏️ **Atualizar Link de Saque**
**Modifica configurações de um link existente**

```http
PUT /withdraw/api/v1/links/<withdraw_id>
```

**Headers:**
```json
{
  "X-Api-Key": "8fce34f4b0f8446a990418bd167dc644",
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "title": "Saque Atualizado",
  "min_withdrawable": 5000,
  "max_withdrawable": 500000,
  "uses": 3,
  "wait_time": 60,
  "is_unique": false
}
```

**Response:** `200 OK`
```json
{
  "lnurl": "lnurl1dp68gurn8ghj7um5v93kketj9ehx2amn9uh8wetvdskkkmn0wahz7mrww4excup0..."
}
```

**Exemplo cURL:**
```bash
curl -X PUT https://lnvoltz.com/withdraw/api/v1/links/abc123 \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644" \
  -d '{
    "title": "Saque Atualizado",
    "min_withdrawable": 5000,
    "max_withdrawable": 500000,
    "uses": 3,
    "wait_time": 60,
    "is_unique": false
  }'
```

---

### 5. 🗑️ **Deletar Link de Saque**
**Remove um link de saque (não pode ser usado novamente)**

```http
DELETE /withdraw/api/v1/links/<withdraw_id>
```

**Headers:**
```json
{
  "X-Api-Key": "8fce34f4b0f8446a990418bd167dc644"
}
```

**Response:** `204 NO CONTENT`

**Exemplo cURL:**
```bash
curl -X DELETE https://lnvoltz.com/withdraw/api/v1/links/abc123 \
  -H "X-Api-Key: 8fce34f4b0f8446a990418bd167dc644"
```

---

### 6. 🔐 **Verificação Hash (Anti-spam)**
**Verifica hash para prevenir uso excessivo/bots**

```http
GET /withdraw/api/v1/links/<the_hash>/<lnurl_id>
```

**Headers:**
```json
{
  "X-Api-Key": "b2f68df91c8848f6a1db26f2e403321f"
}
```

**Response:** `201 CREATED`
```json
{
  "status": true
}
```

**Exemplo cURL:**
```bash
curl -X GET https://lnvoltz.com/withdraw/api/v1/links/hash123/lnurl456 \
  -H "X-Api-Key: b2f68df91c8848f6a1db26f2e403321f"
```

---

### 7. 🖼️ **Obter QR Code**
**Gera imagem QR Code para o link de saque**

```http
GET /withdraw/img/<lnurl_id>
```

**Response:** Imagem PNG do QR Code

**Exemplo cURL:**
```bash
curl -X GET https://lnvoltz.com/withdraw/img/lnurl456 \
  --output qrcode.png
```

---

## 📋 **Parâmetros Detalhados**

### **Campos do Link de Saque:**

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `title` | string | Nome identificador do link | "Saque Ghost #123" |
| `min_withdrawable` | integer | Valor mínimo em **millisatoshis** | 1000 (= 1 sat) |
| `max_withdrawable` | integer | Valor máximo em **millisatoshis** | 100000 (= 100 sats) |
| `uses` | integer | Quantas vezes pode ser usado | 1 (uso único) |
| `wait_time` | integer | Segundos entre usos | 0 (sem espera) |
| `is_unique` | boolean | Gera novo invoice a cada uso | true |
| `webhook_url` | string | URL para notificações | "https://..." |

### **Conversão de Valores:**
```
1 Satoshi = 1.000 Millisatoshis
1 BTC = 100.000.000 Satoshis = 100.000.000.000 Millisatoshis

Exemplos:
- 10 sats = 10.000 msat
- 0.001 BTC = 100.000 sats = 100.000.000 msat
```

---

## 🔄 **Fluxo de Uso no Ghost Bot**

### **1. Criação de Link (Backend)**
```php
// Criar link de saque para usuário
$voltz_api->createWithdrawLink([
    'title' => "Saque Ghost #{$deposit_id}",
    'min_withdrawable' => $amount_msat,
    'max_withdrawable' => $amount_msat,
    'uses' => 1,
    'is_unique' => true,
    'webhook_url' => 'https://useghost.squareweb.app/voltz_webhook.php'
]);
```

### **2. Envio para Usuário (Bot)**
```python
# Enviar LNURL para usuário via Telegram
message = f"""
⚡ Seu saque está pronto!

💰 Valor: {amount_sats} sats
🔗 LNURL: {lnurl}

📱 Escaneie o QR code com sua carteira Lightning
"""
await bot.send_photo(chat_id, qr_image, caption=message)
```

### **3. Processamento (Usuário)**
1. Usuário escaneia QR code na carteira
2. Carteira decodifica LNURL-withdraw
3. Carteira gera invoice BOLT11
4. Voltz paga o invoice automaticamente
5. Webhook notifica conclusão

---

## ⚠️ **Limitações e Considerações**

### **Segurança:**
- ✅ Links únicos (`is_unique: true`) são mais seguros
- ⚠️ Links reutilizáveis podem ser interceptados
- 🔒 Use `wait_time` para prevenir spam

### **Valores:**
- 💰 Valores em **millisatoshis** (não satoshis)
- 📏 Min/Max devem ser válidos conforme rede Lightning
- ⚡ Considere taxas da rede

### **Monitoramento:**
- 📊 Configure webhooks para tracking
- 🔔 Monitore status dos saques
- 📝 Logs para auditoria

---

## 🔗 **Referências**

- **LNURL Spec:** https://github.com/fiatjaf/lnurl-rfc
- **LUD-03:** LNURL-withdraw specification
- **Voltz API:** https://lnvoltz.com/api/docs
- **Ghost Bot Integration:** `/ghostbackend/voltz/`

---

## 📝 **Changelog**

- **2025-01-27:** Documentação inicial criada
- **2025-01-27:** Estrutura e exemplos adicionados

