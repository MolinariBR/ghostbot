# Configurações do Bot
class Config:
    # Configuração de Ambiente (True para produção, False para desenvolvimento)
    IS_PRODUCTION = True  # Ativado para produção - webhook
    
    # Token do Bot do Telegram
    TELEGRAM_BOT_TOKEN = "7105509014:AAENhZArthrysOBoEmdA6vaxE72pobliahI"
    
    # Configurações do Banco de Dados
    DB_NAME = "ghost_bot.db"
    
    # URLs da API
    API_URLS = {
        True: "https://useghost.squareweb.app/api/bot_deposit.php",    # Produção
        False: "https://useghost.squareweb.app/api/bot_deposit.php"  # Desenvolvimento
    }
    
    # URL base da API de depósito (será definida automaticamente)
    PIX_API_URL = API_URLS[IS_PRODUCTION]  # URL do endpoint de depósito no backend
    
    # Configurações de Transferência Bancária
    TED_BANCO = "Banco do Brasil"
    TED_AGENCIA = "0000-1"
    TED_CONTA = "12345-6"
    TED_CPF_CNPJ = "000.000.000-00"
    TED_FAVORECIDO = "Nome da Empresa LTDA"
    TED_CHAT_ID = "@GhosttP2P"  # Chat para TED, igual ao boleto
    TED_CHAT_URL = "https://t.me/GhosttP2P"  # Link direto para o chat
    
    # Configurações de Boleto
    BOLETO_CHAT_ID = "@GhosttP2P"

# Exemplo de uso:
# from tokens import Config
# token = Config.TELEGRAM_BOT_TOKEN