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
        with patch('api.binance_api.BinanceAPI') as mock_binance, \
             patch('api.coingecko_api.CoinGeckoAPI') as mock_coingecko:
            
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
        assert price == Decimal('300000.00')
        
        # Verifica se o método correto foi chamado
        mock_apis[0].return_value.get_btc_price_brl.assert_called_once()
        mock_apis[1].return_value.get_btc_price_brl.assert_not_called()
    
    def test_get_btc_price_brl_fallback(self, mock_apis):
        """Testa o fallback para CoinGecko quando Binance falha."""
        # Configura o mock para falhar na primeira chamada
        mock_apis[0].return_value.get_btc_price_brl.side_effect = Exception("API error")
        
        cotacao = CotacaoAPI()
        price = cotacao.get_btc_price_brl()
        
        # Deve retornar o valor do CoinGecko (fallback)
        assert price == Decimal('310000.00')
        
        # Verifica se ambos os métodos foram chamados
        mock_apis[0].return_value.get_btc_price_brl.assert_called_once()
        mock_apis[1].return_value.get_btc_price_brl.assert_called_once()
    
    def test_get_usdt_price_brl(self, mock_apis):
        """Testa a obtenção do preço do USDT."""
        cotacao = CotacaoAPI()
        price = cotacao.get_usdt_price_brl()
        assert price == Decimal('5.50')
    
    def test_get_depix_price_brl(self, mock_apis):
        """Testa a obtenção do preço do Depix."""
        cotacao = CotacaoAPI()
        price = cotacao.get_depix_price_brl()
        assert price == Decimal('0.05')
    
    def test_all_apis_fail(self, mock_apis):
        """Testa o comportamento quando todas as APIs falham."""
        # Configura todos os métodos para falharem
        mock_apis[0].return_value.get_btc_price_brl.side_effect = Exception("Binance error")
        mock_apis[1].return_value.get_btc_price_brl.side_effect = Exception("CoinGecko error")
        
        cotacao = CotacaoAPI()
        
        # Deve levantar uma exceção
        with pytest.raises(Exception, match=".*Erro ao obter cotação.*"):
            cotacao.get_btc_price_brl()
