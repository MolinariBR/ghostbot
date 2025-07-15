# Esqueleto inicial para lógica de validação de cotação e cálculo final

from .cotacao import get_realtime_price
from .comissao import get_comissao
from .limites import get_limite_in_cents
from .parceiro import get_parceiro_in_cents

def validar_pedido(moeda: str, valor_brl: float, chatid: str, compras: int, metodo: str, rede: str) -> dict:
    # 1. Cotação
    cotacao_info = get_realtime_price(moeda, 'brl')
    preco_btc = cotacao_info['price'] if 'price' in cotacao_info else 0

    # 2. Comissão
    comissao_info = get_comissao(moeda, valor_brl)
    comissao_in_cents = comissao_info['comissao_in_cents'] if comissao_info else 0

    # 3. Limite
    limite_in_cents = get_limite_in_cents(chatid, compras)

    # 4. Parceiro
    parceiro_in_cents = get_parceiro_in_cents(metodo)

    # 5. Valor bruto em centavos
    amount_in_cents = int(round(valor_brl * 100))
    # 6. Valor líquido a receber (em centavos)
    send_in_cents = amount_in_cents - comissao_in_cents - parceiro_in_cents

    # 7. Converter para sats (se for BTC ou DEPIX)
    sats = 0
    if preco_btc > 0 and moeda.lower() in ('btc', 'bitcoin', 'depix'):
        sats = int((send_in_cents / 100) / preco_btc * 100_000_000)

    # 8. Montar resumo
    return {
        'moeda': moeda,
        'rede': rede,
        'valor_brl': valor_brl,
        'cotacao': {
            'preco_btc': preco_btc,
            'fonte': cotacao_info.get('source', ''),
            'data_atualizacao': cotacao_info.get('timestamp', '')
        },
        'comissao': {
            'valor': comissao_in_cents / 100,
            'valor_in_cents': comissao_in_cents,
            'percentual': comissao_info['percentual'] if comissao_info else 0
        },
        'parceiro': {
            'valor': parceiro_in_cents / 100,
            'valor_in_cents': parceiro_in_cents
        },
        'limite': {
            'maximo': limite_in_cents / 100,
            'maximo_in_cents': limite_in_cents
        },
        'valor_recebe': {
            'brl': send_in_cents / 100,
            'sats': sats
        },
        'amount_in_cents': amount_in_cents,
        'send_in_cents': send_in_cents
    } 
    #teste