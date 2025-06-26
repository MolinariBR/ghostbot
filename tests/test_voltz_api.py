"""
Testes unitários para a classe VoltzAPI.
"""
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from api.voltz import VoltzAPI


class TestVoltzAPI:
    """Testes para a classe VoltzAPI."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.voltz_api = VoltzAPI('https://test.example.com/voltz')
    
    def test_init_default_url(self):
        """Testa inicialização com URL padrão."""
        api = VoltzAPI()
        assert api.backend_url == 'https://ghostp2p.squareweb.app/voltz'
        assert api.timeout == 30
    
    def test_init_custom_url(self):
        """Testa inicialização com URL customizada."""
        custom_url = 'https://custom.backend.com/voltz/'
        api = VoltzAPI(custom_url)
        assert api.backend_url == 'https://custom.backend.com/voltz'  # Remove trailing slash
        assert api.timeout == 30
    
    @patch('api.voltz.requests.post')
    def test_create_withdraw_link_success(self, mock_post):
        """Testa criação bem-sucedida de link de saque."""
        # Mock da resposta
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 'withdraw_123',
            'lnurl': 'LNURL1DP68GURN8GHJ7EM9W3SKC...',
            'qr_code_url': 'https://api.qrserver.com/v1/create-qr-code/?data=LNURL...'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Teste
        result = self.voltz_api.create_withdraw_link(1000, 'Teste saque')
        
        # Verificações
        mock_post.assert_called_once_with(
            'https://test.example.com/voltz/create_withdraw.php',
            json={'amount_sats': 1000, 'description': 'Teste saque'},
            timeout=30
        )
        assert result['id'] == 'withdraw_123'
        assert 'lnurl' in result
        assert 'qr_code_url' in result
    
    @patch('api.voltz.requests.post')
    def test_create_withdraw_link_default_description(self, mock_post):
        """Testa criação de link de saque com descrição padrão."""
        mock_response = Mock()
        mock_response.json.return_value = {'id': 'test', 'lnurl': 'test', 'qr_code_url': 'test'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        self.voltz_api.create_withdraw_link(500)
        
        mock_post.assert_called_once_with(
            'https://test.example.com/voltz/create_withdraw.php',
            json={'amount_sats': 500, 'description': 'Saque Ghost Bot'},
            timeout=30
        )
    
    @patch('api.voltz.requests.post')
    def test_create_withdraw_link_http_error(self, mock_post):
        """Testa erro HTTP na criação de link de saque."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('404 Not Found')
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            self.voltz_api.create_withdraw_link(1000)
        
        assert "Erro ao requisitar link de saque ao backend" in str(exc_info.value)
    
    @patch('api.voltz.requests.post')
    def test_create_withdraw_link_timeout_error(self, mock_post):
        """Testa erro de timeout na criação de link de saque."""
        mock_post.side_effect = requests.exceptions.Timeout('Timeout')
        
        with pytest.raises(Exception) as exc_info:
            self.voltz_api.create_withdraw_link(1000)
        
        assert "Erro ao requisitar link de saque ao backend" in str(exc_info.value)
    
    @patch('api.voltz.requests.post')
    def test_create_withdraw_link_connection_error(self, mock_post):
        """Testa erro de conexão na criação de link de saque."""
        mock_post.side_effect = requests.exceptions.ConnectionError('Connection failed')
        
        with pytest.raises(Exception) as exc_info:
            self.voltz_api.create_withdraw_link(1000)
        
        assert "Erro ao requisitar link de saque ao backend" in str(exc_info.value)
    
    @patch('api.voltz.requests.get')
    def test_get_wallet_balance_success(self, mock_get):
        """Testa obtenção bem-sucedida do saldo da carteira."""
        mock_response = Mock()
        mock_response.json.return_value = {'balance': 50000}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        balance = self.voltz_api.get_wallet_balance()
        
        mock_get.assert_called_once_with(
            'https://test.example.com/voltz/get_wallet_balance.php',
            timeout=30
        )
        assert balance == 50000
    
    @patch('api.voltz.requests.get')
    def test_get_wallet_balance_no_balance_field(self, mock_get):
        """Testa obtenção do saldo quando o campo balance não existe."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        balance = self.voltz_api.get_wallet_balance()
        
        assert balance == 0
    
    @patch('api.voltz.requests.get')
    def test_get_wallet_balance_http_error(self, mock_get):
        """Testa erro HTTP na obtenção do saldo."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('500 Internal Server Error')
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            self.voltz_api.get_wallet_balance()
        
        assert "Erro ao requisitar saldo ao backend" in str(exc_info.value)
    
    @patch('api.voltz.requests.get')
    def test_get_wallet_balance_timeout_error(self, mock_get):
        """Testa erro de timeout na obtenção do saldo."""
        mock_get.side_effect = requests.exceptions.Timeout('Timeout')
        
        with pytest.raises(Exception) as exc_info:
            self.voltz_api.get_wallet_balance()
        
        assert "Erro ao requisitar saldo ao backend" in str(exc_info.value)
    
    @patch('api.voltz.requests.get')
    def test_get_wallet_balance_connection_error(self, mock_get):
        """Testa erro de conexão na obtenção do saldo."""
        mock_get.side_effect = requests.exceptions.ConnectionError('Connection failed')
        
        with pytest.raises(Exception) as exc_info:
            self.voltz_api.get_wallet_balance()
        
        assert "Erro ao requisitar saldo ao backend" in str(exc_info.value)
    
    def test_format_withdraw_message(self):
        """Testa formatação da mensagem de saque."""
        amount_sats = 1000
        lnurl = 'LNURL1DP68GURN8GHJ7EM9W3SKC...'
        qr_code_url = 'https://api.qrserver.com/v1/create-qr-code/?data=LNURL...'
        
        message = self.voltz_api.format_withdraw_message(amount_sats, lnurl, qr_code_url)
        
        assert "⚡ *Solicitação de Saque* ⚡" in message
        assert "*1000 sats*" in message
        assert "*Lightning Network*" in message
        assert "📱 *Como sacar:*" in message
        assert lnurl in message
        assert "💰 O valor será creditado em até 10 minutos." in message
    
    def test_format_withdraw_message_float_amount(self):
        """Testa formatação da mensagem com valor em float."""
        amount_sats = 1500.5
        lnurl = 'LNURL_TEST'
        qr_code_url = 'https://qr.test'
        
        message = self.voltz_api.format_withdraw_message(amount_sats, lnurl, qr_code_url)
        
        assert "*1500.5 sats*" in message
        assert "LNURL_TEST" in message
    
    def test_format_withdraw_message_special_characters(self):
        """Testa formatação da mensagem com caracteres especiais no LNURL."""
        amount_sats = 2000
        lnurl = 'LNURL1DP68GURN8GHJ7EM9W3SKC&special=chars'
        qr_code_url = 'https://qr.test'
        
        message = self.voltz_api.format_withdraw_message(amount_sats, lnurl, qr_code_url)
        
        assert lnurl in message
        assert "*2000 sats*" in message


