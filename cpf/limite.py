# Lógica de cálculo de limite diário para usuários

LIMITE_ESCADA = [
    500.00,  # 1ª compra
    850.00,  # 2ª compra
    1000.00, # 3ª compra
    2000.00, # 4ª compra
    2500.00, # 5ª compra
    3000.00, # 6ª compra
    3500.00, # 7ª compra
    4000.00, # 8ª compra
    4500.00, # 9ª compra
    5000.00  # 10ª compra ou mais
]

LIMITE_MAXIMO = 5000.00


def calcular_limite_diario(num_compras: int, cpf: str = None) -> float:
    """
    Calcula o limite diário do usuário.
    Se CPF válido, retorna o limite máximo.
    Caso contrário, segue a escada de compras.
    """
    from .validador import validar_cpf
    if cpf and validar_cpf(cpf):
        return LIMITE_MAXIMO
    idx = min(num_compras, len(LIMITE_ESCADA)) - 1
    return LIMITE_ESCADA[max(idx, 0)]
