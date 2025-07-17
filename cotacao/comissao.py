   # Forçar git a versionar este arquivo
# Regras de comissão detalhadas para BTC e USDT
BTC_COMISSOES = [
    {'min': 10,    'max': 500,   'percentual': 0.10, 'fixo_in_cents': 0},
    {'min': 500.01,'max': 1000,  'percentual': 0.06, 'fixo_in_cents': 0},
    {'min': 1000.01,'max': 4999, 'percentual': 0.05, 'fixo_in_cents': 0},
]

# Comissão DEPIX: a partir de 100 reais até 4999
DEPIX_COMISSAO = {'min': 100, 'max': 4999, 'percentual': 0.019, 'fixo_in_cents': 0}

COMISSAO_MAP = {
    'btc':    BTC_COMISSOES,
    'bitcoin':BTC_COMISSOES,
    'usdt':   BTC_COMISSOES,
    'depix':  [DEPIX_COMISSAO],
}

COMISSAO_PADRAO = {'percentual': 0.10, 'fixo_in_cents': 0}


def get_comissao(moeda: str, valor_brl: float) -> dict | None:
    moeda = moeda.lower()
    if moeda == 'depix' and valor_brl < 100:
        return None
    if valor_brl < 10:
        return None
    regras = COMISSAO_MAP.get(moeda)
    if not regras:
        if valor_brl <= 500:
            regra = COMISSAO_PADRAO
        else:
            return None
    else:
        regra = None
        for r in regras:
            if valor_brl >= r['min'] and (('max' not in r) or valor_brl <= r['max']):
                regra = r
                break
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