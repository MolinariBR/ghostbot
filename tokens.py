# Configurações do Bot
class Config:
    # Configuração de Ambiente (True para produção, False para desenvolvimento)
    IS_PRODUCTION = True  # Mude para False em desenvolvimento
    
    # Token do Bot do Telegram
    TELEGRAM_BOT_TOKEN = "7226334777:AAEnunCE322uSFmaKzs5RPw5HOkxQAUwHsE"
    
    # Configurações do Banco de Dados
    DB_NAME = "ghost_bot.db"
    
    # URLs da API
    API_URLS = {
        True: "https://basetria.xyz/api/bot_deposit.php",    # Produção
        False: "https://ghostp2p.squareweb.app/api/bot_deposit.php"  # Desenvolvimento
    }
    
    # URL base da API de depósito (será definida automaticamente)
    PIX_API_URL = API_URLS[IS_PRODUCTION]  # URL do endpoint de depósito no backend
    
    # Configurações de Transferência Bancária
    TED_BANCO = "Banco do Brasil"
    TED_AGENCIA = "0000-1"
    TED_CONTA = "12345-6"
    TED_CPF_CNPJ = "000.000.000-00"
    TED_FAVORECIDO = "Nome da Empresa LTDA"
    
    # Configurações de Boleto
    BOLETO_CHAT_ID = "@triacorelabs"

# Exemplo de uso:
# from tokens import Config
# token = Config.TELEGRAM_BOT_TOKEN
