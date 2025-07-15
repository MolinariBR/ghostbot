# Mapa de taxas de parceiro em centavos por método
PARCEIRO_TAXA_MAP = {
    'pix': 100,     # 1 real em centavos
    'depix': 100,  # 1 real em centavos
}

PARCEIRO_TAXA_PADRAO = 0  # Outros métodos: 0 centavos

def get_parceiro_in_cents(metodo: str) -> int:
    metodo = metodo.strip().lower()
    return PARCEIRO_TAXA_MAP.get(metodo, PARCEIRO_TAXA_PADRAO) 
    #teste