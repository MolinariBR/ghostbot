"""
Módulo de fallback para cotação quando a API do backend falhar.
Fornece cotação de emergência usando APIs alternativas ou valores fixos.
"""

import requests
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

# Configuração de logging
logger = logging.getLogger(__name__)

class FallbackCotacaoError(Exception):
    """Exceção para erros na cotação de fallback."""
    pass

class FallbackCotacao:
    """
    Cliente para cotação de fallback quando a API principal falhar.
    Usa múltiplas estratégias para garantir que sempre haja uma cotação disponível.
    """
    
    def __init__(self):
        """Inicializa o cliente de cotação de fallback."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GhostBot-Fallback/1.0',
            'Accept': 'application/json'
        })
    
    def get_cotacao_fallback(self, moeda: str = "bitcoin", vs: str = "brl") -> Dict[str, Any]:
        """
        Obtém cotação usando estratégias de fallback.
        
        Args:
            moeda: Símbolo da moeda (bitcoin, ethereum, etc.)
            vs: Moeda de referência (brl, usd, etc.)
            
        Returns:
            Dicionário com a cotação de fallback
            
        Raises:
            FallbackCotacaoError: Se nenhuma estratégia funcionar
        """
        moeda = moeda.lower()
        vs = vs.lower()
        
        logger.info(f"Tentando cotação de fallback para {moeda.upper()}/{vs.upper()}")
        
        # Estratégia 1: CoinGecko (mais confiável)
        try:
            cotacao = self._get_coingecko_price(moeda, vs)
            if cotacao:
                logger.info(f"Cotação obtida via CoinGecko: {cotacao}")
                return cotacao
        except Exception as e:
            logger.warning(f"CoinGecko falhou: {e}")
        
        # Estratégia 2: Binance P2P
        try:
            cotacao = self._get_binance_p2p_price(moeda, vs)
            if cotacao:
                logger.info(f"Cotação obtida via Binance P2P: {cotacao}")
                return cotacao
        except Exception as e:
            logger.warning(f"Binance P2P falhou: {e}")
        
        # Se ambas falharem, lança exceção
        error_msg = f"Não foi possível obter cotação de fallback para {moeda.upper()}/{vs.upper()}"
        logger.error(error_msg)
        raise FallbackCotacaoError(error_msg)
    
    def _get_coingecko_price(self, moeda: str, vs: str) -> Optional[Dict[str, Any]]:
        """Obtém cotação via CoinGecko."""
        try:
            # Mapeia símbolos para IDs do CoinGecko
            coin_map = {
                'btc': 'bitcoin',
                'bitcoin': 'bitcoin',
                'eth': 'ethereum',
                'ethereum': 'ethereum',
                'ltc': 'litecoin',
                'litecoin': 'litecoin',
                'usdt': 'tether',
                'tether': 'tether'
            }
            
            coin_id = coin_map.get(moeda, moeda)
            vs_currency = vs if vs in ['brl', 'usd', 'eur'] else 'usd'
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if coin_id in data and vs_currency in data[coin_id]:
                price = float(data[coin_id][vs_currency])
                # Aplica spread de 1% para simular margem
                final_price = price * 1.01
                
                return {
                    'price': round(final_price, 2),
                    'source': 'coingecko_fallback',
                    'timestamp': datetime.now().isoformat(),
                    'symbol': moeda,
                    'vs': vs,
                    'raw_price': price,
                    'spread': 1.0
                }
        except Exception as e:
            logger.error(f"Erro ao obter cotação CoinGecko: {e}")
        
        return None
    
    def _get_binance_p2p_price(self, moeda: str, vs: str) -> Optional[Dict[str, Any]]:
        """Obtém cotação via Binance P2P."""
        try:
            url = "https://p2p.binance.com/bapi/c2c/v1/friendly/c2c/adv/search"
            payload = {
                "page": 1,
                "rows": 1,
                "payTypes": [],
                "asset": moeda.upper(),
                "tradeType": "SELL",
                "fiat": vs.upper(),
                "publisherType": "merchant"
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                price = float(data['data'][0]['adv']['price'])
                # Aplica spread de 1.5% para simular margem
                final_price = price * 1.015
                
                return {
                    'price': round(final_price, 2),
                    'source': 'binance_p2p_fallback',
                    'timestamp': datetime.now().isoformat(),
                    'symbol': moeda,
                    'vs': vs,
                    'raw_price': price,
                    'spread': 1.5
                }
        except Exception as e:
            logger.error(f"Erro ao obter cotação Binance P2P: {e}")
        
        return None

# Instância global
fallback_cotacao = FallbackCotacao()

def get_cotacao_fallback_simples(moeda: str = "bitcoin", vs: str = "brl") -> Dict[str, Any]:
    """
    Função simples para obter cotação de fallback.
    
    Args:
        moeda: Símbolo da moeda
        vs: Moeda de referência
        
    Returns:
        Dicionário com a cotação
    """
    return fallback_cotacao.get_cotacao_fallback(moeda, vs)

# Exemplo de uso
if __name__ == "__main__":
    import sys
    
    # Configura logging para exibir no console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    try:
        # Testa cotação de fallback
        cotacao = get_cotacao_fallback_simples("bitcoin", "brl")
        print(f"Cotação de fallback: {json.dumps(cotacao, indent=2)}")
        
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1) 