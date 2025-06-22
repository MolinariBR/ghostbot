"""
Módulo que contém as informações de ajuda e contatos do serviço.
"""

def obter_ajuda() -> str:
    """
    Retorna o texto de ajuda formatado para o Telegram com informações de contato.
    
    Returns:
        str: Texto formatado em Markdown com as informações de ajuda e contatos.
    """
    ajuda_texto = """
🤖 *Central de Ajuda do Ghost Bot* 🤖

Bem-vindo à central de ajuda! Aqui você encontra informações sobre como utilizar nossos serviços e como entrar em contato conosco.

*📌 Como usar o bot:*
- Utilize o menu principal para navegar entre as opções
- Para comprar criptomoedas, clique em *🛒 Comprar*
- Para vender criptomoedas, clique em *💰 Vender*
- Consulte os termos de uso em *📜 Termos*

*📞 Atendimento ao Cliente*
Estamos disponíveis para te ajudar com qualquer dúvida ou problema.

*📧 E-mail:* suporte@ghostbot.com.br  
*📱 Telefone/WhatsApp:* +55 (11) 91234-5678  
*🌐 Site:* [www.ghostbot.com.br](https://www.ghostbot.com.br)  
*✉️ Telegram:* @suportegb  

*🕒 Horário de Atendimento:*  
Segunda a Sexta: 9h às 18h  
Sábado: 9h às 13h  
Domingo: Fechado

*⚠️ Dúvidas Frequentes:*

*1. Como faço minha primeira compra?*  
Acesse o menu *🛒 Comprar*, escolha a criptomoeda e siga as instruções.

*2. Qual o prazo para entrega?*  
As transações são processadas em até 30 minutos após a confirmação do pagamento.

*3. Como faço para vender minhas criptomoedas?*  
Acesse o menu *💰 Vender* e siga as instruções para iniciar a venda.

*4. Meu pagamento não foi identificado, o que fazer?*  
Entre em contato com nosso suporte informando o número da transação.

Estamos à disposição para melhor atendê-lo!

*Equipe Ghost Bot* 👻
"""
    return ajuda_texto.strip()

def obter_ajuda_resumida() -> str:
    """
    Retorna uma versão resumida da mensagem de ajuda.
    
    Returns:
        str: Texto resumido da ajuda.
    """
    return "❓ Central de Ajuda - Clique para informações detalhadas"

# Exemplo de uso:
if __name__ == "__main__":
    print(obter_ajuda())
