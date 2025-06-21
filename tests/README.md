# Testes do Bot de Criptomoedas

Este diretório contém os testes automatizados para o bot de criptomoedas.

## Estrutura de Diretórios

```
tests/
├── __init__.py
├── conftest.py           # Configurações globais de teste
├── integration/          # Testes de integração
│   ├── __init__.py
│   └── test_fluxo_compra.py
└── unit/                 # Testes unitários
    ├── __init__.py
    ├── test_api_binance.py
    ├── test_api_coingecko.py
    ├── test_cotacao.py
    ├── test_depix.py
    ├── test_menu_compra.py
    └── test_menu_venda.py
```

## Como Executar os Testes

### Instalar Dependências

Certifique-se de ter todas as dependências instaladas:

```bash
pip install -r requirements-dev.txt
```

### Executar Todos os Testes

```bash
python run_tests.py
```

### Executar Apenas Testes Unitários

```bash
pytest tests/unit/ -v
```

### Executar Apenas Testes de Integração

```bash
pytest tests/integration/ -v
```

### Executar um Teste Específico

```bash
pytest tests/unit/test_depix.py -v
```

### Gerar Relatório de Cobertura

```bash
pytest --cov=api --cov=menus --cov-report=html:htmlcov
```

## Tipos de Testes

### Testes Unitários

- Testam unidades individuais de código (funções, classes) de forma isolada
- Rápidos de executar
- Sem dependências externas (usam mocks)

### Testes de Integração

- Testam a interação entre diferentes módulos
- Podem depender de serviços externos (APIs, banco de dados)
- Mais lentos que os testes unitários

## Boas Práticas

1. **Nomes Descritivos**: Use nomes descritivos para os testes
2. **Um Teste por Coisa**: Cada teste deve verificar apenas uma coisa
3. **Use Mocks**: Para testes unitários, use mocks para simular dependências externas
4. **Teste Casos de Borda**: Não se esqueça de testar casos de erro e entradas inesperadas
5. **Mantenha os Testes Atualizados**: Atualize os testes sempre que o código for alterado

## Logs

Os logs dos testes são salvos em `logs/tests.log`.

## Cobertura de Código

Para verificar a cobertura de código:

```bash
pytest --cov=api --cov=menus --cov-report=term-missing
```

Isso mostrará quais linhas de código não estão sendo cobertas pelos testes.
