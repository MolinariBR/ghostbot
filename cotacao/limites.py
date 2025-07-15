# Mapa de limites progressivos por número de compras (em centavos)
LIMITES_MAP = {
    0: 50000,    # 500.00
    1: 85000,    # 850.00
    2: 150000,   # 1500.00
    3: 250000,   # 2500.00
    4: 350000,   # 3500.00
    5: 499999,   # 4999.99
}

LIMITE_MAXIMO = 499999  # 4999.99 em centavos


def get_limite_in_cents(chatid: str, compras: int) -> int:
    compras = int(compras)
    if compras < 0:
        compras = 0
    if compras in LIMITES_MAP:
        return LIMITES_MAP[compras]
    return LIMITE_MAXIMO 