# 🚀 Configuração de Webhook para Diferentes Serviços

## 📋 Como funciona
O bot roda em um **container** que é deployado em um serviço de hospedagem. Esse serviço fornece uma **URL pública automática** que usamos para o webhook.

## 🌐 Serviços Suportados

### 1. Railway
```bash
# Variável automática do Railway
RAILWAY_STATIC_URL=your-app-name.railway.app

# Webhook será configurado automaticamente como:
# https://your-app-name.railway.app/webhook/ghost_webhook_secret_2025
```

### 2. Heroku
```bash
# Variável automática do Heroku
HEROKU_APP_NAME=your-app-name

# Webhook será configurado automaticamente como:
# https://your-app-name.herokuapp.com/webhook/ghost_webhook_secret_2025
```

### 3. Render
```bash
# Variável automática do Render
RENDER_EXTERNAL_URL=https://your-app-name.onrender.com

# Webhook será configurado automaticamente como:
# https://your-app-name.onrender.com/webhook/ghost_webhook_secret_2025
```

### 4. Manual (qualquer serviço)
```bash
# Configure manualmente para qualquer serviço
export WEBHOOK_PUBLIC_URL=https://sua-url-do-servico.com

# Webhook será configurado como:
# https://sua-url-do-servico.com/webhook/ghost_webhook_secret_2025
```

## 🛠️ Configuração no Serviço

### Railway (Recomendado)
```dockerfile
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python webhook_teste.py"
```

### Heroku
```json
// Procfile
web: python webhook_teste.py
```

### SquareCloud
```yaml
# squarecloud.app
name: ghost-bot
version: 1.0.0
main: webhook_teste.py
memory: 512
```

## 🧪 Teste Local com ngrok

### 1. Instalar ngrok
```bash
# Download ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

### 2. Configurar túnel
```bash
# Em um terminal
ngrok http 8080

# Em outro terminal
cd /home/mau/bot/ghost
source .venv/bin/activate
export WEBHOOK_PUBLIC_URL=https://abc123.ngrok.io
python webhook_teste.py
```

### 3. Configurar webhook
```bash
# Configurar webhook no Telegram
curl -X POST http://localhost:8080/set_webhook

# Testar enviando mensagem para o bot
```

## 🔧 Variáveis de Ambiente

### Obrigatórias
```bash
TELEGRAM_BOT_TOKEN=7105509014:AAENhZArthrysOBoEmdA6vaxE72pobliahI
```

### Opcionais
```bash
WEBHOOK_SECRET=ghost_webhook_secret_2025  # Padrão já configurado
PORT=8080                                 # Padrão já configurado
WEBHOOK_HOST=0.0.0.0                     # Padrão já configurado
```

### Automáticas (detectadas pelo serviço)
```bash
RAILWAY_STATIC_URL=...      # Railway
HEROKU_APP_NAME=...         # Heroku
RENDER_EXTERNAL_URL=...     # Render
```

## 🚀 Deploy do Webhook

### 1. Fazer commit
```bash
git add .
git commit -m "Configuração webhook para produção"
git push origin main
```

### 2. Deploy no serviço
- **Railway**: Conecta automaticamente ao GitHub
- **Heroku**: `git push heroku main`
- **Render**: Conecta automaticamente ao GitHub

### 3. Configurar webhook
```bash
# Aguardar deploy e acessar:
curl -X POST https://sua-url-do-servico.com/set_webhook
```

## 📊 Monitoramento

### Verificar status
```bash
curl https://sua-url-do-servico.com/health
```

### Verificar webhook do Telegram
```bash
curl https://sua-url-do-servico.com/webhook_info
```

### Logs do container
```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Render
# Logs disponíveis no dashboard
```

## 🔄 Migração de Polling para Webhook

### Antes (Polling)
```python
# bot.py usa polling
await updater.start_polling(...)
```

### Depois (Webhook)
```python
# webhook_teste.py recebe updates
python webhook_teste.py
```

### Configuração no Telegram
```bash
# Configurar webhook
curl -X POST https://sua-url.com/set_webhook

# Para voltar ao polling (se necessário)
curl -X POST https://sua-url.com/remove_webhook
```

## 💡 Dicas

1. **URL sempre com HTTPS** - Telegram exige SSL
2. **Porta padrão 8080** - Funciona na maioria dos serviços
3. **Secret para segurança** - Evita requisições maliciosas
4. **Logs para debug** - Acompanhe o processamento
5. **Health check** - Monitore a saúde do webhook

## 🚨 Troubleshooting

### Webhook não funciona
```bash
# Verificar URL pública
curl https://sua-url.com/health

# Verificar configuração no Telegram
curl https://sua-url.com/webhook_info

# Reconfigurar webhook
curl -X POST https://sua-url.com/set_webhook
```

### URL não detectada
```bash
# Configurar manualmente
export WEBHOOK_PUBLIC_URL=https://sua-url.com
```

### Erro SSL
- Verificar se URL usa HTTPS
- Certificado válido é obrigatório