class TestVoltzAPILogging:
    """Testes para verificar o logging da classe VoltzAPI."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.voltz_api = VoltzAPI('https://test.example.com/voltz')
    
    @patch('api.voltz.logger')
    @patch('api.voltz.requests.post')
    def test_create_withdraw_link_logs_error(self, mock_post, mock_logger):
        """Testa se erros são logados corretamente."""
        mock_post.side_effect = requests.exceptions.ConnectionError('Connection failed')
        
        with pytest.raises(Exception):
            self.voltz_api.create_withdraw_link(1000)
        
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Erro ao requisitar link de saque ao backend" in error_call
    
    @patch('api.voltz.logger')
    @patch('api.voltz.requests.get')
    def test_get_wallet_balance_logs_error(self, mock_get, mock_logger):
        """Testa se erros são logados corretamente."""
        mock_get.side_effect = requests.exceptions.ConnectionError('Connection failed')
        
        with pytest.raises(Exception):
            self.voltz_api.get_wallet_balance()
        
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Erro ao requisitar saldo ao backend" in error_call


class TestVoltzAPIIntegration:
    """Testes de integração para cenários mais complexos."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.voltz_api = VoltzAPI()
    
    @patch('api.voltz.requests.post')
    @patch('api.voltz.requests.get')
    def test_complete_withdraw_flow(self, mock_get, mock_post):
        """Testa um fluxo completo de saque."""
        # Mock do saldo
        mock_balance_response = Mock()
        mock_balance_response.json.return_value = {'balance': 100000}
        mock_balance_response.raise_for_status.return_value = None
        mock_get.return_value = mock_balance_response
        
        # Mock da criação do link
        mock_withdraw_response = Mock()
        mock_withdraw_response.json.return_value = {
            'id': 'withdraw_123',
            'lnurl': 'LNURL1DP68GURN8GHJ7EM9W3SKC...',
            'qr_code_url': 'https://api.qrserver.com/v1/create-qr-code/?data=LNURL...'
        }
        mock_withdraw_response.raise_for_status.return_value = None
        mock_post.return_value = mock_withdraw_response
        
        # Teste do fluxo
        balance = self.voltz_api.get_wallet_balance()
        assert balance == 100000
        
        withdraw_data = self.voltz_api.create_withdraw_link(50000, 'Saque de teste')
        assert withdraw_data['id'] == 'withdraw_123'
        
        message = self.voltz_api.format_withdraw_message(
            50000, 
            withdraw_data['lnurl'], 
            withdraw_data['qr_code_url']
        )
        assert "*50000 sats*" in message
        assert withdraw_data['lnurl'] in message
