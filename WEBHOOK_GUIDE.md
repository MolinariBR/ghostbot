# 🚀 Guia de Implementação do Webhook para Container do Bot

## 📋 Resumo
Este guia explica como substituir o **polling** por **webhook** no container do bot para reduzir a sobrecarga do servidor.

## 🏗️ Arquitetura Atual
```
┌─────────────────────┐    ┌─────────────────────┐
│   Backend PHP       │    │   Bot Python        │
│ (useghost.squareweb)│    │   (Container)       │
│                     │    │                     │
│ - Processa dados    │    │ - Polling ❌        │
│ - API endpoints     │    │ - Webhook ✅        │
│ - Login/Profile     │    │ - Mensagens bot     │
└─────────────────────┘    └─────────────────────┘
```

## 📁 Arquivos Criados
- `webhook_teste.py` - Servidor webhook standalone
- `bot_webhook.py` - Bot principal com webhook integrado
- `tokens.py` - Configuração corrigida para produção

## 🔧 Configuração

### 1. Variáveis de Ambiente no Container do Bot
```bash
# Token do bot (já configurado em tokens.py)
TELEGRAM_BOT_TOKEN=7105509014:AAENhZArthrysOBoEmdA6vaxE72pobliahI

# Secret do webhook (segurança)
WEBHOOK_SECRET=ghost_webhook_secret_2025

# URL pública do container do bot (configurar na produção)
WEBHOOK_PUBLIC_URL=https://seu-container-bot.com

# Porta do webhook (padrão: 8080)
PORT=8080
```

### 2. Endpoints do Webhook
```
POST /webhook/{secret}     - Recebe updates do Telegram
GET  /health              - Status do webhook
POST /set_webhook         - Configura webhook no Telegram
POST /remove_webhook      - Remove webhook (volta polling)
GET  /webhook_info        - Info do webhook atual
```

## 🚀 Como Usar

### Opção 1: Webhook Standalone (Teste)
```bash
# No container do bot
python webhook_teste.py
```

### Opção 2: Bot Principal com Webhook
```bash
# No container do bot
python bot_webhook.py
```

## 📡 Configuração do Webhook no Telegram

### 1. Manual via API
```bash
curl -X POST "https://api.telegram.org/bot{BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://seu-container-bot.com/webhook/ghost_webhook_secret_2025",
    "drop_pending_updates": true,
    "max_connections": 40,
    "allowed_updates": ["message", "callback_query"]
  }'
```

### 2. Via Endpoint do Webhook
```bash
# Configurar webhook
curl -X POST http://seu-container-bot.com/set_webhook

# Verificar status
curl -X GET http://seu-container-bot.com/webhook_info

# Remover webhook
curl -X POST http://seu-container-bot.com/remove_webhook
```

## 🔄 Processo de Migração

### Passo 1: Parar o Bot com Polling
```bash
# Parar o bot atual
pkill -f bot.py
```

### Passo 2: Iniciar Webhook
```bash
# Iniciar webhook
python webhook_teste.py
# ou
python bot_webhook.py
```

### Passo 3: Configurar Webhook no Telegram
```bash
# Via endpoint
curl -X POST http://localhost:8080/set_webhook
```

### Passo 4: Testar
```bash
# Verificar status
curl -X GET http://localhost:8080/health

# Enviar mensagem para o bot no Telegram
# Verificar logs do webhook
```

## 🛠️ Deployment no Container

### 1. Dockerfile (exemplo)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Usar webhook ao invés de polling
CMD ["python", "webhook_teste.py"]
```

### 2. SquareCloud Config
```yaml
# squarecloud.app
name: ghost-bot-webhook
version: 1.0.0
main: webhook_teste.py
memory: 512
```

## 📊 Vantagens do Webhook

### ✅ Benefícios
- **Menos CPU**: Sem polling constante
- **Menos memória**: Não mantém conexões ativas
- **Menor latência**: Resposta imediata
- **Maior escalabilidade**: Suporta mais usuários
- **Menor custo**: Reduz uso de recursos

### ❌ Desvantagens
- **Requer URL pública**: Container precisa ser acessível
- **Mais complexo**: Configuração adicional
- **Dependente de rede**: Falhas na rede afetam webhook

## 🔍 Monitoramento

### Logs do Webhook
```bash
# Verificar logs
tail -f logs/bot.log

# Status do webhook
curl -X GET http://localhost:8080/health
```

### Métricas do Telegram
```bash
# Informações do webhook
curl -X GET http://localhost:8080/webhook_info
```

## 🚨 Troubleshooting

### Problema: Webhook não recebe mensagens
```bash
# Verificar configuração
curl -X GET http://localhost:8080/webhook_info

# Reconfigurar webhook
curl -X POST http://localhost:8080/set_webhook
```

### Problema: Erro 403 Forbidden
- Verificar WEBHOOK_SECRET
- Confirmar URL correta

### Problema: Erro 400 Bad Request
- Verificar formato JSON
- Confirmar processamento de updates

## 🎯 Próximos Passos

1. **Testar localmente** com `webhook_teste.py`
2. **Configurar URL pública** do container
3. **Fazer deploy** com webhook
4. **Monitorar performance**
5. **Otimizar** conforme necessário

## 📝 Notas Importantes

- O **backend PHP** continua independente
- O **webhook** substitui apenas o polling
- **Mensagens são processadas** da mesma forma
- **Configuração é reversível** (pode voltar para polling)

## 🔗 URLs Importantes

- **Backend PHP**: https://useghost.squareweb.app
- **Container Bot**: https://seu-container-bot.com
- **Webhook Endpoint**: https://seu-container-bot.com/webhook/ghost_webhook_secret_2025
