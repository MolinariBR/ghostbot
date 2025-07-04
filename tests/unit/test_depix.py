"""
Testes unitários para o módulo depix.py
"""
import pytest
from unittest.mock import patch, MagicMock
from api.depix import PixAPI, PixAPIError

class TestPixAPI:
    """Testes para a classe PixAPI."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Fixture para mockar variáveis de ambiente."""
        monkeypatch.setenv('PIX_API_URL', 'https://basetria.xyz/api/bot_deposit.php')
    
    def test_init_with_default_url(self, mock_env):
        """Testa a inicialização com URL padrão."""
        api = PixAPI()
        assert api.api_url == 'https://basetria.xyz/api/bot_deposit.php'
    
    def test_init_with_custom_url(self):
        """Testa a inicialização com URL personalizada."""
        api = PixAPI(api_url='http://custom-api.com/deposit')
        assert api.api_url == 'http://custom-api.com/deposit'
    
    @patch('api.depix.requests.post')
    def test_criar_pagamento_success(self, mock_post, mock_env):
        """Testa a criação de pagamento com sucesso."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'qr_image_url': 'http://test.com/qr.png',
                'qr_code_text': '00020126330014BR.GOV.BCB.PIX0111test@test.com5204000053039865802BR5913Teste Loja6008BRASILIA62070503***6304A8A0',
                'transaction_id': '12345'
            }
        }
        mock_post.return_value = mock_response
        
        # Executa o teste
        api = PixAPI()
        result = api.criar_pagamento(1000, 'test@test.com')
        
        # Verifica os resultados
        assert result == {
            'qr_image_url': 'http://test.com/qr.png',
            'qr_code_text': '00020126330014BR.GOV.BCB.PIX0111test@test.com5204000053039865802BR5913Teste Loja6008BRASILIA62070503***6304A8A0',
            'transaction_id': '12345'
        }
        
        # Verifica se a chamada foi feita com os parâmetros corretos
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json'] == {
            'amount_in_cents': 1000,
            'address': 'test@test.com',
            'type': 'pix'
        }
    
    @patch('api.depix.requests.post')
    def test_criar_pagamento_error(self, mock_post, mock_env):
        """Testa tratamento de erro na criação de pagamento."""
        # Configura o mock para simular erro
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'success': False,
            'error': 'Erro na API',
            'data': None
        }
        mock_post.return_value = mock_response
        
        # Executa o teste e verifica a exceção
        api = PixAPI()
        with pytest.raises(PixAPIError, match='Erro na API'):
            api.criar_pagamento(1000, 'test@test.com')
    
    @patch('api.depix.requests.post')
    def test_criar_pagamento_invalid_response(self, mock_post, mock_env):
        """Testa tratamento de resposta inválida da API."""
        # Configura o mock para simular resposta inválida
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'success': False,
            'error': 'Erro de validação',
            'data': None
        }
        mock_post.return_value = mock_response
        
        # Executa o teste e verifica a exceção
        api = PixAPI()
        with pytest.raises(PixAPIError, match='Erro na API: Erro de validação'):
            api.criar_pagamento(1000, 'test@test.com')
    
    def test_formatar_valor_brl(self):
        """Testa a formatação de valor em BRL."""
        from api.depix import formatar_valor_brl
        assert formatar_valor_brl(1000) == 'R$ 10,00'
        assert formatar_valor_brl(123456) == 'R$ 1.234,56'
