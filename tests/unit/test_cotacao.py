"""
Testes unitários para o módulo cotacao.py
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from api.cotacao import CotacaoAPI

class TestCotacaoAPI:
    """Testes para a classe CotacaoAPI."""
    
    @pytest.fixture
    def mock_apis(self):
        """Fixture para mockar as APIs de cotação."""
        with patch('api.api_binance.BinanceAPI') as mock_binance, \
             patch('api.api_coingecko.CoinGeckoAPI') as mock_coingecko:
            
            # Configura os mocks
            mock_binance.return_value.get_btc_price_brl.return_value = Decimal('300000.00')
            mock_binance.return_value.get_usdt_price_brl.return_value = Decimal('5.50')
            mock_binance.return_value.get_depix_price_brl.return_value = Decimal('0.05')
            
            mock_coingecko.return_value.get_btc_price_brl.return_value = Decimal('310000.00')
            mock_coingecko.return_value.get_usdt_price_brl.return_value = Decimal('5.40')
            mock_coingecko.return_value.get_depix_price_brl.return_value = Decimal('0.06')
            
            yield mock_binance, mock_coingecko

    def test_get_btc_price_brl_primary(self, mock_apis):
        """Testa a obtenção do preço do BTC via Binance."""
        cotacao = CotacaoAPI()
        price = cotacao.get_btc_price_brl()
        assert isinstance(price, Decimal)
        assert price > 0

    def test_get_btc_price_brl_fallback(self, mock_apis):
        """Testa o fallback para CoinGecko quando Binance falha."""
        # Configura o mock para falhar na primeira chamada
        mock_apis[0].return_value.get_btc_price_brl.side_effect = Exception("API error")
        cotacao = CotacaoAPI()
        price = cotacao.get_btc_price_brl()
        assert isinstance(price, Decimal)
        assert price > 0
        
    def test_get_usdt_price_brl(self, mock_apis):
        """Testa a obtenção do preço do USDT."""
        cotacao = CotacaoAPI()
        price = cotacao.get_usdt_price_brl()
        assert price == Decimal('1.02030600')
    
    def test_get_depix_price_brl(self, mock_apis):
        """Testa a obtenção do preço do Depix."""
        cotacao = CotacaoAPI()
        price = cotacao.get_depix_price_brl()
        assert price == Decimal('1.020')
    
    @patch('api.cotacao.binance_api.get_btc_price_brl', side_effect=Exception("Binance error"))
    @patch('api.cotacao.coingecko_api.get_btc_price_brl', side_effect=Exception("CoinGecko error"))
    def test_all_apis_fail(self, mock_coingecko, mock_binance):
        """Testa o comportamento quando todas as APIs falham."""
        cotacao = CotacaoAPI()
        
        # Deve levantar uma exceção
        with pytest.raises(Exception):
            cotacao.get_btc_price_brl()
