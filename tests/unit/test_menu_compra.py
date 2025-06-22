"""
Testes unitários para o módulo menu_compra.py
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from telegram import Update, Message, Chat, User, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from menus.menu_compra import (
    obter_cotacao, formatar_brl, formatar_cripto,
    menu_moedas, menu_redes, iniciar_compra, escolher_moeda,
    escolher_rede, processar_quantidade, confirmar_compra,
    processar_endereco, processar_metodo_pagamento, cancelar_compra,
    ESCOLHER_MOEDA, ESCOLHER_REDE, QUANTIDADE, CONFIRMAR,
    SOLICITAR_ENDERECO, ESCOLHER_PAGAMENTO
)

# Fixtures para mocks comuns
@pytest.fixture
def mock_update():
    """Retorna um mock de Update."""
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.chat = MagicMock(spec=Chat)
    update.message.chat.id = 12345
    update.message.from_user = MagicMock(spec=User)
    update.message.from_user.id = 54321
    update.message.text = ""
    update.effective_chat = MagicMock()
    update.effective_chat.id = 12345
    return update

@pytest.fixture
def mock_context():
    """Retorna um mock de ContextTypes.DEFAULT_TYPE."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = MagicMock()
    context.user_data = {}
    return context

class TestMenuCompra:
    """Testes para as funções do menu de compra."""
    
    @pytest.mark.asyncio
    @patch('menus.menu_compra.get_btc_price_brl')
    @patch('menus.menu_compra.get_usdt_price_brl')
    @patch('menus.menu_compra.get_depix_price_brl')
    async def test_obter_cotacao(self, mock_depix, mock_usdt, mock_btc):
        """Testa a função obter_cotacao com diferentes moedas."""
        # Configura os mocks para retornar valores diretamente (sem ser corotina)
        mock_btc.return_value = 300000.00
        mock_usdt.return_value = 5.50
        mock_depix.return_value = 0.05
        
        # Testa com BTC - note o await
        resultado = await obter_cotacao("BTC")
        assert resultado == 300000.00
        mock_btc.assert_called_once()
        
        # Limpa os mocks para os próximos testes
        mock_btc.reset_mock()
        
        # Testa com USDT
        resultado = await obter_cotacao("USDT")
        assert resultado == 5.50
        mock_usdt.assert_called_once()
        
        # Limpa os mocks para os próximos testes
        mock_usdt.reset_mock()
        
        # Testa com Depix
        resultado = await obter_cotacao("Depix")
        assert resultado == 0.05
        mock_depix.assert_called_once()
        
        # Testa moeda inválida
        resultado = await obter_cotacao("INVALID")
        assert resultado == 1.0
    
    def test_formatar_brl(self):
        """Testa a formatação de valores em BRL."""
        assert formatar_brl(1500.5) == "R$ 1.500,50"
        assert formatar_brl(0.5) == "R$ 0,50"
        assert formatar_brl(1000000) == "R$ 1.000.000,00"
    
    def test_formatar_cripto(self):
        """Testa a formatação de valores de criptomoedas."""
        # BTC com 8 casas decimais
        assert formatar_cripto(1.23456789, "BTC") == "1.23456789 BTC"
        # USDT com 2 casas decimais
        assert formatar_cripto(100.5, "USDT") == "100.50 USDT"
        # Depix com 2 casas decimais
        assert formatar_cripto(50.0, "Depix") == "50.00 Depix"
        assert formatar_cripto(1000.5, "Depix") == "1,000.50 Depix"
    
    def test_menu_moedas(self):
        """Testa a criação do menu de moedas."""
        keyboard = menu_moedas()
        # Verifica o número de linhas (4: BTC, USDT, Depix e Voltar)
        assert len(keyboard) == 4  # Agora é uma lista de listas
        # Verifica os textos dos botões
        assert keyboard[0][0].text == "₿ Bitcoin (BTC)"
        assert keyboard[1][0].text == "💵 Tether (USDT)"
        assert keyboard[2][0].text == "💠 Depix"
        assert keyboard[3][0].text == "🔙 Voltar"

    def test_menu_redes(self):
        """Testa a criação do menu de redes."""
        # Testa com BTC
        keyboard = menu_redes("BTC")
        assert len(keyboard) == 4  # 3 redes + voltar
        assert keyboard[0][0].text == "⛓️ On-chain"
        assert keyboard[1][0].text == "⚡ Lightning"
        assert keyboard[2][0].text == "💧 Liquid"
        assert keyboard[3][0].text == "🔙 Voltar"
        
        # Testa com USDT
        keyboard = menu_redes("USDT")
        assert len(keyboard) == 3  # 2 redes + voltar
        assert keyboard[0][0].text == "💧 Liquid"
        assert keyboard[1][0].text == "🟣 Polygon"
        assert keyboard[2][0].text == "🔙 Voltar"
        
        # Testa com Depix
        keyboard = menu_redes("Depix")
        assert len(keyboard) == 2  # 1 rede + voltar
        assert keyboard[0][0].text == "💧 Liquid"
        assert keyboard[1][0].text == "🔙 Voltar"
    
    @pytest.mark.asyncio
    @patch('menus.menu_compra.ReplyKeyboardMarkup')
    async def test_iniciar_compra(self, mock_keyboard, mock_update, mock_context):
        """Testa o início do fluxo de compra."""
        mock_update.message.reply_text = AsyncMock()
        result = await iniciar_compra(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()
        assert result == ESCOLHER_MOEDA
    
    @pytest.mark.asyncio
    @patch('menus.menu_compra.ReplyKeyboardMarkup')
    async def test_escolher_moeda_valida(self, mock_keyboard, mock_update, mock_context):
        """Testa a seleção de uma moeda válida."""
        mock_update.message.text = "\u20bf Bitcoin (BTC)"
        mock_update.message.reply_text = AsyncMock()
        result = await escolher_moeda(mock_update, mock_context)
        assert mock_context.user_data["moeda"] == "\u20bf Bitcoin (BTC)"
        assert result == ESCOLHER_REDE
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    @patch('menus.menu_compra.ReplyKeyboardMarkup')
    async def test_escolher_rede_valida(self, mock_keyboard, mock_update, mock_context):
        """Testa a seleção de uma rede válida."""
        mock_update.message.text = "Bitcoin"
        mock_context.user_data["moeda"] = "BTC"
        mock_update.message.reply_text = AsyncMock()
        
        result = await escolher_rede(mock_update, mock_context)
        
        assert mock_context.user_data["rede"] == "Bitcoin"
        assert result == QUANTIDADE
        mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_processar_quantidade_valida(self, mock_update, mock_context):
        """Testa o processamento de uma quantidade válida."""
        mock_update.message.text = "100.50"
        mock_context.user_data["moeda"] = "BTC"
        mock_context.user_data["rede"] = "Bitcoin"
        mock_update.message.reply_text = AsyncMock()
        
        with patch('menus.menu_compra.obter_cotacao', new_callable=AsyncMock) as mock_cotacao:
            mock_cotacao.return_value = 300000.00
            result = await processar_quantidade(mock_update, mock_context)
        
        assert mock_context.user_data["valor_brl"] == 100.50
        assert mock_context.user_data["cotacao"] == 300000.00
        assert result == CONFIRMAR
        mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_confirmar_compra(self, mock_update, mock_context):
        """Testa a confirmação da compra."""
        mock_update.message.text = "✅ Confirmar Compra"
        mock_context.user_data.update({
            "moeda": "BTC",
            "rede": "Bitcoin",
            "valor_brl": 100.50,
            "cotacao": 300000.00
        })
        mock_update.message.reply_text = AsyncMock()
        
        result = await confirmar_compra(mock_update, mock_context)
        
        assert result == SOLICITAR_ENDERECO
        mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    @patch('menus.menu_compra.ReplyKeyboardMarkup')
    async def test_processar_endereco(self, mock_keyboard, mock_update, mock_context):
        """Testa o processamento do endereço de recebimento."""
        mock_update.message.text = "bc1qxyz..."
        mock_update.message.reply_text = AsyncMock()
        
        result = await processar_endereco(mock_update, mock_context)
        
        assert mock_context.user_data["endereco_recebimento"] == "bc1qxyz..."
        assert result == ESCOLHER_PAGAMENTO
        mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_cancelar_compra(self, mock_update, mock_context):
        """Testa o cancelamento da compra."""
        mock_update.message.reply_text = AsyncMock()
        
        result = await cancelar_compra(mock_update, mock_context)
        
        assert result == -1  # Encerra a conversa
        mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_confirmar_compra_lightning(self, mock_update, mock_context):
        """Testa a confirmação da compra para Lightning: não pede endereço, exibe menu de pagamento."""
        mock_update.message.text = "✅ Confirmar Compra"
        mock_context.user_data.update({
            "moeda": "BTC",
            "rede": "Lightning",
            "valor_brl": 100.50,
            "cotacao": 300000.00
        })
        mock_update.message.reply_text = AsyncMock()
        # Chama a função
        result = await confirmar_compra(mock_update, mock_context)
        # Deve ir direto para ESCOLHER_PAGAMENTO
        assert result == ESCOLHER_PAGAMENTO
        mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_processar_metodo_pagamento_lightning(self, mock_update, mock_context):
        """Testa o fluxo de pagamento Lightning: após pagamento tradicional, exibe mensagem de aguarde confirmação e usa endereço padrão."""
        mock_update.message.text = "💠 PIX"
        mock_context.user_data.update({
            "moeda": "BTC",
            "rede": "Lightning",
            "valor_brl": 100.50,
            "cotacao": 300000.00
        })
        mock_update.message.reply_text = AsyncMock()
        mock_update.message.reply_photo = AsyncMock()
        # Mock da API Depix para não chamar de verdade
        with patch('api.depix.pix_api') as mock_pix_api:
            mock_pix_api.criar_pagamento.return_value = {
                'success': True,
                'data': {
                    'qr_image_url': 'http://fake-qr',
                    'transaction_id': 'txid123',
                    'qr_copy_paste': 'copiaecola123'
                }
            }
            result = await processar_metodo_pagamento(mock_update, mock_context)
            # O endereço padrão deve ser usado
            assert mock_context.user_data['endereco_recebimento'] == 'voltzapi@tria.com'
            # O fluxo deve terminar
            assert result == -1  # ConversationHandler.END
            # Mensagens de confirmação devem ser chamadas
            mock_update.message.reply_photo.assert_called()
            mock_update.message.reply_text.assert_called()
