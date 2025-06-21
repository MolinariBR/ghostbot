"""
Testes unitários para o módulo api_coingecko.py
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from api.api_coingecko import CoinGeckoAPI

class TestCoinGeckoAPI:
    """Testes para a classe CoinGeckoAPI."""
    
    @pytest.fixture
    def mock_requests(self):
        """Fixture para mockar as requisições HTTP."""
        with patch('api.api_coingecko.requests') as mock_requests:
            yield mock_requests

    def test_init(self):
        """Testa a inicialização da classe CoinGeckoAPI."""
        api = CoinGeckoAPI()
        assert api.margin == Decimal('1.02')
        assert api.coin_ids == {
            'BTC': 'bitcoin',
            'USDT': 'tether',
            'BRL': 'brl',
            'DEPIX': 'depix'
        }
    
    def test_make_request_success(self, mock_requests):
        """Testa uma requisição bem-sucedida."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.json.return_value = {'bitcoin': {'brl': 300000.00}}
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response
        
        # Executa o teste
        api = CoinGeckoAPI()
        result = api._make_request('simple/price', {'ids': 'bitcoin', 'vs_currencies': 'brl'})
        
        # Verifica os resultados
        assert result == {'bitcoin': {'brl': 300000.00}}
        mock_requests.get.assert_called_once_with(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin', 'vs_currencies': 'brl'},
            timeout=10
        )
    
    @patch('api.api_coingecko.CoinGeckoAPI._make_request')
    def test_get_price_btc_brl(self, mock_make_request):
        """Testa a obtenção do preço do BTC em BRL."""
        # Configura o mock
        mock_make_request.return_value = {'bitcoin': {'brl': 300000.00}}
        
        # Executa o teste
        api = CoinGeckoAPI()
        price = api.get_price('btc')
        
        # Verifica os resultados
        assert price == Decimal('306000.00')  # 300000 * 1.02
        mock_make_request.assert_called_once_with(
            'simple/price',
            {'ids': 'bitcoin', 'vs_currencies': 'brl', 'precision': 'full'}
        )
    
    @patch('api.api_coingecko.CoinGeckoAPI._make_request')
    def test_get_price_usdt_brl(self, mock_make_request):
        """Testa a obtenção do preço do USDT em BRL."""
        # Configura o mock
        mock_make_request.return_value = {'tether': {'brl': 5.20}}
        
        # Executa o teste
        api = CoinGeckoAPI()
        price = api.get_price('usdt')
        
        # Verifica os resultados
        assert price == Decimal('5.304')  # 5.20 * 1.02
        mock_make_request.assert_called_once_with(
            'simple/price',
            {'ids': 'tether', 'vs_currencies': 'brl', 'precision': 'full'}
        )
    
    @patch('api.api_coingecko.CoinGeckoAPI._make_request')
    def test_get_price_coin_not_found(self, mock_make_request):
        """Testa o comportamento quando uma moeda não é encontrada."""
        # Configura o mock para simular moeda não encontrada
        mock_make_request.return_value = {}
        
        # Executa o teste e verifica a exceção
        api = CoinGeckoAPI()
        with pytest.raises(ValueError, match="Moeda não encontrada: INVALID"):
            api.get_price('invalid')
    
    @patch('api.api_coingecko.CoinGeckoAPI._make_request')
    def test_get_btc_price_brl(self, mock_make_request):
        """Testa o método get_btc_price_brl."""
        # Configura o mock
        mock_make_request.return_value = {'bitcoin': {'brl': 300000.00}}
        
        # Executa o teste
        api = CoinGeckoAPI()
        price = api.get_btc_price_brl()
        
        # Verifica os resultados
        assert price == Decimal('306000.00')  # 300000 * 1.02
        mock_make_request.assert_called_once()
    
    @patch('api.api_coingecko.CoinGeckoAPI._make_request')
    def test_get_usdt_price_brl(self, mock_make_request):
        """Testa o método get_usdt_price_brl."""
        # Configura o mock
        mock_make_request.return_value = {'tether': {'brl': 5.20}}
        
        # Executa o teste
        api = CoinGeckoAPI()
        price = api.get_usdt_price_brl()
        
        # Verifica os resultados
        assert price == Decimal('5.304')  # 5.20 * 1.02
        mock_make_request.assert_called_once()
    
    @patch('api.api_coingecko.CoinGeckoAPI._make_request')
    def test_get_depix_price_brl(self, mock_make_request):
        """Testa o método get_depix_price_brl."""
        # Configura o mock
        mock_make_request.return_value = {'depix': {'brl': 0.05}}
        
        # Executa o teste
        api = CoinGeckoAPI()
        price = api.get_depix_price_brl()
        
        # Verifica os resultados
        assert price == Decimal('0.051')  # 0.05 * 1.02
        mock_make_request.assert_called_once()
