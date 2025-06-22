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
📜 *TERMOS DE USO E POLÍTICA DE PRIVACIDADE*

*1. Aceitação dos Termos* 
Ao utilizar este serviço, você concorda com estes termos e condições. Se não concordar, por favor, não utilize nosso serviço.

*2. Serviço Oferecido* 
Este serviço permite a compra e venda de criptomoedas de forma facilitada através do Telegram.

*3. Responsabilidades do Usuário* 
- É de responsabilidade do usuário fornecer informações corretas e atualizadas.
- O usuário é responsável por manter a segurança de suas credenciais de acesso.
- O usuário concorda em não utilizar o serviço para atividades ilegais.

*4. Política de Privacidade* 
- Coletamos apenas as informações necessárias para a prestação do serviço.
- Não compartilhamos seus dados pessoais com terceiros sem sua autorização, exceto quando exigido por lei.
- Utilizamos medidas de segurança para proteger suas informações.

*5. Limitação de Responsabilidade* 
- Não nos responsabilizamos por perdas decorrentes de flutuações do mercado de criptomoedas.
- Não nos responsabilizamos por perdas resultantes de falhas de segurança causadas pelo usuário.

*6. Alterações nos Termos* 
Reservamo-nos o direito de modificar estes termos a qualquer momento. As alterações entrarão em vigor imediatamente após a publicação.

*7. Lei Aplicável* 
Estes termos são regidos pelas leis do Brasil e qualquer litígio será resolvido no foro da comarca de São Paulo/SP.

*8. Contato* 
Para dúvidas sobre estes termos, entre em contato através do nosso suporte.

*Data da última atualização: 22/06/2024*
"""
    return termos.strip()

def obter_termos_resumido() -> str:
    """
    Retorna uma versão resumida dos termos para exibição em menus ou mensagens curtas.
    
    Returns:
        str: Texto resumido dos termos.
    """
    return "📜 Termos de Uso e Política de Privacidade"

# Exemplo de uso:
if __name__ == "__main__":
    print(obter_termos())
