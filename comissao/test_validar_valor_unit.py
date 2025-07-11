import re
import pytest

MIN_VALOR = 10.0
MAX_VALOR = 5000.0

def validar_valor(valor_str: str):
    try:
        match = re.search(r'(\d+[\.,]?\d*)', valor_str.replace(' ', ''))
        if not match:
            return False, 0, "Formato inválido. Use apenas números (ex: 50.00)"
        valor = match.group(1).replace(',', '.')
        valor = float(valor)
        if valor < MIN_VALOR:
            return False, 0, f"Valor mínimo é R$ {MIN_VALOR:.2f}"
        if valor > MAX_VALOR:
            return False, 0, f"Valor máximo é R$ {MAX_VALOR:.2f}"
        return True, valor, ""
    except (ValueError, AttributeError):
        return False, 0, "Formato inválido. Use apenas números (ex: 50.00)"

@pytest.mark.parametrize("input_str,expected", [
    ("R$ 50,00", 50.00),
    ("50,00 reais", 50.00),
    ("50.00", 50.00),
    ("R$100.50", 100.50),
    ("250", 250.00),
    ("R$ 10,00", 10.00),
    ("R$ 5000,00", 5000.00),
    ("R$ 9,99", None),  # abaixo do mínimo
    ("R$ 6000,00", None), # acima do máximo
    ("abc", None), # inválido
])
def test_validar_valor(input_str, expected):
    valido, valor, erro = validar_valor(input_str)
    if expected is None:
        assert not valido
        assert "Formato inválido" in erro or "mínimo" in erro or "máximo" in erro
    else:
        assert valido
        assert abs(valor - expected) < 0.01
