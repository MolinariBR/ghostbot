# Bancos de Dados

Este diretório contém os bancos de dados SQLite do sistema Ghost Bot.

## Estrutura dos Bancos de Dados

### 1. users.db
Armazena informações dos usuários e suas carteiras.

#### Tabela: users
- `id`: ID único do usuário
- `telegram_id`: ID do usuário no Telegram
- `username`: Nome de usuário no Telegram
- `first_name`: Primeiro nome do usuário
- `last_name`: Sobrenome do usuário
- `is_admin`: Se o usuário é administrador
- `created_at`: Data de criação
- `updated_at`: Data de atualização

#### Tabela: user_wallets
- `id`: ID único da carteira
- `user_id`: ID do usuário dono da carteira
- `currency`: Moeda (BTC, USDT, DEPIX)
- `address`: Endereço da carteira
- `balance`: Saldo atual
- `created_at`: Data de criação
- `updated_at`: Data de atualização

### 2. deposit.db
Gerencia depósitos e endereços de depósito.

#### Tabela: deposits
- `id`: ID único do depósito
- `user_id`: ID do usuário
- `tx_hash`: Hash da transação
- `currency`: Moeda do depósito
- `amount`: Valor depositado
- `status`: Status do depósito (pending, completed, failed)
- `confirmations`: Número de confirmações
- `required_confirmations`: Confirmações necessárias
- `address`: Endereço de depósito
- `created_at`: Data de criação
- `updated_at`: Data de atualização

#### Tabela: deposit_addresses
- `id`: ID único do endereço
- `user_id`: ID do usuário
- `currency`: Moeda do endereço
- `address`: Endereço de depósito
- `is_active`: Se o endereço está ativo
- `created_at`: Data de criação

### 3. servico.db
Gerencia serviços e pedidos.

#### Tabela: services
- `id`: ID único do serviço
- `name`: Nome do serviço
- `description`: Descrição do serviço
- `price_brl`: Preço em BRL
- `price_depix`: Preço em DEPIX
- `is_active`: Se o serviço está ativo
- `created_at`: Data de criação
- `updated_at`: Data de atualização

#### Tabela: orders
- `id`: ID único do pedido
- `user_id`: ID do usuário
- `service_id`: ID do serviço
- `status`: Status do pedido (pending, processing, completed, cancelled)
- `amount_brl`: Valor em BRL
- `amount_depix`: Valor em DEPIX
- `payment_tx`: Hash da transação de pagamento
- `created_at`: Data de criação
- `updated_at`: Data de atualização

### 4. cotacao.db
Armazena cotações e histórico.

#### Tabela: exchange_rates
- `id`: ID único da cotação
- `base_currency`: Moeda de origem (BTC, USDT, DEPIX)
- `target_currency`: Moeda de destino (BRL)
- `rate`: Taxa de câmbio
- `source`: Fonte da cotação (binance, coingecko, manual)
- `created_at`: Data de criação

#### Tabela: rate_history
- `id`: ID único do histórico
- `base_currency`: Moeda de origem
- `target_currency`: Moeda de destino
- `rate`: Taxa de câmbio
- `source`: Fonte da cotação
- `created_at`: Data de criação

## Como Usar

### Inicialização dos Bancos de Dados

Para criar e inicializar todos os bancos de dados, execute:

```bash
python database/create_databases.py
```

### Exemplos Práticos

#### 1. Gerenciamento de Usuários

```python
from database import get_or_create_user, execute_query

# Criar ou obter um usuário
user = get_or_create_user(
    telegram_id=123456789,
    username="joaosilva",
    first_name="João",
    last_name="Silva"
)

# Tornar um usuário administrador
execute_query(
    'users',
    'UPDATE users SET is_admin = 1 WHERE telegram_id = ?',
    (123456789,),
    fetch='none'
)
```

#### 2. Gerenciamento de Carteiras

```python
# Criar uma nova carteira para o usuário
execute_query(
    'users',
    '''
    INSERT INTO user_wallets (user_id, currency, address, balance)
    VALUES (?, ?, ?, ?)
    ''',
    (1, 'BTC', 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh', 0.0),
    fetch='none'
)

# Obter saldo de uma carteira
wallet = execute_query(
    'users',
    'SELECT * FROM user_wallets WHERE user_id = ? AND currency = ?',
    (1, 'BTC'),
    'one'
)
```

#### 3. Processamento de Depósitos

```python
# Registrar um novo depósito
execute_query(
    'deposit',
    '''
    INSERT INTO deposits 
    (user_id, tx_hash, currency, amount, status, address)
    VALUES (?, ?, ?, ?, ?, ?)
    ''',
    (1, 'tx1234567890', 'BTC', 0.01, 'pending', 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'),
    fetch='none'
)

# Atualizar status de um depósito
execute_query(
    'deposit',
    'UPDATE deposits SET status = ?, confirmations = ? WHERE tx_hash = ?',
    ('completed', 3, 'tx1234567890'),
    fetch='none'
)
```

#### 4. Gerenciamento de Serviços

```python
# Adicionar um novo serviço
execute_query(
    'servico',
    '''
    INSERT INTO services (name, description, price_brl, price_depix, is_active)
    VALUES (?, ?, ?, ?, ?)
    ''',
    ('Marketing Digital', 'Pacote de marketing digital', 500.00, 490.20, 1),
    fetch='none'
)

# Listar serviços ativos
services = execute_query(
    'servico',
    'SELECT * FROM services WHERE is_active = 1',
    fetch='all'
)
```

#### 5. Processamento de Pedidos

```python
# Criar um novo pedido
execute_query(
    'servico',
    '''
    INSERT INTO orders 
    (user_id, service_id, status, amount_brl, amount_depix, payment_tx)
    VALUES (?, ?, ?, ?, ?, ?)
    ''',
    (1, 1, 'pending', 500.00, 490.20, 'tx_payment_123'),
    fetch='none'
)

# Atualizar status de um pedido
execute_query(
    'servico',
    'UPDATE orders SET status = ? WHERE id = ?',
    ('completed', 1),
    fetch='none'
)
```

#### 6. Gerenciamento de Cotações

```python
# Registrar uma nova cotação
execute_query(
    'cotacao',
    '''
    INSERT INTO exchange_rates 
    (base_currency, target_currency, rate, source)
    VALUES (?, ?, ?, ?)
    ''',
    ('BTC', 'BRL', 325000.50, 'binance'),
    fetch='none'
)

# Obter a cotação mais recente
latest_rate = execute_query(
    'cotacao',
    '''
    SELECT * FROM exchange_rates 
    WHERE base_currency = ? AND target_currency = ?
    ORDER BY created_at DESC LIMIT 1
    ''',
    ('BTC', 'BRL'),
    'one'
)
```

### Funções Auxiliares

O módulo `database` oferece funções úteis para operações comuns:

```python
from database import (
    get_connection,     # Obter conexão com um banco
    execute_query,      # Executar consultas SQL
    execute_many,       # Executar consulta com múltiplos parâmetros
    execute_script,     # Executar script SQL
    get_or_create_user  # Obter ou criar usuário
)
```

### Boas Práticas

1. **Sempre feche as conexões**: Use `with` statement ou chame `.close()` após o uso
2. **Use parâmetros**: Sempre use parâmetros nas consultas para evitar SQL injection
3. **Trate erros**: Use blocos try/except para lidar com possíveis erros de banco de dados
4. **Faça backup regular**: Mantenha backups dos seus bancos de dados
5. **Use transações**: Para operações críticas, use transações para garantir a integridade dos dados
