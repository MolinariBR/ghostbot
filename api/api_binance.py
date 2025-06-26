import os
import requests
from typing import Dict, Optional
from decimal import Decimal, ROUND_DOWN
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

class BinanceAPI:
    BASE_URL = "https://api.binance.com/api/v3"
    
    def __init__(self):
        # Removido margem - usando preço real da corretora
        pass
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Faz uma requisição para a API da Binance."""
        try:
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para Binance: {e}")
            raise
    
    def get_price(self, symbol: str) -> Decimal:
        """
        Obtém o preço atual de um par de negociação na Binance.
        
        Args:
            symbol: Par de negociação (ex: 'BTCBRL', 'BTCUSDT')
            
        Returns:
            Decimal: Preço real da corretora
        """
        try:
            endpoint = "ticker/price"
            params = {"symbol": symbol.upper()}
            data = self._make_request(endpoint, params)
            
            # Retorna o preço real sem margem, formatado para 8 casas decimais
            price = Decimal(str(data['price']))
            return price.quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
            
        except Exception as e:
            logger.error(f"Erro ao obter preço da Binance: {e}")
            raise
    
    def get_btc_price_brl(self) -> Decimal:
        """Obtém o preço real do BTC em BRL."""
        return self.get_price("BTCBRL")
    
    def get_usdt_price_brl(self) -> Decimal:
        """Obtém o preço real do USDT em BRL."""
        return self.get_price("BUSDUSDT")  # Usando BUSD como proxy para BRL
    
    def get_depix_price_brl(self) -> Decimal:
        """
        Obtém o preço do Depix em BRL.
        Como o Depix é uma stablecoin atrelada ao Real, retornamos 1:1 sem margem.
        """
        # Depix é 1:1 com BRL, sem margem
        return Decimal('1.0')

# Instância global para ser importada
binance_api = BinanceAPI()

# Exemplo de uso:
if __name__ == "__main__":
    try:
        print(f"BTC/BRL: {binance_api.get_btc_price_brl()}")
        print(f"USDT/BRL: {binance_api.get_usdt_price_brl()}")
        print(f"Depix/BRL: {binance_api.get_depix_price_brl()}")
    except Exception as e:
        print(f"Erro: {e}")
