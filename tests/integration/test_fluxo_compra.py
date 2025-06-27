"""
Testes de integração para o fluxo de compra.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from telegram import Update, Message, Chat, User, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from menus.menu_compra import (
    iniciar_compra, escolher_moeda, escolher_rede, processar_quantidade,
    processar_endereco, processar_metodo_pagamento, get_compra_conversation,
    confirmar_compra, ESCOLHER_MOEDA, ESCOLHER_REDE, QUANTIDADE, CONFIRMAR_COMPRA, 
    SOLICITAR_ENDERECO, ESCOLHER_PAGAMENTO, menu_principal
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
    """Retorna um mock de ContextTypes.DEFAULT_TYPE."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = MagicMock()
    context.user_data = {}
    return context

class TestFluxoCompraIntegracao:
    """Testes de integração para o fluxo de compra."""
    
    @pytest.mark.asyncio
    @patch('menus.menu_compra.obter_cotacao', new_callable=AsyncMock)
    @patch('api.depix.PixAPI.criar_pagamento')
    @patch('menus.menu_compra.ReplyKeyboardMarkup')
    async def test_fluxo_completo_compra_pix(
        self, mock_keyboard, mock_criar_pagamento, mock_obter_cotacao, mock_update, mock_context
    ):
        """Testa o fluxo completo de compra com pagamento via PIX."""
        mock_update.message.reply_text = AsyncMock()
        mock_update.message.reply_photo = AsyncMock()
        mock_keyboard.return_value = MagicMock()
        
        mock_obter_cotacao.return_value = 300000.00
        
        mock_criar_pagamento.return_value = {
            'qr_image_url': 'http://test.com/qr.png',
            'qr_code_text': '00020126330014BR.GOV.BCB.PIX0111test@test.com5204000053039865802BR5913Teste Loja6008BRASILIA62070503***6304A8A0',
            'transaction_id': '12345'
        }
        
        # 1. Iniciar compra
        result = await iniciar_compra(mock_update, mock_context)
        assert result == 0  # ESCOLHER_MOEDA
        
        # 2. Selecionar moeda (BTC)
        mock_update.message.text = "₿ Bitcoin (BTC)"
        result = await escolher_moeda(mock_update, mock_context)
        assert result == ESCOLHER_REDE
        assert mock_context.user_data["moeda"] == "₿ Bitcoin (BTC)"
        
        # 3. Selecionar rede (Bitcoin)
        mock_update.message.text = "Bitcoin"
        result = await escolher_rede(mock_update, mock_context)
        assert result == QUANTIDADE
        assert mock_context.user_data["rede"] == "Bitcoin"
        
        # 4. Informar quantidade (R$ 100,50)
        mock_update.message.text = "100.50"
        result = await processar_quantidade(mock_update, mock_context)
        print(f"Resultado de processar_quantidade: {result}, esperado: {CONFIRMAR_COMPRA}")
        print(f"user_data: {mock_context.user_data}")
        assert result == CONFIRMAR_COMPRA
        assert mock_context.user_data["valor_brl"] == 100.50
        assert mock_context.user_data["cotacao"] == 300000.00
        
        # 5. Confirmar compra (vai para SOLICITAR_ENDERECO)
        mock_update.message.text = "✅ Confirmar Compra"
        result = await confirmar_compra(mock_update, mock_context)
        assert result == SOLICITAR_ENDERECO
        
        # 6. Informar endereço
        mock_update.message.text = "bc1qxyz..."
        result = await processar_endereco(mock_update, mock_context)
        assert result == ESCOLHER_PAGAMENTO
        assert mock_context.user_data["endereco_recebimento"] == "bc1qxyz..."
        
        # 7. Selecionar PIX como método de pagamento
        mock_update.message.text = "💠 PIX"
        
        # Configura o mock para retornar uma resposta de sucesso da API PIX
        mock_criar_pagamento.return_value = {
            'success': True,
            'data': {
                'transaction_id': '12345',
                'qr_image_url': 'http://test.com/qr.png',
                'qr_code_text': '00020126330014BR.GOV.BCB.PIX0111test@test.com5204000053039865802BR5913Teste Loja6008BRASILIA62070503***6304A8A0',
                'qr_copy_paste': '00020126330014BR.GOV.BCB.PIX0111test@test.com5204000053039865802BR5913Teste Loja6008BRASILIA62070503***6304A8A0'
            }
        }
        
        # Configura o mock para reply_photo retornar um objeto Message
        mock_message = AsyncMock()
        mock_update.message.reply_photo.return_value = mock_message
        
        # Executa a função
        result = await processar_metodo_pagamento(mock_update, mock_context)
        
        # Verifica se o pagamento PIX foi criado corretamente
        mock_criar_pagamento.assert_called_once_with(
            valor_centavos=10050,  # R$ 100,50 em centavos
            endereco="bc1qxyz..."
        )
        
        # Verifica se as mensagens foram enviadas corretamente
        mock_update.message.reply_photo.assert_called_once_with(
            photo='http://test.com/qr.png',
            caption='📱 *QR Code para pagamento*\n\nAponte a câmera do seu app de pagamento para escanear o QR Code acima.',
            parse_mode='Markdown'
        )
        
        # Verifica se a mensagem de confirmação foi enviada
        mock_update.message.reply_text.assert_called_with(
            '✅ *SOLICITAÇÃO DE DEPÓSITO RECEBIDA!*\n'
            '━━━━━━━━━━━━━━━━━━━━\n'
            '• *Valor:* R$ 100,50\n'
            '• *Criptomoeda:* ₿ BITCOIN (BTC)\n'
            '• *Endereço de destino:* `bc1qxyz...`\n'
            '• *ID da transação:* `12345`\n\n'
            '📱 *Pague o PIX usando o QR Code abaixo ou o código copia e cola:*\n\n'
            '`00020126330014BR.GOV.BCB.PIX0111test@test.com5204000053039865802BR5913Teste Loja6008BRASILIA62070503***6304A8A0`\n\n'
            'Após o pagamento, aguarde alguns instantes para a confirmação.\n'
            'Obrigado pela preferência!',
            parse_mode='Markdown',
            reply_markup=menu_principal()
        )
        
        # Verifica se o ConversationHandler foi encerrado
        assert result == ConversationHandler.END
    
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
        assert CONFIRMAR_COMPRA in conversation_handler.states
        assert SOLICITAR_ENDERECO in conversation_handler.states
        assert ESCOLHER_PAGAMENTO in conversation_handler.states
        
        # Verifica se há um handler para cancelar a compra
        assert any(
            f.filter(update=MagicMock(message=MagicMock(text="❌ Cancelar")))
            for f in conversation_handler.fallbacks[0].filters
        )
