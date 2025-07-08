# Ghost Backend

Backend para o sistema de pagamentos Ghost, integrado com PIX e criptomoedas via rede Liquid.

## Funcionalidades

- Criação de pedidos de pagamento via PIX
- Integração com carteiras cripto na rede Liquid
- Painel administrativo para gerenciamento de transações
- Webhooks para notificações em tempo real
- API RESTful para integração com outros sistemas

## Requisitos

- PHP 8.0 ou superior
- SQLite3
- Extensões PHP: sqlite3, json, curl
- Servidor web (Apache/Nginx) ou PHP Built-in Server

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/ghostbackend.git
   cd ghostbackend
   ```

2. Configure as permissões:
   ```bash
   chmod -R 755 ./
   chmod -R 777 /data
   ```

3. Inicialize o banco de dados:
   ```bash
   php setup_databases.php
   ```

4. Inicie o servidor de desenvolvimento:
   ```bash
   php -S localhost:8000
   ```

5. Acesse o painel administrativo em `http://localhost:8000`

## Estrutura do Projeto

```
ghostbackend/
├── api/                  # Endpoints da API
├── data/                 # Banco de dados SQLite
├── depix/                # Integração com API Depix
├── assets/               # Arquivos estáticos (CSS, JS, imagens)
├── .gitignore           # Arquivos ignorados pelo Git
├── README.md            # Documentação
├── index.php            # Página inicial
├── transacoes.php       # Painel de transações
└── setup_databases.php  # Script de configuração do banco
```

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
PIX_API_URL=https://sua-api-pix.com
PIX_API_KEY=sua_chave_api
WEBHOOK_SECRET=sua_chave_secreta
```

## Desenvolvimento

Para contribuir com o projeto:

1. Crie um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das alterações (`git commit -am 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
