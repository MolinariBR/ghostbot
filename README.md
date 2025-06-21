# Ghost Bot - Bot de Negociação de Criptomoedas

Bot do Telegram para compra e venda de criptomoedas com interface amigável.

## 🚀 Como Executar

1. **Configuração Inicial**
   ```bash
   # Clone o repositório
   git clone <seu-repositorio>
   cd ghost-bot
   
   # Crie um ambiente virtual
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   
   # Instale as dependências
   pip install -r requirements.txt
   ```

2. **Configure o Ambiente**
   - Renomeie `.env.example` para `.env`
   - Adicione seu token do BotFather ao arquivo `.env`

3. **Inicie o Bot**
   ```bash
   python bot.py
   ```

## 📋 Funcionalidades

- 🛒 Comprar Bitcoin
- 💰 Vender Bitcoin
- 🔧 Serviços disponíveis
- ❓ Ajuda e suporte
- 📜 Termos de uso

## 🔧 Estrutura do Projeto

```
ghost-bot/
├── bot.py           # Script principal do bot
├── requirements.txt # Dependências
├── .env            # Variáveis de ambiente
├── .gitignore      # Arquivos ignorados pelo git
└── README.md       # Este arquivo
```

## 📝 Licença

Este projeto está sob a licença MIT.
