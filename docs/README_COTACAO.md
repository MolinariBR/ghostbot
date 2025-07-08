# Script de Atualização de Cotações (`atualiza_cotacoes.php`)

Este diretório contém o script responsável por consultar as APIs de cotação (CoinGecko e Binance) para as moedas BTC, USDT e DEPIX, e armazenar os valores no banco de dados `cotacao.db`.

## Funcionamento
- O script `atualiza_cotacoes.php` consulta as APIs CoinGecko e Binance para as moedas BTC, USDT e DEPIX, sempre em relação ao BRL.
- As consultas devem ser feitas 3 vezes por minuto (a cada 20 segundos), utilizando agendamento via cron.
- Cada cotação obtida é armazenada na tabela `cotacoes` do banco `cotacao.db`, com timestamp e origem.
- Em caso de falha na consulta, a última cotação válida permanece disponível no banco, garantindo continuidade do serviço.

## Como agendar no cron
Para rodar o script automaticamente a cada 20 segundos, adicione a seguinte linha ao crontab do sistema (ajuste o caminho conforme necessário):

```
* * * * * php /CAMINHO/ghostbackend/scripts/atualiza_cotacoes.php
* * * * * sleep 20; php /CAMINHO/ghostbackend/scripts/atualiza_cotacoes.php
* * * * * sleep 40; php /CAMINHO/ghostbackend/scripts/atualiza_cotacoes.php
```

> Substitua `/CAMINHO/ghostbackend/scripts/` pelo caminho absoluto do seu projeto.

## Estrutura esperada do banco `cotacao.db`
A tabela `cotacoes` possui os seguintes campos:
- `id` (INTEGER, PK, autoincremento)
- `moeda_origem` (TEXT)
- `moeda_destino` (TEXT)
- `valor` (REAL)
- `spread` (REAL, opcional)
- `data_atualizacao` (TIMESTAMP)
- `ativo` (INTEGER)

Cada nova cotação é registrada com o horário da consulta, permitindo histórico e fallback.

## Observações
- Certifique-se de que as APIs estejam acessíveis localmente (ajuste as URLs no script se necessário).
- O script pode ser executado manualmente para testes.
- O campo `spread` pode ser utilizado para ajustes de preço, se necessário.
