# Centralização de Configurações - `config_global.php`

Este diretório contém o arquivo `config_global.php`, responsável por centralizar o acesso a todas as configurações do sistema, incluindo tokens, chaves de API e parâmetros sensíveis.

## Funcionamento
- O arquivo `config_global.php` fornece a função `get_config($chave)`, que busca o valor da configuração desejada diretamente no banco `configuracoes.db`.
- Todas as APIs, scripts e sistemas que precisarem acessar configurações devem incluir este arquivo e utilizar a função para obter valores.
- As configurações podem ser atualizadas via painel administrativo, sem necessidade de editar arquivos manualmente.

## Exemplo de uso
```php
require_once __DIR__ . '/config_global.php';
$token_depix = get_config('depix_api_key');
$token_voltz = get_config('voltz_api_key');
$spread = get_config('spread_coingecko');
```

## Vantagens
- **Segurança:** Tokens e chaves não ficam espalhados em vários arquivos.
- **Manutenção:** Qualquer ajuste é feito no banco e refletido em todo o sistema.
- **Flexibilidade:** Novas configurações podem ser adicionadas sem alterar código.

## Observações
- Certifique-se de que o banco `configuracoes.db` está corretamente populado e acessível.
- O painel administrativo pode ser usado para editar e atualizar as configurações.
- Sempre utilize a função `get_config()` para acessar valores sensíveis ou variáveis de ambiente do sistema.
