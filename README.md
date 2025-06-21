# Ghost Bot - Bot de Negociação de Criptomoedas

Bot do Telegram para compra e venda de criptomoedas com interface amigável.

## 🚀 Pré-requisitos

- Python 3.8 (recomendado) ou superior
- Conta no Telegram e token do BotFather
- Conta no Square Cloud (para deploy)

## 🛠️ Instalação Local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/MolinariBR/ghostbot.git
   cd ghostbot
   ```

2. **Crie e ative um ambiente virtual**
   ```bash
   # Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   # python -m venv venv
   # venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   # Método recomendado (usando setup.py)
   pip install -e .
   
   # Ou instale diretamente do requirements.txt
   # pip install -r requirements.txt
   ```

4. **Configure o ambiente**
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione suas variáveis de ambiente (veja `.env.example`)

## 🚀 Executando o Bot

```bash
# Ative o ambiente virtual se ainda não estiver ativado
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate  # Windows

# Execute o bot
python bot.py
```

## ☁️ Deploy no Square Cloud

1. Faça login na sua conta do [Square Cloud](https://squarecloud.app/)
2. Crie um novo aplicativo
3. Faça upload do diretório do projeto
4. Configure as variáveis de ambiente no painel do Square Cloud
5. Inicie o aplicativo

## 📋 Funcionalidades

- 🛒 Comprar criptomoedas
- 💰 Vender criptomoedas
- 🔧 Serviços disponíveis
- ❓ Ajuda e suporte
- 📜 Termos de uso

## 🏗️ Estrutura do Projeto

```
ghost-bot/
├── bot.py             # Script principal do bot
├── setup.py           # Configuração do pacote Python
├── requirements.txt   # Dependências do projeto
├── runtime.txt        # Versão do Python para deploy
├── .env              # Variáveis de ambiente (não versionado)
├── .env.example      # Exemplo de variáveis de ambiente
├── .gitignore        # Arquivos ignorados pelo git
├── README.md         # Este arquivo
├── compat.py         # Módulo de compatibilidade
└── menus/            # Módulos dos menus do bot
    ├── __init__.py
    ├── menu_compra.py
    └── menu_venda.py
```

## 🔧 Dependências Principais

- `python-telegram-bot==13.7` - Biblioteca para interação com a API do Telegram
- `requests` - Requisições HTTP
- `python-decouple` - Gerenciamento de variáveis de ambiente
- `aiosqlite` - Banco de dados SQLite assíncrono
- `Pillow` - Processamento de imagens (para QR Codes)

## 🐛 Solução de Problemas

### Erro: Módulo não encontrado
Se encontrar erros de módulos faltando, tente:
```bash
pip install -r requirements.txt --force-reinstall
```

### Erro: Python 3.13
O bot foi testado com Python 3.8. Para usar versões mais recentes, pode ser necessário ajustar as dependências.

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
