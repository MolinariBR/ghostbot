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
O bot facilita a compra de criptomoedas, com controle de comissão, limites diários por usuário e direcionamento ao atendimento quando necessário.

*2. Comissão e Limites*
Todas as compras possuem comissão variável conforme moeda e valor. Os limites diários são escalonados por usuário, iniciando em R$500,00 e podendo chegar até R$4.999,99. Compras acima do limite exigem CPF e/ou contato com o atendente.

*3. Métodos de Pagamento*
O método principal é o PIX. Para TED ou boleto, ou para redes específicas (Liquid, Polygon, Onchain), o usuário deve falar com o atendente @GhosttP2P. Pagamentos de terceiros só são permitidos para usuários cadastrados.

*4. Regras de Pagamento*
Chave PIX: Copie todo o texto da chave PIX e pague na área "PIX Copia e Cola" do seu banco. Envie o comprovante após o pagamento.

*5. Contestações e Retenção*
Tentativas de chargeback, MED ou contestações indevidas são proibidas. Pagamentos retidos exigem KYC para estorno, feito apenas à conta de origem. Não nos responsabilizamos por atrasos causados por dados incorretos.

*6. Privacidade*
Dados são tratados com confidencialidade, usados apenas para averiguação e controle de limites.

*7. Aceitação*
Usar o bot implica concordância com estes termos, incluindo regras de comissão, limites e métodos de pagamento.

Dúvidas ou compras especiais? Fale com o suporte: @GhosttP2P
"""
    return termos.strip()

def obter_termos_resumido() -> str:
    """
    Retorna uma versão resumida dos termos para exibição em menus ou mensagens curtas.
    
    Returns:
        str: Texto resumido dos termos.
    """
    return "📜 Termos de Uso: Comissão, Limites, Pagamentos e Atendimento via @GhosttP2P"

# Exemplo de uso:
if __name__ == "__main__":
    print(obter_termos())
