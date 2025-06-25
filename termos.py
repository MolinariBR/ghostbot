"""
Módulo que contém os termos de uso e política de privacidade do serviço.
"""

def obter_termos() -> str:
    """
    Retorna o texto completo dos termos de uso e política de privacidade formatado para o Telegram.
    
    Returns:
        str: Texto formatado em Markdown com os termos de uso.
    """
    termos = """
📜 *Termos de Uso para Compra de Criptomoedas*

Ao usar este bot, você concorda com os termos abaixo:

*1. Objetivo*
O bot facilita a compra de criptomoedas, direcionando usuários a atendentes após confirmação do pagamento.

*2. Regras de Pagamento*
Chave PIX: Copie todo o texto da chave PIX e pague na área "PIX Copia e Cola" do seu banco.

Proibição de terceiros: Use apenas sua conta bancária. Pagamentos de terceiros são permitidos só para cadastrados no bot. Inconsistências podem levar à retenção do valor e processo de KYC para estorno.

Comprovante: Clique em PAGO, envie o comprovante e aguarde o atendente.

*3. Contestações Indevidas*
Tentativas de chargeback, MED ou contestações indevidas são proibidas.

Medidas legais serão tomadas, e custos bancários serão repassados ao usuário.

A entrega das criptomoedas será suspensa até a resolução da disputa.

*4. Responsabilidades do Usuário*
Forneça dados corretos e siga as instruções.

Fraudes ou uso indevido resultam em bloqueio e retenção de valores.

O usuário assume os riscos da compra de criptomoedas.

*5. Retenção e Estorno*
Pagamentos retidos por inconsistências ou contestações exigem KYC para estorno, feito apenas à conta de origem.

Não nos responsabilizamos por atrasos causados por dados incorretos.

*6. Privacidade*
Dados são tratados com confidencialidade, e usados apenas para averiguação.

*7. Aceitação*
Usar o bot implica concordância com estes termos.

Dúvidas? Fale com o suporte: @GhosttP2P
"""
    return termos.strip()

def obter_termos_resumido() -> str:
    """
    Retorna uma versão resumida dos termos para exibição em menus ou mensagens curtas.
    
    Returns:
        str: Texto resumido dos termos.
    """
    return "📜 Termos de Uso para Compra de Criptomoedas"

# Exemplo de uso:
if __name__ == "__main__":
    print(obter_termos())
