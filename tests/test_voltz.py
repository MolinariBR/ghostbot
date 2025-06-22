"""
Testes de integração simulada para o fluxo Voltz sem pagamento real de PIX.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes
from menus.menu_compra import processar_metodo_pagamento

@pytest.mark.asyncio
async def test_fluxo_voltz_simulado():
    # Mocks do Update e Context
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.chat = MagicMock(spec=Chat)
    update.message.chat.id = 12345
    update.message.from_user = MagicMock(spec=User)
    update.message.from_user.id = 54321
    update.message.text = "💠 PIX"
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    update.effective_chat = MagicMock()
    update.effective_chat.id = 12345

    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = MagicMock()
    context.user_data = {
        "moeda": "BTC",
        "rede": "Lightning",
        "valor_brl": 50.0,
        "cotacao": 300000.0,
        "endereco_recebimento": "voltzapi@tria.com"
    }

    # Mock da API Depix para não chamar de verdade
    import sys
    from unittest.mock import patch
    with patch('api.depix.pix_api') as mock_pix_api:
        mock_pix_api.criar_pagamento.return_value = {
            'success': True,
            'data': {
                'qr_image_url': 'http://fake-qr',
                'transaction_id': 'txid123',
                'qr_code_text': 'copiaecola123'
            }
        }
        result = await processar_metodo_pagamento(update, context)
        assert context.user_data['endereco_recebimento'] == 'voltzapi@tria.com'
        assert result == -1  # ConversationHandler.END
        update.message.reply_photo.assert_called()
        update.message.reply_text.assert_called()
