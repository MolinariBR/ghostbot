from comissao.comissao import calcular_comissao
from comissao.cotacao import get_cotacao
from comissao.limites import get_limite, precisa_cpf, precisa_atendente, registrar_compra, MENSAGEM_CPF, MENSAGEM_ATENDENTE

# Função para formatar valores

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace('.', 'v').replace(',', '.').replace('v', ',')

def formatar_usd(valor):
    return f"US$ {valor:,.2f}".replace('.', 'v').replace(',', '.').replace('v', ',')

def formatar_sats(valor):
    return f"{int(valor):,} sats"

# Função principal do validador

def gerar_resumo_compra(chatid, moeda, rede, valor, pix=False, registrar=False):
    cotacao = get_cotacao(moeda)
    taxa_parceiro = 1.0 if pix or (moeda.upper() in ["BITCOIN", "BTC"] and rede.upper() in ["LIGHTNING", "LNT"]) else 0.0
    percentual, comissao, _ = calcular_comissao(valor, moeda, pix=pix)
    parceiro = taxa_parceiro if taxa_parceiro else 0.0
    valor_liquido = valor - comissao - parceiro
    # Limite do usuário
    limite = get_limite(chatid)
    precisa_cpf_flag = precisa_cpf(chatid, valor)
    precisa_atendente_flag = precisa_atendente(valor)
    if registrar and not precisa_cpf_flag and not precisa_atendente_flag:
        registrar_compra(chatid, valor)
    # Cálculo do valor recebido na moeda correta
    moeda_upper = str(moeda).upper()
    if "BITCOIN" in moeda_upper or "BTC" in moeda_upper:
        valor_btc = valor_liquido / cotacao if cotacao > 0 else 0
        valor_sats = int(valor_btc * 100_000_000)
        if valor_sats < 1:
            valor_sats = 1
        recebe = formatar_sats(valor_sats)
        cotacao_str = formatar_brl(cotacao) + " por BTC"
    elif moeda_upper == "DEPIX":
        recebe = formatar_brl(valor_liquido)
        cotacao_str = formatar_brl(cotacao) + " por BRL"
    elif moeda_upper == "USDT":
        valor_usdt = valor_liquido / cotacao if cotacao > 0 else 0
        recebe = formatar_usd(valor_usdt)
        cotacao_str = formatar_brl(cotacao) + " por USDT"
    else:
        recebe = formatar_brl(valor_liquido)
        cotacao_str = formatar_brl(cotacao)
    # Nome da moeda para exibir (ex: Bitcoin (BTC))
    nome_moeda = moeda
    if "BITCOIN" in moeda_upper or "BTC" in moeda_upper:
        nome_moeda = "Bitcoin (BTC)"
    elif moeda_upper == "USDT":
        nome_moeda = "USDT (Tether)"
    elif moeda_upper == "DEPIX":
        nome_moeda = "DEPIX (BRL)"
    resumo = (
        f"📋 *RESUMO DA COMPRA*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 Moeda: {nome_moeda}\n"
        f"⚡ Rede: {rede}\n"
        f"💰 Valor: {formatar_brl(valor)}\n"
        f"💸 Comissão ({percentual}%): {formatar_brl(comissao)}\n"
    )
    if parceiro:
        resumo += f"🤝 Taxa de Parceiro: {formatar_brl(parceiro)}\n"
    resumo += (
        f"💱 Cotação: {cotacao_str}\n"
        f"✅ Você recebe: {recebe}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
    )
    if precisa_atendente_flag:
        resumo += f"\n{MENSAGEM_ATENDENTE}"
    elif precisa_cpf_flag:
        resumo += f"\n{MENSAGEM_CPF}"
    return resumo

# Exemplo de uso
if __name__ == "__main__":
    chatid = "123456"
    print(gerar_resumo_compra(chatid, "Bitcoin", "Lightning", 1000, pix=True))
    print(gerar_resumo_compra(chatid, "DEPIX", "Liquid", 1000))
    print(gerar_resumo_compra(chatid, "USDT", "Polygon", 1000))
