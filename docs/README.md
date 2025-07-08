# Ghost Bot - Bot de Negociação de Criptomoedas

Bot do Telegram para compra e venda de criptomoedas com interface amigável e integração PIX.

## ✨ Melhorias Recentes

- **Maior estabilidade**: Implementação de reconexão automática e tratamento de erros robusto
- **Desempenho aprimorado**: Timeouts configuráveis e gerenciamento de conexão otimizado
- **Logs detalhados**: Sistema de logging aprimorado com rotação de arquivos
- **Segurança**: Atualização das dependências para as versões mais recentes e seguras
- **Manutenção**: Código mais organizado e fácil de manter

## 🚀 Pré-requisitos

- Python 3.8 ou superior (recomendado Python 3.9+)
- Conta no Telegram e token do BotFather
- Dependências do sistema (se necessário):
  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install python3-dev python3-pip python3-venv
  ```

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
   # .\venv\Scripts\activate
   ```

3. **Atualize o pip e instale as dependências**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure o bot**
   - Edite o arquivo `tokens.py` e adicione suas credenciais necessárias

## 🚀 Executando o Bot

### Modo Desenvolvimento
```bash
# Ative o ambiente virtual se ainda não estiver ativado
source venv/bin/activate  # Linux/MacOS
# .\venv\Scripts\activate  # Windows

# Execute o bot em modo de desenvolvimento
python bot.py
```

### Em Produção
Recomenda-se o uso de um gerenciador de processos como o PM2 para manter o bot em execução:

```bash
# Instale o PM2 globalmente (se ainda não tiver)
npm install -g pm2

# Inicie o bot com PM2
pm2 start bot.py --name "ghost-bot" --interpreter python3 --restart-delay=3000

# Monitore os logs
pm2 logs ghost-bot
```

## 🔍 Solução de Problemas

### Erros de Conexão
Se encontrar erros de conexão, verifique:
1. Seu token do bot está correto
2. Sua conexão com a internet está estável
3. Seu firewall não está bloqueando as conexões de saída

### Logs
Os logs são salvos em `logs/bot.log` e incluem informações detalhadas sobre o funcionamento do bot.

## 🤝 Contribuindo
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e enviar pull requests.
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
