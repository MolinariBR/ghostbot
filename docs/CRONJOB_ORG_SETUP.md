# Configuração Cron-job.org - Lightning Monitor

## 1. URL do Endpoint
```
https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025
```

## 2. Configurações no cron-job.org
- **Título**: Lightning Monitor Bot
- **URL**: https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025
- **Intervalo**: A cada 60 segundos (1 minuto - mínimo permitido)
- **Método**: GET
- **Timeout**: 30 segundos
- **Tentativas**: 3

## 3. Alterar Token de Segurança
No arquivo `/api/lightning_cron_endpoint.php`, linha 8:
```php
$expected_token = "SEU_TOKEN_SECRETO_AQUI";
```

## 4. Testar Localmente
```bash
cd /path/to/ghostbackend
./scripts/test_lightning_cron_endpoint.sh
```

## 5. Logs
- Web: `/logs/lightning_cron_web.log`
- Bot: `/ghost/logs/lightning_cron.log`
