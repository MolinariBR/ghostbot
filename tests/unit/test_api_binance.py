"""
Testes unitários para o módulo api_binance.py
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from api.api_binance import BinanceAPI

class TestBinanceAPI:
    """Testes para a classe BinanceAPI."""
    
    @pytest.fixture
    def mock_requests(self):
        """Fixture para mockar as requisições HTTP."""
        with patch('api.api_binance.requests') as mock_requests:
            yield mock_requests

    def test_init(self):
        """Testa a inicialização da classe BinanceAPI."""
        api = BinanceAPI()
        assert api.margin == Decimal('1.02')
    
    def test_make_request_success(self, mock_requests):
        """Testa uma requisição bem-sucedida."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.json.return_value = {'price': '300000.00'}
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response
        
        # Executa o teste
        api = BinanceAPI()
        result = api._make_request('ticker/price', {'symbol': 'BTCBRL'})
        
        # Verifica os resultados
        assert result == {'price': '300000.00'}
        mock_requests.get.assert_called_once_with(
            'https://api.binance.com/api/v3/ticker/price',
            params={'symbol': 'BTCBRL'}
        )
    
    def test_make_request_error(self, mock_requests):
        """Testa o tratamento de erro em uma requisição."""
        # Configura o mock para simular um erro
        mock_requests.get.side_effect = Exception("Erro de conexão")
        
        # Executa o teste e verifica a exceção
        api = BinanceAPI()
        with pytest.raises(Exception, match="Erro na requisição para Binance"):
            api._make_request('ticker/price')
    
    @patch('api.api_binance.BinanceAPI._make_request')
    def test_get_price(self, mock_make_request):
        """Testa a obtenção de preço com margem."""
        # Configura o mock
        mock_make_request.return_value = {'price': '300000.00'}
        
        # Executa o teste
        api = BinanceAPI()
        price = api.get_price('BTCBRL')
        
        # Verifica os resultados
        assert price == Decimal('306000.00')  # 300000 * 1.02
        mock_make_request.assert_called_once_with(
            'ticker/price',
            {'symbol': 'BTCBRL'}
        )
    
    @patch('api.api_binance.BinanceAPI.get_price')
    def test_get_btc_price_brl(self, mock_get_price):
        """Testa a obtenção do preço do BTC em BRL."""
        # Configura o mock
        mock_get_price.return_value = Decimal('306000.00')
        
        # Executa o teste
        api = BinanceAPI()
        price = api.get_btc_price_brl()
        
        # Verifica os resultados
        assert price == Decimal('306000.00')
        mock_get_price.assert_called_once_with('BTCBRL')
    
    @patch('api.api_binance.BinanceAPI.get_price')
    def test_get_usdt_price_brl(self, mock_get_price):
        """Testa a obtenção do preço do USDT em BRL."""
        # Configura o mock
        mock_get_price.return_value = Decimal('5.50')
        
        # Executa o teste
        api = BinanceAPI()
        price = api.get_usdt_price_brl()
        
        # Verifica os resultados
        assert price == Decimal('5.50')
        mock_get_price.assert_called_once_with('BUSDUSDT')
    
    @patch('api.api_binance.BinanceAPI.get_price')
    def test_get_depix_price_brl(self, mock_get_price):
        """Testa a obtenção do preço do Depix em BRL."""
        # Configura o mock para retornar preço em USDT
        mock_get_price.return_value = Decimal('0.10')
        
        # Executa o teste
        api = BinanceAPI()
        price = api.get_depix_price_brl()
        
        # Verifica os resultados
        assert price == Decimal('0.10')
        assert mock_get_price.call_count == 2  # Deve chamar duas vezes (USDT e BUSD)
    
    @patch('api.api_binance.BinanceAPI._make_request')
    def test_get_price_with_rounding(self, mock_make_request):
        """Testa o arredondamento correto do preço."""
        # Preço com mais de 8 casas decimais
        mock_make_request.return_value = {'price': '0.123456789'}
        
        # Executa o teste
        api = BinanceAPI()
        price = api.get_price('DEPIXBRL')
        
        # Deve arredondar para 8 casas decimais
        assert price == Decimal('0.12592692')  # 0.123456789 * 1.02 = 0.12592592478 -> 0.12592692
