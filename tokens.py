# Configurações do Bot
class Config:
    # Token do Bot do Telegram
    TELEGRAM_BOT_TOKEN = "7226334777:AAEnunCE322uSFmaKzs5RPw5HOkxQAUwHsE"
    
    # Configurações do Banco de Dados
    DB_NAME = "ghost_bot.db"
    
    # Configurações de Transferência Bancária
    TED_BANCO = "Banco do Brasil"
    TED_AGENCIA = "0000-1"
    TED_CONTA = "12345-6"
    TED_CPF_CNPJ = "000.000.000-00"
    TED_FAVORECIDO = "Nome da Empresa LTDA"
    
    # Configurações da API de Pagamento
    PIX_API_URL = "https://basetria.xyz/bot_deposit"
    
    # Configurações de Boleto
    BOLETO_CHAT_ID = "@triacorelabs"

# Exemplo de uso:
# from tokens import Config
# token = Config.TELEGRAM_BOT_TOKEN
