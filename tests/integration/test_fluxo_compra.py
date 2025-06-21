"""
Testes de integração para o fluxo de compra.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from telegram import Update, Message, Chat, User, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ContextTypes
from menus.menu_compra import (
    iniciar_compra, escolher_moeda, escolher_rede, processar_quantidade,
    processar_endereco, processar_metodo_pagamento, get_compra_conversation
)
from api.depix import PixAPI

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
    """Retorna um mock de CallbackContext."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = MagicMock()
    context.user_data = {}
    return context

class TestFluxoCompraIntegracao:
    """Testes de integração para o fluxo de compra."""
    
    @pytest.mark.asyncio
    @patch('menus.menu_compra.obter_cotacao')
    @patch('api.depix.PixAPI.criar_pagamento')
    @patch('menus.menu_compra.ReplyKeyboardMarkup')
    async def test_fluxo_completo_compra_pix(
        self, mock_keyboard, mock_criar_pagamento, mock_obter_cotacao, mock_update, mock_context
    ):
        """Testa o fluxo completo de compra com pagamento via PIX."""
        # Configura os mocks
        mock_update.message.reply_text = AsyncMock()
        mock_update.message.reply_photo = AsyncMock()
        mock_keyboard.return_value = MagicMock()
        
        # Mock para obter_cotacao (chamado em processar_quantidade)
        mock_obter_cotacao.return_value = 300000.00  # Preço do BTC
        
        # Mock para criar_pagamento (chamado em processar_metodo_pagamento)
        mock_criar_pagamento.return_value = {
            'qr_image_url': 'http://test.com/qr.png',
            'qr_copy_paste': '00020126330014BR.GOV.BCB.PIX0111test@test.com5204000053039865802BR5913Teste Loja6008BRASILIA62070503***6304A8A0',
            'transaction_id': '12345'
        }
        
        # 1. Iniciar compra
        result = await iniciar_compra(mock_update, mock_context)
        assert result == 0  # ESCOLHER_MOEDA
        
        # 2. Selecionar moeda (BTC)
        mock_update.message.text = "₿ Bitcoin (BTC)"
        result = await escolher_moeda(mock_update, mock_context)
        assert result == 1  # ESCOLHER_REDE
        assert mock_context.user_data["moeda"] == "BTC"
        
        # 3. Selecionar rede (Bitcoin)
        mock_update.message.text = "Bitcoin"
        result = await escolher_rede(mock_update, mock_context)
        assert result == 2  # QUANTIDADE
        assert mock_context.user_data["rede"] == "Bitcoin"
        
        # 4. Informar quantidade (R$ 100,50)
        mock_update.message.text = "100.50"
        result = await processar_quantidade(mock_update, mock_context)
        assert result == 3  # CONFIRMAR
        assert mock_context.user_data["valor_brl"] == 100.50
        assert mock_context.user_data["cotacao"] == 300000.00
        
        # 5. Confirmar compra (vai para SOLICITAR_ENDERECO)
        mock_update.message.text = "✅ Confirmar Compra"
        result = await processar_quantidade(mock_update, mock_context)
        assert result == 4  # SOLICITAR_ENDERECO
        
        # 6. Informar endereço
        mock_update.message.text = "bc1qxyz..."
        result = await processar_endereco(mock_update, mock_context)
        assert result == 5  # ESCOLHER_PAGAMENTO
        assert mock_context.user_data["endereco"] == "bc1qxyz..."
        
        # 7. Selecionar PIX como método de pagamento
        mock_update.message.text = "💠 PIX"
        result = await processar_metodo_pagamento(mock_update, mock_context)
        
        # Verifica se o pagamento foi criado corretamente
        mock_criar_pagamento.assert_called_once_with(
            valor_centavos=10050,  # R$ 100,50 em centavos
            chave_pix="bc1qxyz..."
        )
        
        # Verifica se as mensagens foram enviadas corretamente
        assert mock_update.message.reply_photo.called
        assert mock_update.message.reply_text.called
        
        # Verifica se o ConversationHandler foi encerrado (retorno -1)
        assert result == -1
    
    @pytest.mark.asyncio
    async def test_conversation_handler_compra(self):
        """Testa se o ConversationHandler está configurado corretamente."""
        # Obtém o ConversationHandler
        conversation_handler = get_compra_conversation()
        
        # Verifica os estados e handlers
        assert len(conversation_handler.states) == 6  # 6 estados definidos
        assert ESCOLHER_MOEDA in conversation_handler.states
        assert ESCOLHER_REDE in conversation_handler.states
        assert QUANTIDADE in conversation_handler.states
        assert CONFIRMAR in conversation_handler.states
        assert SOLICITAR_ENDERECO in conversation_handler.states
        assert ESCOLHER_PAGAMENTO in conversation_handler.states
        
        # Verifica se há um handler para cancelar a compra
        assert any(
            f.filter(update=MagicMock(message=MagicMock(text="❌ Cancelar")))
            for f in conversation_handler.fallbacks[0].filters
        )
