# Mapeamento de regras de comissão por moeda (acima de 500 reais)
COMISSAO_MAP = {
    'btc':    {'percentual': 0.035, 'fixo_in_cents': 0},
    'bitcoin':{'percentual': 0.035, 'fixo_in_cents': 0},
    'usdt':   {'percentual': 0.05,  'fixo_in_cents': 0},
    'depix':  {'percentual': 0.035, 'fixo_in_cents': 0},
}

# Comissão padrão para valores de 10 até 500 reais
COMISSAO_PADRAO = {'percentual': 0.10, 'fixo_in_cents': 0}


def get_comissao(moeda: str, valor_brl: float) -> dict | None:
    moeda = moeda.lower()
    if valor_brl < 10:
        return None
    if valor_brl <= 500:
        regra = COMISSAO_PADRAO
    else:
        regra = COMISSAO_MAP.get(moeda)
        if not regra:
            return None
    percentual = regra['percentual']
    fixo_in_cents = regra['fixo_in_cents']
    comissao = valor_brl * percentual
    comissao_in_cents = int(round(comissao * 100)) + fixo_in_cents
    return {
        'moeda': moeda,
        'valor_brl': valor_brl,
        'percentual': percentual,
        'fixo_in_cents': fixo_in_cents,
        'comissao': round(comissao, 2),
        'comissao_in_cents': comissao_in_cents
    } 
    #teste