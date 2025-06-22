"""
Módulo de fachada para acesso unificado às APIs de cotações.

Este módulo fornece uma interface única para acessar diferentes provedores de cotações,
permitindo alternar facilmente entre eles e implementar lógica de fallback.
"""

from decimal import Decimal
from typing import Optional
import logging
from . import binance_api, coingecko_api

# Configuração do logger
logger = logging.getLogger(__name__)

class CotacaoAPI:
    """Classe de fachada para acesso unificado às APIs de cotações."""
    
    def __init__(self, provider: str = 'binance'):
        """
        Inicializa a API de cotações com o provedor especificado.
        
        Args:
            provider: Provedor de cotações ('binance' ou 'coingecko')
        """
        self.provider = provider.lower()
        self.providers = {
            'binance': binance_api,
            'coingecko': coingecko_api
        }
        
        if self.provider not in self.providers:
            logger.warning(f"Provedor {provider} não encontrado. Usando Binance como padrão.")
            self.provider = 'binance'
    
    def _get_provider(self):
        """Retorna a instância do provedor atual."""
        return self.providers[self.provider]
    
    def get_btc_price_brl(self) -> Decimal:
        """Obtém o preço do BTC em BRL com margem de 2%."""
        try:
            return self._get_provider().get_btc_price_brl()
        except Exception as e:
            logger.error(f"Erro ao obter preço do BTC: {e}")
            # Tenta o outro provedor em caso de falha
            try:
                if self.provider == 'binance':
                    logger.info("Tentando obter cotação do BTC na CoinGecko...")
                    return coingecko_api.get_btc_price_brl()
                else:
                    logger.info("Tentando obter cotação do BTC na Binance...")
                    return binance_api.get_btc_price_brl()
            except Exception as e2:
                logger.error(f"Falha em ambos os provedores: {e2}")
                raise Exception("Falha ao obter cotação do BTC em todos os provedores.")
    
    def get_usdt_price_brl(self) -> Decimal:
        """Obtém o preço do USDT em BRL com margem de 2%."""
        try:
            return self._get_provider().get_usdt_price_brl()
        except Exception as e:
            logger.error(f"Erro ao obter preço do USDT: {e}")
            # Tenta o outro provedor em caso de falha
            if self.provider == 'binance':
                logger.info("Tentando obter cotação do USDT na CoinGecko...")
                return coingecko_api.get_usdt_price_brl()
            else:
                logger.info("Tentando obter cotação do USDT na Binance...")
                return binance_api.get_usdt_price_brl()
    
    def get_depix_price_brl(self) -> Decimal:
        """
        Obtém o preço do Depix em BRL.
        Como o Depix é uma stablecoin atrelada ao Real, retornamos 1:1 com margem de 2%.
        """
        # Para o Depix, não precisamos consultar a API, pois é 1:1 com BRL
        # Apenas aplicamos a margem de 2%
        return Decimal('1.0') * Decimal('1.02')  # 1.0 * 1.02 = 1.02

# Instância global para ser importada
cotacao_api = CotacaoAPI()  # Usa Binance como padrão

# Funções de conveniência
get_btc_price_brl = cotacao_api.get_btc_price_brl
get_usdt_price_brl = cotacao_api.get_usdt_price_brl
get_depix_price_brl = cotacao_api.get_depix_price_brl

# Exemplo de uso:
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("=== Teste de Cotações ===")
    print(f"BTC/BRL: {get_btc_price_brl()}")
    print(f"USDT/BRL: {get_usdt_price_brl()}")
    print(f"Depix/BRL: {get_depix_price_brl()}")
    
    # Teste com fallback
    print("\n=== Teste de Fallback ===")
    cotacao_fallback = CotacaoAPI('invalido')  # Força fallback
    print(f"BTC/BRL (fallback): {cotacao_fallback.get_btc_price_brl()}")
