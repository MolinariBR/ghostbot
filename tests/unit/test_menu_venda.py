"""
Testes unitários para o módulo menu_venda.py
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from telegram import Update, Message, Chat, User, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from menus.menu_venda import (
    menu_moedas_venda, iniciar_venda, escolher_moeda_venda, 
    processar_quantidade_venda, processar_endereco, confirmar_venda, 
    cancelar_venda, ESCOLHER_MOEDA, QUANTIDADE, ENDERECO, CONFIRMAR
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

class TestMenuVenda:
    """Testes para as funções do menu de venda."""
    
    def test_menu_moedas_venda(self):
        """Testa a criação do menu de moedas para venda."""
        keyboard = menu_moedas_venda()
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert len(keyboard.keyboard) == 4  # 3 moedas + voltar
        assert keyboard.keyboard[0][0].text == "₿ Vender Bitcoin (BTC)"
        assert keyboard.keyboard[1][0].text == "💵 Vender Tether (USDT)"
        assert keyboard.keyboard[2][0].text == "💠 Vender Depix"
        assert keyboard.keyboard[3][0].text == "🔙 Voltar"
    
    @pytest.mark.asyncio
    async def test_iniciar_venda(self, mock_update, mock_context):
        """Testa o início do fluxo de venda."""
        mock_update.message.reply_text = AsyncMock()
        
        result = await iniciar_venda(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        assert result == ESCOLHER_MOEDA
    
    @pytest.mark.asyncio
    async def test_escolher_moeda_venda_btc(self, mock_update, mock_context):
        """Testa a seleção de BTC para venda."""
        mock_update.message.text = "₿ Vender Bitcoin (BTC)"
        mock_update.message.reply_text = AsyncMock()
        
        result = await escolher_moeda_venda(mock_update, mock_context)
        
        assert mock_context.user_data["moeda_venda"] == "₿ Vender Bitcoin (BTC)"
        assert result == QUANTIDADE
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_escolher_moeda_venda_voltar(self, mock_update, mock_context):
        """Testa o botão de voltar no menu de moedas."""
        mock_update.message.text = "🔙 Voltar"
        mock_update.message.reply_text = AsyncMock()
        
        # Mock da função cancelar_venda
        with patch('menus.menu_venda.cancelar_venda', new_callable=AsyncMock) as mock_cancelar:
            mock_cancelar.return_value = -1
            result = await escolher_moeda_venda(mock_update, mock_context)
            
        mock_cancelar.assert_called_once_with(mock_update, mock_context)
        assert result == -1
    
    @pytest.mark.asyncio
    async def test_processar_quantidade_valida(self, mock_update, mock_context):
        """Testa o processamento de uma quantidade válida."""
        mock_update.message.text = "1.5"
        mock_context.user_data["moeda_venda"] = "₿ Vender Bitcoin (BTC)"
        mock_update.message.reply_text = AsyncMock()
        
        result = await processar_quantidade_venda(mock_update, mock_context)
        
        assert mock_context.user_data["quantidade_venda"] == 1.5
        assert result == ENDERECO
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_processar_quantidade_invalida(self, mock_update, mock_context):
        """Testa o processamento de uma quantidade inválida."""
        mock_update.message.text = "abc"  # Valor inválido
        mock_context.user_data["moeda_venda"] = "₿ Vender Bitcoin (BTC)"
        mock_update.message.reply_text = AsyncMock()
        
        result = await processar_quantidade_venda(mock_update, mock_context)
        
        assert result == QUANTIDADE  # Deve permanecer no mesmo estado
        assert mock_update.message.reply_text.call_count == 2  # Mensagem de erro + pedido de nova quantidade
    
    @pytest.mark.asyncio
    async def test_processar_endereco(self, mock_update, mock_context):
        """Testa o processamento do endereço de saque."""
        mock_update.message.text = "bc1qxyz..."
        mock_context.user_data.update({
            "moeda_venda": "\u20bf Vender Bitcoin (BTC)",
            "quantidade_venda": 0.5
        })
        mock_update.message.reply_text = AsyncMock()
        
        result = await processar_endereco(mock_update, mock_context)
        
        assert mock_context.user_data["endereco"] == "bc1qxyz..."
        assert result == CONFIRMAR
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_confirmar_venda(self, mock_update, mock_context):
        """Testa a confirmação da venda."""
        mock_update.message.text = "\u2705 Confirmar Venda"
        mock_context.user_data.update({
            "moeda_venda": "\u20bf Vender Bitcoin (BTC)",
            "quantidade_venda": 0.5,
            "endereco": "bc1qxyz..."
        })
        mock_update.message.reply_text = AsyncMock()
        
        result = await confirmar_venda(mock_update, mock_context)
        
        assert result == -1  # Encerra a conversa
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cancelar_venda(self, mock_update, mock_context):
        """Testa o cancelamento da venda."""
        mock_update.message.reply_text = AsyncMock()
        
        # Mock da função menu_principal
        with patch('menus.menu_venda.menu_principal') as mock_menu_principal:
            result = await cancelar_venda(mock_update, mock_context)
            
        assert result == -1  # Encerra a conversa
        mock_update.message.reply_text.assert_called_once()
        mock_menu_principal.assert_called_once()
