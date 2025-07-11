# Mapa de comissão por moeda e faixa de valor
COMISSAO_MAPA = {
    "BITCOIN": [
        {"min": 10, "max": 500, "percentual": 10.0},
        {"min": 500.01, "max": float("inf"), "percentual": 3.5}
    ],
    "DEPIX": [
        {"min": 10, "max": 500, "percentual": 10.0},
        {"min": 500.01, "max": float("inf"), "percentual": 1.5}
    ],
    "USDT": [
        {"min": 10, "max": 500, "percentual": 10.0},
        {"min": 500.01, "max": float("inf"), "percentual": 5.0}
    ]
}

def calcular_comissao(valor: float, moeda: str, pix: bool = False) -> tuple[float, float, float]:
    """
    Calcula a comissão conforme o mapa de regras.
    Se for via PIX, adiciona taxa fixa de R$1,00.
    Retorna (percentual, valor_comissao, valor_total)
    """
    if valor < 10:
        raise ValueError("Valor mínimo para comissão é R$10,00")
    moeda_key = moeda.upper()
    if "BTC" in moeda_key:
        moeda_key = "BITCOIN"
    for key in COMISSAO_MAPA.keys():
        if key in moeda_key:
            for faixa in COMISSAO_MAPA[key]:
                if faixa["min"] <= valor <= faixa["max"]:
                    percentual = faixa["percentual"]
                    comissao = valor * (percentual / 100)
                    taxa_pix = 1.0 if pix else 0.0
                    valor_total = comissao + taxa_pix
                    return percentual, comissao, valor_total
    # fallback
    percentual = 10.0
    comissao = valor * (percentual / 100)
    taxa_pix = 1.0 if pix else 0.0
    valor_total = comissao + taxa_pix
    return percentual, comissao, valor_total

# Exemplo de uso:
if __name__ == "__main__":
    for moeda in ["Bitcoin", "DEPIX", "USDT"]:
        for valor in [100, 600]:
            p, c, t = calcular_comissao(valor, moeda, pix=True)
            print(f"Moeda: {moeda}, Valor: R${valor:.2f} => Comissão: {p}% = R${c:.2f} + Taxa PIX: R$1,00 = Total: R${t:.2f}")
