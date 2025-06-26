"""
Testes unitários para a classe BinanceAPI.
"""
import pytest
import requests
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from api.api_binance import BinanceAPI, binance_api


class TestBinanceAPI:
    """Testes para a classe BinanceAPI."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.api = BinanceAPI()
    
    def test_init(self):
        """Testa inicialização da classe."""
        assert self.api.BASE_URL == "https://api.binance.com/api/v3"
        # Margem removida - agora usa preço real
    
    @patch('api.api_binance.requests.get')
    def test_make_request_success(self, mock_get):
        """Testa requisição bem-sucedida."""
        mock_response = Mock()
        mock_response.json.return_value = {'price': '50000.00'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.api._make_request('ticker/price', {'symbol': 'BTCBRL'})
        
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/ticker/price',
            params={'symbol': 'BTCBRL'}
        )
        assert result == {'price': '50000.00'}
    
    @patch('api.api_binance.requests.get')
    def test_make_request_no_params(self, mock_get):
        """Testa requisição sem parâmetros."""
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'ok'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.api._make_request('time')
        
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/time',
            params={}
        )
        assert result == {'status': 'ok'}
    
    @patch('api.api_binance.requests.get')
    def test_make_request_http_error(self, mock_get):
        """Testa erro HTTP na requisição."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('404 Not Found')
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            self.api._make_request('invalid/endpoint')
    
    @patch('api.api_binance.requests.get')
    def test_make_request_connection_error(self, mock_get):
        """Testa erro de conexão na requisição."""
        mock_get.side_effect = requests.exceptions.ConnectionError('Connection failed')
        
        with pytest.raises(requests.exceptions.ConnectionError):
            self.api._make_request('ticker/price')
    
    @patch('api.api_binance.requests.get')
    def test_get_price_success(self, mock_get):
        """Testa obtenção bem-sucedida de preço."""
        mock_response = Mock()
        mock_response.json.return_value = {'price': '300000.00'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('BTCBRL')
        
        # Verifica se o preço real foi retornado (sem margem)
        expected_price = Decimal('300000.00000000')
        assert price == expected_price
        
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/ticker/price',
            params={'symbol': 'BTCBRL'}
        )
    
    @patch('api.api_binance.requests.get')
    def test_get_price_lowercase_symbol(self, mock_get):
        """Testa obtenção de preço com símbolo em minúsculo."""
        mock_response = Mock()
        mock_response.json.return_value = {'price': '100.50'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('btcbrl')
        
        # Verifica se o símbolo foi convertido para maiúsculo
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/ticker/price',
            params={'symbol': 'BTCBRL'}
        )
        
        # Verifica o preço real (sem margem)
        expected_price = Decimal('100.50000000')
        assert price == expected_price
    
    @patch('api.api_binance.requests.get')
    def test_get_price_precision(self, mock_get):
        """Testa precisão do preço retornado."""
        mock_response = Mock()
        mock_response.json.return_value = {'price': '1.123456789'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('TESTCOIN')
        
        # Verifica se o preço tem exatamente 8 casas decimais
        price_str = str(price)
        decimal_places = len(price_str.split('.')[1])
        assert decimal_places == 8
    
    @patch('api.api_binance.requests.get')
    def test_get_price_error_handling(self, mock_get):
        """Testa tratamento de erro na obtenção de preço."""
        mock_get.side_effect = requests.exceptions.RequestException('API Error')
        
        with pytest.raises(requests.exceptions.RequestException):
            self.api.get_price('BTCBRL')
    
    @patch.object(BinanceAPI, 'get_price')
    def test_get_btc_price_brl(self, mock_get_price):
        """Testa obtenção do preço do BTC em BRL."""
        mock_get_price.return_value = Decimal('306000.00000000')
        
        price = self.api.get_btc_price_brl()
        
        mock_get_price.assert_called_once_with("BTCBRL")
        assert price == Decimal('306000.00000000')
    
    @patch.object(BinanceAPI, 'get_price')
    def test_get_usdt_price_brl(self, mock_get_price):
        """Testa obtenção do preço do USDT em BRL."""
        mock_get_price.return_value = Decimal('5.10000000')
        
        price = self.api.get_usdt_price_brl()
        
        mock_get_price.assert_called_once_with("BUSDUSDT")
        assert price == Decimal('5.10000000')
    
    def test_get_depix_price_brl(self):
        """Testa obtenção do preço do Depix em BRL."""
        price = self.api.get_depix_price_brl()
        
        # Depix é 1:1 com BRL, sem margem
        expected_price = Decimal('1.0')
        assert price == expected_price


class TestBinanceAPILogging:
    """Testes para verificar o logging da classe BinanceAPI."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.api = BinanceAPI()
    
    @patch('api.api_binance.logger')
    @patch('api.api_binance.requests.get')
    def test_make_request_logs_error(self, mock_get, mock_logger):
        """Testa se erros são logados corretamente."""
        mock_get.side_effect = requests.exceptions.ConnectionError('Connection failed')
        
        with pytest.raises(requests.exceptions.ConnectionError):
            self.api._make_request('ticker/price')
        
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Erro na requisição para Binance" in error_call
    
    @patch('api.api_binance.logger')
    @patch.object(BinanceAPI, '_make_request')
    def test_get_price_logs_error(self, mock_make_request, mock_logger):
        """Testa se erros na obtenção de preço são logados."""
        mock_make_request.side_effect = Exception('API Error')
        
        with pytest.raises(Exception):
            self.api.get_price('BTCBRL')
        
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Erro ao obter preço da Binance" in error_call


class TestBinanceAPIGlobalInstance:
    """Testes para a instância global."""
    
    def test_global_instance_exists(self):
        """Testa se a instância global existe."""
        assert binance_api is not None
        assert isinstance(binance_api, BinanceAPI)
    
    def test_global_instance_properties(self):
        """Testa propriedades da instância global."""
        assert binance_api.BASE_URL == "https://api.binance.com/api/v3"
        # Margem removida - agora usa preço real


class TestBinanceAPIEdgeCases:
    """Testes para casos extremos."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.api = BinanceAPI()
    
    @patch('api.api_binance.requests.get')
    def test_get_price_zero_price(self, mock_get):
        """Testa comportamento com preço zero."""
        mock_response = Mock()
        mock_response.json.return_value = {'price': '0.00000000'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('TESTCOIN')
        
        # Mesmo com preço zero, a margem deve ser aplicada
        expected_price = Decimal('0.00000000')
        assert price == expected_price
    
    @patch('api.api_binance.requests.get')
    def test_get_price_very_small_price(self, mock_get):
        """Testa comportamento com preço muito pequeno."""
        mock_response = Mock()
        mock_response.json.return_value = {'price': '0.00000001'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('TESTCOIN')
        
        # Verifica se a precisão é mantida
        assert isinstance(price, Decimal)
        # Verifica se o valor é positivo e muito pequeno
        assert price > 0
        assert price < Decimal('0.00000002')
    
    @patch('api.api_binance.requests.get')
    def test_get_price_invalid_json_response(self, mock_get):
        """Testa comportamento com resposta JSON inválida."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError):
            self.api.get_price('BTCBRL')
    
    @patch('api.api_binance.requests.get')
    def test_get_price_missing_price_field(self, mock_get):
        """Testa comportamento quando campo 'price' está ausente."""
        mock_response = Mock()
        mock_response.json.return_value = {'symbol': 'BTCBRL', 'status': 'ok'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(KeyError):
            self.api.get_price('BTCBRL')
