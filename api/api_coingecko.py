import os
import requests
from typing import Dict, Optional
from decimal import Decimal, ROUND_DOWN
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        # Margem de 2% acima do preço de mercado
        self.margin = Decimal('1.02')
        # Mapeamento de moedas para IDs da CoinGecko
        self.coin_ids = {
            'BTC': 'bitcoin',
            'USDT': 'tether',
            'BRL': 'brl',
            'DEPIX': 'depix'  # Atualize com o ID correto quando disponível
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Faz uma requisição para a API da CoinGecko."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params or {},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para CoinGecko: {e}")
            raise
    
    def get_price(self, coin: str, vs_currency: str = 'brl') -> Decimal:
        """
        Obtém o preço atual de uma criptomoeda em relação a uma moeda fiduciária.
        
        Args:
            coin: Símbolo da criptomoeda (ex: 'btc', 'usdt')
            vs_currency: Moeda de referência (padrão: 'brl')
            
        Returns:
            Decimal: Preço atual com margem de 2%, arredondado para 2 casas decimais
        """
        try:
            coin_id = self.coin_ids.get(coin.upper())
            if not coin_id:
                raise ValueError(f"Moeda não suportada: {coin}")
                
            endpoint = f"simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": vs_currency.lower(),
                "include_24hr_change": "false"
            }
            
            data = self._make_request(endpoint, params)
            
            if coin_id not in data or vs_currency.lower() not in data[coin_id]:
                raise ValueError(f"Dados de preço não disponíveis para {coin}/{vs_currency}")
            
            # Aplica a margem de 2% e formata para 2 casas decimais
            price = Decimal(str(data[coin_id][vs_currency.lower()])) * self.margin
            return price.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            
        except Exception as e:
            logger.error(f"Erro ao obter preço da CoinGecko: {e}")
            raise
    
    def get_btc_price_brl(self) -> Decimal:
        """Obtém o preço do BTC em BRL com margem de 2%."""
        return self.get_price('BTC', 'BRL')
    
    def get_usdt_price_brl(self) -> Decimal:
        """Obtém o preço do USDT em BRL com margem de 2%."""
        return self.get_price('USDT', 'BRL')
    
    def get_depix_price_brl(self) -> Decimal:
        """
        Obtém o preço do Depix em BRL com margem de 2%.
        """
        return self.get_price('DEPIX', 'BRL')

# Instância global para ser importada
coingecko_api = CoinGeckoAPI()

# Exemplo de uso:
if __name__ == "__main__":
    try:
        print(f"BTC/BRL: {coingecko_api.get_btc_price_brl()}")
        print(f"USDT/BRL: {coingecko_api.get_usdt_price_brl()}")
        print(f"Depix/BRL: {coingecko_api.get_depix_price_brl()}")
    except Exception as e:
        print(f"Erro: {e}")
