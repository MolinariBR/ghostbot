# Configuração do Cron Lightning Monitor

## Como funciona o sistema

1. **PIX é pago** → Depix confirma e preenche `blockchainTxID` 
2. **Cron executa** → Verifica depósitos Lightning com PIX confirmado
3. **Invoice solicitado** → Bot pede invoice Lightning do cliente
4. **Pagamento processado** → Ghost paga via Voltz

## Scripts criados

- `cron_lightning_monitor.py` - Script principal que monitora Lightning
- `scripts/run_lightning_cron.sh` - Wrapper que ativa venv e executa
- `logs/lightning_cron.log` - Log das execuções

## Configurar no crontab

Para executar a cada 30 segundos:

```bash
# Editar crontab
crontab -e

# Adicionar estas linhas (executa a cada 30 segundos)
# Substitua /path/to/ghost pelo caminho real do seu bot
* * * * * /path/to/ghost/scripts/run_lightning_cron.sh
* * * * * ( sleep 30 ; /path/to/ghost/scripts/run_lightning_cron.sh )
```

Ou usar um arquivo cron dedicado:

```bash
# Criar arquivo cron
sudo vim /etc/cron.d/lightning-monitor

# Conteúdo:
# Executa Lightning monitor a cada 30 segundos
* * * * * user /path/to/ghost/scripts/run_lightning_cron.sh
* * * * * user ( sleep 30 ; /path/to/ghost/scripts/run_lightning_cron.sh )
```

## Testar manualmente

```bash
# Teste simples
cd /path/to/ghost
./scripts/run_lightning_cron.sh

# Verificar logs
tail -f logs/lightning_cron.log

# Teste com venv diretamente
source .venv/bin/activate
python cron_lightning_monitor.py
```

## Fluxo completo

### Antes (PROBLEMA):
```
User paga PIX → Depix confirma → NADA ACONTECE → Invoice nunca solicitado
```

### Depois (CORRETO):
```
1. User paga PIX
2. Depix confirma → preenche blockchainTxID
3. Cron encontra Lightning com blockchainTxID
4. Bot solicita invoice Lightning
5. User envia invoice
6. Ghost paga via Voltz
```

## Condições para processar

O cron só processa depósitos que atendem TODAS as condições:

1. ✅ `rede` contém "lightning"
2. ✅ `blockchainTxID` está preenchido (PIX confirmado)
3. ✅ `status` não é 'completed', 'cancelled' ou 'failed'
4. ✅ `depix_id` está presente
5. ✅ `chatid` está presente

## Logs importantes

```bash
# Monitorar em tempo real
tail -f /path/to/ghost/logs/lightning_cron.log

# Verificar depósitos encontrados
grep "Encontrados.*Lightning pendentes" logs/lightning_cron.log

# Ver processamentos
grep "Processando Lightning pendente" logs/lightning_cron.log
```

## Troubleshooting

### Erro: "Ambiente virtual não encontrado"
```bash
cd /path/to/ghost
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Módulo não encontrado"
```bash
cd /path/to/ghost
source .venv/bin/activate
pip install python-telegram-bot requests
```

### Erro: "Token do bot não encontrado"
Verificar se existe `tokens.py` com `BOT_TOKEN`

### Timeout nas requisições
Normal - o backend pode estar lento. O script tenta novamente na próxima execução.

## Status atual

✅ Script criado e testado
✅ Ambiente virtual configurado  
✅ Logs funcionando
⏳ **PENDENTE: Adicionar ao crontab para execução automática**
