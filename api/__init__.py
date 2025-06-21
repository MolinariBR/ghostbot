"""
Módulo de integração com APIs de criptomoedas.

Este pacote fornece acesso às APIs de cotações de criptomoedas como Binance e CoinGecko,
com uma camada de abstração que permite trocar facilmente entre diferentes provedores.
"""

from .api_binance import binance_api
from .api_coingecko import coingecko_api

# Exporta as instâncias das APIs
__all__ = ['binance_api', 'coingecko_api']
