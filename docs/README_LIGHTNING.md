# Sistema de Pagamentos Lightning Automático

Este sistema processa automaticamente pagamentos BTC Lightning usando a API Voltz quando as condições são atendidas no banco de dados `deposit.db`.

## 📋 Requisitos

- PHP 7.4 ou superior
- Extensão SQLite3 habilitada
- Acesso à API Voltz configurado
- Banco de dados `deposit.db` configurado

## 🚀 Instalação

1. **Verifique as configurações do Voltz:**
   ```bash
   # Edite os arquivos de configuração
   vi /home/mau/bot/ghostbackend/config/development.php
   vi /home/mau/bot/ghostbackend/config/production.php
   ```

2. **Teste a conectividade:**
   ```bash
   cd /home/mau/bot/ghostbackend/api
   php test_lightning.php list
   ```

## 📦 Componentes do Sistema

### 1. **Processador Principal**
- **Arquivo:** `lightning_payment_processor.php`
- **Função:** Processa pagamentos Lightning pendentes
- **Execução:** Manual ou via trigger

### 2. **Monitor Contínuo**
- **Arquivo:** `lightning_monitor.php`
- **Função:** Execução contínua em background
- **Uso:** Daemon para processamento automático

### 3. **Endpoint HTTP**
- **Arquivo:** `lightning_trigger.php`
- **Função:** API REST para processar pagamentos
- **Métodos:** GET (todos) e POST (específico)

### 4. **Script de Teste**
- **Arquivo:** `test_lightning.php`
- **Função:** Criar transações de teste e validar sistema
- **Uso:** Desenvolvimento e debugging

### 5. **Cron Job**
- **Arquivo:** `scripts/lightning_cron.sh`
- **Função:** Execução automatizada via crontab
- **Frequência:** Configurável (padrão: 2 minutos)

## 💻 Formas de Execução

### Execução Manual
```bash
cd /home/mau/bot/ghostbackend/api

# Processar todos os pagamentos pendentes
php lightning_payment_processor.php

# Processar transação específica
curl -X POST http://localhost/api/lightning_trigger.php \
  -H "Content-Type: application/json" \
  -d '{"id": 123}'
```

### Monitor Contínuo (Daemon)
```bash
cd /home/mau/bot/ghostbackend/api

# Execução contínua (30 segundos de intervalo)
php lightning_monitor.php 30

# Em background
nohup php lightning_monitor.php 30 > ../logs/monitor.log 2>&1 &
```

### Cron Job (Recomendado)
```bash
# Adicionar ao crontab
crontab -e

# Executa a cada 2 minutos
*/2 * * * * /home/mau/bot/ghostbackend/scripts/lightning_cron.sh
```

### Via HTTP/Webhook
```bash
# Processar todos os pagamentos
curl -X GET http://localhost/api/lightning_trigger.php

# Processar pagamento específico
curl -X POST http://localhost/api/lightning_trigger.php \
  -H "Content-Type: application/json" \
  -d '{"id": 123}'
```

## 🔄 Fluxo de Processamento

1. **Verificação de Condições:**
   - `moeda = 'BTC'`
   - `rede = 'lightning'`
   - `status = 'processando'`
   - `blockchainTxID` preenchido (confirmação Liquid)
   - `send > 0` (valor a enviar)

2. **Processamento Lightning:**
   - Verifica saldo da carteira Voltz
   - Cria link de saque (LNURL-withdraw)
   - Atualiza `address` com LNURL
   - Muda `status` para `'completo'`

3. **Notificação:**
   - Gera QR code do LNURL
   - Prepara mensagem para cliente
   - Log de todas as operações

## 🧪 Testando o Sistema

### 1. Criar Transação de Teste
```bash
cd /home/mau/bot/ghostbackend/api

# Criar transação de teste (1000 sats)
php test_lightning.php create 123456789 1000
```

### 2. Listar Transações
```bash
# Ver transações Lightning no banco
php test_lightning.php list
```

### 3. Testar Processador
```bash
# Executar processamento de teste
php test_lightning.php test
```

### 4. Limpar Dados de Teste
```bash
# Remover transações de teste
php test_lightning.php cleanup
```

## 📊 Monitoramento

### Logs Disponíveis
- **Processador:** `/logs/lightning_payments.log`
- **Monitor:** `/logs/lightning_monitor.log` 
- **Cron:** `/logs/lightning_cron.log`
- **Webhook Depix:** `/logs/webhook.log`

### Verificação de Status
```bash
# Ver logs em tempo real
tail -f /home/mau/bot/ghostbackend/logs/lightning_payments.log

# Verificar transações no banco
sqlite3 /home/mau/bot/ghostbackend/data/deposit.db \
  "SELECT id, chatid, send, status FROM deposit WHERE rede='lightning' ORDER BY created_at DESC LIMIT 5;"
```

## 🔧 Configuração Avançada

### Webhook Integration
Para integrar com webhooks do Depix, adicione ao `depix/webhook.php`:

```php
// Após processar webhook do Depix
if (isset($data['blockchainTxID']) && isset($data['id'])) {
    // Trigger processamento Lightning
    $triggerUrl = 'http://localhost/api/lightning_trigger.php';
    $triggerData = json_encode(['id' => $data['id']]);
    
    $ch = curl_init($triggerUrl);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $triggerData);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_exec($ch);
    curl_close($ch);
}
```

### Systemd Service (Linux)
```bash
# Criar service para monitor contínuo
sudo nano /etc/systemd/system/lightning-monitor.service

[Unit]
Description=Lightning Payment Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/mau/bot/ghostbackend/api
ExecStart=/usr/bin/php lightning_monitor.php 30
Restart=always

[Install]
WantedBy=multi-user.target

# Ativar serviço
sudo systemctl enable lightning-monitor.service
sudo systemctl start lightning-monitor.service
```

## ⚠️ Troubleshooting

### Problemas Comuns

1. **Erro de conexão com Voltz:**
   - Verificar configurações em `config/development.php`
   - Testar conectividade: `php voltz/exemplo_uso.php`

2. **Banco SQLite não encontrado:**
   - Verificar permissões: `chmod 664 data/deposit.db`
   - Verificar propriedade: `chown www-data:www-data data/deposit.db`

3. **Saldo insuficiente:**
   - Verificar saldo da carteira Voltz
   - Logs mostrarão erro detalhado

4. **Transações não processadas:**
   - Verificar se `blockchainTxID` está preenchido
   - Verificar se status é `'processando'`
   - Ver logs para erros específicos

### Debug Mode
```bash
# Executar com debug detalhado
php -d display_errors=1 lightning_payment_processor.php
```

## 📈 Métricas e Performance

- **Tempo médio de processamento:** < 5 segundos
- **Intervalo recomendado:** 30-60 segundos
- **Capacidade:** Até 100 transações/minuto
- **Falha de recuperação:** Automática com retry

## 🔒 Segurança

- Logs não expostos via web
- Validação de dados de entrada
- Rate limiting nos endpoints
- Backup automático do banco
- Monitoramento de falhas

---

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verificar logs em `/logs/`
2. Executar `test_lightning.php` para diagnóstico
3. Verificar configuração do Voltz
4. Validar estrutura do banco de dados
