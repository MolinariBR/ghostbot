import pytest
from menus.menu_compra_v2 import MenuCompraV2

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
    menu = MenuCompraV2()
    valido, valor, erro = menu.validar_valor(input_str)
    if expected is None:
        assert not valido
        assert "Formato inválido" in erro or "mínimo" in erro or "máximo" in erro
    else:
        assert valido
        assert abs(valor - expected) < 0.01

