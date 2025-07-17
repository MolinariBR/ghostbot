# Esqueleto inicial para lógica de validação de cotação e cálculo final
   # Forçar git a versionar este arquivo
from .cotacao import get_realtime_price
from .comissao import get_comissao
from .limites import get_limite_in_cents
from .parceiro import get_parceiro_in_cents
import uuid

def validar_pedido(moeda: str, valor_brl: float, chatid: str, compras: int, metodo: str, rede: str) -> dict:
    # 1. Cotação
    cotacao_info = get_realtime_price(moeda, 'brl')
    preco_btc = cotacao_info['price'] if 'price' in cotacao_info else 0
    fonte = cotacao_info.get('source', '')
    vs = cotacao_info.get('vs', 'brl')
    print(f"[VALIDADOR] preco_btc: {preco_btc} | fonte: {fonte} | vs: {vs}")

    # Se a cotação veio em USD, converter para BRL
    if vs == 'usd':
        # TODO: Buscar cotação USD/BRL online se possível
        usd_brl = 5.40  # Valor fixo temporário, ajuste conforme necessário
        preco_btc = preco_btc * usd_brl
        print(f"[VALIDADOR] preco_btc convertido para BRL: {preco_btc}")

    # 2. Comissão
    comissao_info = get_comissao(moeda, valor_brl)
    if comissao_info is None:
        return {
            'erro': True,
            'mensagem': f'Operação não permitida para {moeda.upper()} com valor de R$ {valor_brl:.2f}.',
            'moeda': moeda,
            'valor_brl': valor_brl
        }
    comissao_in_cents = comissao_info['comissao_in_cents']

    # 3. Limite
    limite_in_cents = get_limite_in_cents(chatid, compras)

    # 4. Parceiro
    parceiro_in_cents = get_parceiro_in_cents(metodo)

    # 5. Valor bruto em centavos
    amount_in_cents = int(round(valor_brl * 100))
    # 6. Valor líquido a receber (em centavos)
    send_in_cents = amount_in_cents - comissao_in_cents - parceiro_in_cents

    print(f"[VALIDADOR] amount_in_cents: {amount_in_cents} | send_in_cents: {send_in_cents}")

    # 7. Converter para sats (se for BTC ou DEPIX)
    sats = 0
    if preco_btc > 0 and moeda.lower() in ('btc', 'bitcoin', 'depix'):
        sats = int((send_in_cents / 100) / preco_btc * 100_000_000)
        print(f"[VALIDADOR] sats calculado: {sats}")

    # 8. Montar resumo
    gtxid = str(uuid.uuid4())
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
        'send_in_cents': send_in_cents,
        'gtxid': gtxid
    } 
    #teste