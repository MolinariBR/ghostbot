"""
Testes unitários para a classe CoinGeckoAPI.
"""
import pytest
import requests
from decimal import Decimal
from unittest.mock import Mock, patch
from api.api_coingecko import CoinGeckoAPI, coingecko_api


class TestCoinGeckoAPI:
    """Testes para a classe CoinGeckoAPI."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.api = CoinGeckoAPI()
    
    def test_init(self):
        """Testa inicialização da classe."""
        assert self.api.BASE_URL == "https://api.coingecko.com/api/v3"
        # Margem removida - agora usa preço real
        assert self.api.coin_ids['BTC'] == 'bitcoin'
        assert self.api.coin_ids['USDT'] == 'tether'
        assert self.api.coin_ids['BRL'] == 'brl'
        assert self.api.coin_ids['DEPIX'] == 'depix'
    
    @patch('api.api_coingecko.requests.get')
    def test_make_request_success(self, mock_get):
        """Testa requisição bem-sucedida."""
        mock_response = Mock()
        mock_response.json.return_value = {'bitcoin': {'brl': 300000.0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.api._make_request('simple/price', {'ids': 'bitcoin'})
        
        mock_get.assert_called_once_with(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin'},
            timeout=10
        )
        assert result == {'bitcoin': {'brl': 300000.0}}
    
    @patch('api.api_coingecko.requests.get')
    def test_make_request_no_params(self, mock_get):
        """Testa requisição sem parâmetros."""
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'ok'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.api._make_request('ping')
        
        mock_get.assert_called_once_with(
            'https://api.coingecko.com/api/v3/ping',
            params={},
            timeout=10
        )
        assert result == {'status': 'ok'}
    
    @patch('api.api_coingecko.requests.get')
    def test_make_request_http_error(self, mock_get):
        """Testa erro HTTP na requisição."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('404 Not Found')
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            self.api._make_request('invalid/endpoint')
    
    @patch('api.api_coingecko.requests.get')
    def test_make_request_timeout_error(self, mock_get):
        """Testa erro de timeout na requisição."""
        mock_get.side_effect = requests.exceptions.Timeout('Timeout')
        
        with pytest.raises(requests.exceptions.Timeout):
            self.api._make_request('simple/price')
    
    @patch('api.api_coingecko.requests.get')
    def test_get_price_success(self, mock_get):
        """Testa obtenção bem-sucedida de preço."""
        mock_response = Mock()
        mock_response.json.return_value = {'bitcoin': {'brl': 300000.0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('BTC', 'BRL')
        
        # Verifica se o preço real foi retornado (sem margem)
        expected_price = Decimal('300000.00')
        assert price == expected_price
        
        mock_get.assert_called_once_with(
            'https://api.coingecko.com/api/v3/simple/price',
            params={
                'ids': 'bitcoin',
                'vs_currencies': 'brl',
                'include_24hr_change': 'false'
            },
            timeout=10
        )
    
    @patch('api.api_coingecko.requests.get')
    def test_get_price_default_currency(self, mock_get):
        """Testa obtenção de preço com moeda padrão (BRL)."""
        mock_response = Mock()
        mock_response.json.return_value = {'bitcoin': {'brl': 300000.0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('BTC')
        
        # Verifica se usou BRL como padrão
        mock_get.assert_called_once_with(
            'https://api.coingecko.com/api/v3/simple/price',
            params={
                'ids': 'bitcoin',
                'vs_currencies': 'brl',
                'include_24hr_change': 'false'
            },
            timeout=10
        )
        assert price == Decimal('300000.00')
    
    @patch('api.api_coingecko.requests.get')
    def test_get_price_lowercase_inputs(self, mock_get):
        """Testa obtenção de preço com entradas em minúsculo."""
        mock_response = Mock()
        mock_response.json.return_value = {'tether': {'usd': 1.0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('usdt', 'USD')
        
        # Verifica se o mapeamento funcionou
        mock_get.assert_called_once_with(
            'https://api.coingecko.com/api/v3/simple/price',
            params={
                'ids': 'tether',
                'vs_currencies': 'usd',
                'include_24hr_change': 'false'
            },
            timeout=10
        )
        assert price == Decimal('1.00')
    
    def test_get_price_unsupported_coin(self):
        """Testa erro para moeda não suportada."""
        with pytest.raises(ValueError) as exc_info:
            self.api.get_price('UNSUPPORTED')
        
        assert "Moeda não suportada: UNSUPPORTED" in str(exc_info.value)
    
    @patch('api.api_coingecko.requests.get')
    def test_get_price_missing_coin_data(self, mock_get):
        """Testa erro quando dados da moeda não estão disponíveis."""
        mock_response = Mock()
        mock_response.json.return_value = {}  # Dados vazios
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            self.api.get_price('BTC', 'BRL')
        
        assert "Dados de preço não disponíveis para BTC/BRL" in str(exc_info.value)
    
    @patch('api.api_coingecko.requests.get')
    def test_get_price_missing_currency_data(self, mock_get):
        """Testa erro quando dados da moeda de referência não estão disponíveis."""
        mock_response = Mock()
        mock_response.json.return_value = {'bitcoin': {'usd': 45000.0}}  # Sem BRL
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            self.api.get_price('BTC', 'BRL')
        
        assert "Dados de preço não disponíveis para BTC/BRL" in str(exc_info.value)
    
    @patch('api.api_coingecko.requests.get')
    def test_get_price_precision(self, mock_get):
        """Testa precisão do preço retornado."""
        mock_response = Mock()
        mock_response.json.return_value = {'bitcoin': {'brl': 123.456789}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('BTC', 'BRL')
        
        # Verifica se o preço tem exatamente 2 casas decimais
        price_str = str(price)
        decimal_places = len(price_str.split('.')[1])
        assert decimal_places == 2
    
    @patch.object(CoinGeckoAPI, 'get_price')
    def test_get_btc_price_brl(self, mock_get_price):
        """Testa obtenção do preço do BTC em BRL."""
        mock_get_price.return_value = Decimal('306000.00')
        
        price = self.api.get_btc_price_brl()
        
        mock_get_price.assert_called_once_with('BTC', 'BRL')
        assert price == Decimal('306000.00')
    
    @patch.object(CoinGeckoAPI, 'get_price')
    def test_get_usdt_price_brl(self, mock_get_price):
        """Testa obtenção do preço do USDT em BRL."""
        mock_get_price.return_value = Decimal('5.10')
        
        price = self.api.get_usdt_price_brl()
        
        mock_get_price.assert_called_once_with('USDT', 'BRL')
        assert price == Decimal('5.10')
    
    @patch.object(CoinGeckoAPI, 'get_price')
    def test_get_depix_price_brl(self, mock_get_price):
        """Testa obtenção do preço do Depix em BRL."""
        mock_get_price.return_value = Decimal('1.02')
        
        price = self.api.get_depix_price_brl()
        
        mock_get_price.assert_called_once_with('DEPIX', 'BRL')
        assert price == Decimal('1.02')


class TestCoinGeckoAPILogging:
    """Testes para verificar o logging da classe CoinGeckoAPI."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.api = CoinGeckoAPI()
    
    @patch('api.api_coingecko.logger')
    @patch('api.api_coingecko.requests.get')
    def test_make_request_logs_error(self, mock_get, mock_logger):
        """Testa se erros são logados corretamente."""
        mock_get.side_effect = requests.exceptions.ConnectionError('Connection failed')
        
        with pytest.raises(requests.exceptions.ConnectionError):
            self.api._make_request('simple/price')
        
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Erro na requisição para CoinGecko" in error_call
    
    @patch('api.api_coingecko.logger')
    @patch.object(CoinGeckoAPI, '_make_request')
    def test_get_price_logs_error(self, mock_make_request, mock_logger):
        """Testa se erros na obtenção de preço são logados."""
        mock_make_request.side_effect = Exception('API Error')
        
        with pytest.raises(Exception):
            self.api.get_price('BTC')
        
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Erro ao obter preço da CoinGecko" in error_call


class TestCoinGeckoAPIGlobalInstance:
    """Testes para a instância global."""
    
    def test_global_instance_exists(self):
        """Testa se a instância global existe."""
        assert coingecko_api is not None
        assert isinstance(coingecko_api, CoinGeckoAPI)
    
    def test_global_instance_properties(self):
        """Testa propriedades da instância global."""
        assert coingecko_api.BASE_URL == "https://api.coingecko.com/api/v3"
        # Margem removida - agora usa preço real


class TestCoinGeckoAPIEdgeCases:
    """Testes para casos extremos."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.api = CoinGeckoAPI()
    
    @patch('api.api_coingecko.requests.get')
    def test_get_price_zero_price(self, mock_get):
        """Testa comportamento com preço zero."""
        mock_response = Mock()
        mock_response.json.return_value = {'bitcoin': {'brl': 0.0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('BTC', 'BRL')
        
        # Mesmo com preço zero, a margem deve ser aplicada
        expected_price = Decimal('0.00')
        assert price == expected_price
    
    @patch('api.api_coingecko.requests.get')
    def test_get_price_very_small_price(self, mock_get):
        """Testa comportamento com preço muito pequeno."""
        mock_response = Mock()
        mock_response.json.return_value = {'bitcoin': {'brl': 0.1}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = self.api.get_price('BTC', 'BRL')
        
        # Verifica se a precisão é mantida (0.1 * 1.02 = 0.102, arredondado para 0.10)
        assert isinstance(price, Decimal)
        assert price == Decimal('0.10')
    
    @patch('api.api_coingecko.requests.get')
    def test_get_price_invalid_json_response(self, mock_get):
        """Testa comportamento com resposta JSON inválida."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError):
            self.api.get_price('BTC')
    
    def test_coin_ids_mapping(self):
        """Testa mapeamento de IDs das moedas."""
        assert self.api.coin_ids['BTC'] == 'bitcoin'
        assert self.api.coin_ids['USDT'] == 'tether'
        assert self.api.coin_ids['BRL'] == 'brl'
        assert self.api.coin_ids['DEPIX'] == 'depix'
