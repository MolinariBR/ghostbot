#!/usr/bin/env python3
"""
Bot Integration: Sistema de Gatilhos + python-telegram-bot
Integração correta com o bot principal usando python-telegram-bot
"""
import sys
import os
import logging
from pathlib import Path
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    CommandHandler, 
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

try:
    from telegram.ext import Application
except ImportError:
    Application = None  # Fallback para versões antigas

# Adicionar diretório principal ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar sistema de gatilhos
try:
    from .sistema_gatilhos import trigger_system, TriggerEvent, OrderStatus
except ImportError:
    try:
        from trigger.sistema_gatilhos import trigger_system, TriggerEvent, OrderStatus
    except ImportError:
        from trigger.simple_system import simple_trigger_system as trigger_system
        from trigger.config import TriggerEvent, OrderStatus

logger = logging.getLogger('bot_integration')

class TriggerBotIntegration:
    """Integração do sistema de gatilhos com python-telegram-bot"""
    
    def __init__(self, application):
        self.application = application
        self.trigger_system = trigger_system
        self.enabled_users = set()  # Usuários que optaram pelo novo sistema
        self.setup_ui_methods()
        
    def setup_ui_methods(self):
        """Conecta métodos de UI do sistema de gatilhos"""
        # Wrapper para métodos assíncronos
        import asyncio
        
        def async_wrapper(coro_func):
            def wrapper(*args, **kwargs):
                try:
                    # Se já estamos em um loop, usar create_task
                    loop = asyncio.get_running_loop()
                    loop.create_task(coro_func(*args, **kwargs))
                except RuntimeError:
                    # Se não há loop rodando, criar um novo
                    asyncio.run(coro_func(*args, **kwargs))
            return wrapper
        
        self.trigger_system.send_currency_selection_menu = async_wrapper(self.send_currency_selection_menu)
        self.trigger_system.send_network_selection_menu = async_wrapper(self.send_network_selection_menu)
        self.trigger_system.send_amount_request = async_wrapper(self.send_amount_request)
        self.trigger_system.send_order_summary_and_payment_options = async_wrapper(self.send_order_summary_and_payment_options)
        self.trigger_system.send_pix_qr_code = async_wrapper(self.send_pix_qr_code)
        self.trigger_system.send_address_request = async_wrapper(self.send_address_request)
        self.trigger_system.send_transaction_completed_message = async_wrapper(self.send_transaction_completed_message)
        self.trigger_system.send_invalid_amount_message = async_wrapper(self.send_invalid_amount_message)
    
    def enable_for_user(self, chat_id: str):
        """Ativa sistema de gatilhos para usuário específico"""
        self.enabled_users.add(str(chat_id))
        logger.info(f"✅ Sistema de gatilhos ativado para usuário {chat_id}")
    
    def is_enabled_for_user(self, chat_id: str) -> bool:
        """Verifica se sistema está ativo para o usuário"""
        return str(chat_id) in self.enabled_users
    
    def setup_handlers(self):
        """Configura handlers do sistema de gatilhos"""
        
        # Handler para comando /comprar_v2 (novo sistema)
        self.application.add_handler(
            CommandHandler('comprar_v2', self.handle_comprar_v2)
        )
        
        # Handler para callbacks do sistema de gatilhos
        self.application.add_handler(
            CallbackQueryHandler(self.handle_trigger_callback, pattern='^trig_')
        )
        
        # Handler para mensagens de texto em contexto de gatilho
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_trigger_message
            )
        )
    
    # ============================================================================
    # HANDLERS
    # ============================================================================
    
    async def handle_comprar_v2(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para comando /comprar_v2 (novo sistema)"""
        chat_id = str(update.effective_chat.id)
        
        # Ativar sistema para este usuário
        self.enable_for_user(chat_id)
        
        # Disparar evento de compra
        self.trigger_system.trigger_event(
            TriggerEvent.USER_CLICKED_BUY,
            chat_id
        )
        
        logger.info(f"🚀 Sistema de gatilhos iniciado para usuário {chat_id}")
    
    async def handle_trigger_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para callbacks do sistema de gatilhos"""
        query = update.callback_query
        await query.answer()
        
        chat_id = str(query.message.chat.id)
        callback_data = query.data
        
        # Verificar se usuário está no sistema de gatilhos
        if not self.is_enabled_for_user(chat_id):
            await query.edit_message_text("❌ Sistema de gatilhos não ativo para este usuário.")
            return
        
        # Processar callbacks
        if callback_data.startswith('trig_currency_'):
            currency = callback_data.replace('trig_currency_', '')
            self.trigger_system.trigger_event(
                TriggerEvent.CURRENCY_SELECTED,
                chat_id,
                {'currency': currency}
            )
            await query.edit_message_text(f"✅ Moeda selecionada: {currency.upper()}")
            
        elif callback_data.startswith('trig_network_'):
            network = callback_data.replace('trig_network_', '')
            self.trigger_system.trigger_event(
                TriggerEvent.NETWORK_SELECTED,
                chat_id,
                {'network': network}
            )
            await query.edit_message_text(f"✅ Rede selecionada: {network.upper()}")
            
        elif callback_data.startswith('trig_payment_'):
            payment_method = callback_data.replace('trig_payment_', '')
            self.trigger_system.trigger_event(
                TriggerEvent.PAYMENT_METHOD_SELECTED,
                chat_id,
                {'payment_method': payment_method}
            )
            await query.edit_message_text(f"✅ Método de pagamento: {payment_method}")
    
    async def handle_trigger_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensagens de texto em contexto de gatilho"""
        chat_id = str(update.effective_chat.id)
        
        # Verificar se usuário está no sistema de gatilhos
        if not self.is_enabled_for_user(chat_id):
            return  # Deixar outros handlers processarem
        
        # Verificar estado do usuário
        order = self.trigger_system.active_orders.get(chat_id)
        if not order:
            return
        
        message_text = update.message.text
        
        # Processar valor
        if order['status'] == OrderStatus.NETWORK_SELECTED.value:
            try:
                amount = float(message_text.replace(',', '.').replace('R$', '').strip())
                self.trigger_system.trigger_event(
                    TriggerEvent.AMOUNT_ENTERED,
                    chat_id,
                    {'amount': amount}
                )
            except ValueError:
                await update.message.reply_text(
                    "❌ Valor inválido. Digite um número válido (ex: 50.00)"
                )
        
        # Processar endereço
        elif order['status'] == OrderStatus.PIX_PAID.value:
            address = message_text.strip()
            self.trigger_system.trigger_event(
                TriggerEvent.ADDRESS_PROVIDED,
                chat_id,
                {'address': address}
            )
    
    # ============================================================================
    # MÉTODOS DE INTERFACE (UI)
    # ============================================================================
    
    async def send_currency_selection_menu(self, chat_id: str):
        """Envia menu de seleção de moeda"""
        text = (
            "💰 <b>Escolha a criptomoeda:</b>\n\n"
            "• <b>Bitcoin (BTC)</b> - A primeira e maior criptomoeda\n"
            "• <b>Tether (USDT)</b> - Stablecoin pareada ao dólar\n"
            "• <b>DEPIX</b> - Token nativo brasileiro\n\n"
            "👆 Selecione uma opção:"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("₿ Bitcoin", callback_data="trig_currency_bitcoin"),
                InlineKeyboardButton("₮ Tether", callback_data="trig_currency_tether")
            ],
            [
                InlineKeyboardButton("💰 DEPIX", callback_data="trig_currency_depix")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def send_network_selection_menu(self, chat_id: str, currency: str):
        """Envia menu de seleção de rede"""
        networks = {
            'bitcoin': {
                'text': "🌐 <b>Escolha a rede para Bitcoin:</b>\n\n"
                        "⚡ <b>Lightning</b> - Transações instantâneas e taxas baixas\n"
                        "🔗 <b>On-chain</b> - Rede principal do Bitcoin\n"
                        "🌊 <b>Liquid</b> - Sidechain rápida e confidencial",
                'keyboard': [
                    [
                        InlineKeyboardButton("⚡ Lightning", callback_data="trig_network_lightning"),
                        InlineKeyboardButton("🔗 On-chain", callback_data="trig_network_onchain")
                    ],
                    [
                        InlineKeyboardButton("🌊 Liquid", callback_data="trig_network_liquid")
                    ]
                ]
            },
            'tether': {
                'text': "🌐 <b>Escolha a rede para USDT:</b>\n\n"
                        "🔷 <b>Polygon</b> - Rede rápida e taxas baixas\n"
                        "🌊 <b>Liquid</b> - Sidechain do Bitcoin",
                'keyboard': [
                    [
                        InlineKeyboardButton("🔷 Polygon", callback_data="trig_network_polygon"),
                        InlineKeyboardButton("🌊 Liquid", callback_data="trig_network_liquid")
                    ]
                ]
            },
            'depix': {
                'text': "🌐 <b>Rede para DEPIX:</b>\n\n"
                        "🔷 <b>Polygon</b> - Rede nativa do DEPIX",
                'keyboard': [
                    [
                        InlineKeyboardButton("🔷 Polygon", callback_data="trig_network_polygon")
                    ]
                ]
            }
        }
        
        network_info = networks.get(currency, networks['bitcoin'])
        reply_markup = InlineKeyboardMarkup(network_info['keyboard'])
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=network_info['text'],
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def send_amount_request(self, chat_id: str):
        """Solicita valor do usuário"""
        text = (
            "💵 <b>Informe o valor da compra:</b>\n\n"
            "• Valor mínimo: R$ 10,00\n"
            "• Valor máximo: R$ 4.999,99\n"
            "• Formato: 50.00 ou 50,00\n\n"
            "💡 Digite o valor desejado:"
        )
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
        )
    
    async def send_order_summary_and_payment_options(self, chat_id: str, order: dict):
        """Envia resumo do pedido e opções de pagamento"""
        currency = order['currency'].upper()
        network = order['network'].upper()
        amount = order['amount']
        
        # Calcular quantidade de crypto (simulado)
        crypto_amount = self.calculate_crypto_amount(order)
        
        text = (
            f"📋 <b>RESUMO DO PEDIDO</b>\n\n"
            f"💰 Moeda: {currency}\n"
            f"🌐 Rede: {network}\n"
            f"💵 Valor: R$ {amount:.2f}\n"
            f"⚡ Você receberá: ~{crypto_amount}\n\n"
            f"💳 <b>Escolha o método de pagamento:</b>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📱 PIX (Recomendado)", callback_data="trig_payment_pix")
            ],
            [
                InlineKeyboardButton("🏦 TED", callback_data="trig_payment_ted"),
                InlineKeyboardButton("📄 Boleto", callback_data="trig_payment_boleto")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def send_pix_qr_code(self, chat_id: str, pix_data: dict):
        """Envia QR Code PIX"""
        text = (
            f"📱 <b>PAGAMENTO PIX GERADO</b>\n\n"
            f"🎯 ID do Pedido: <code>{pix_data.get('depix_id', 'PIX123')}</code>\n"
            f"💰 Valor: R$ {pix_data.get('amount', '0.00')}\n\n"
            f"📋 <b>Para pagar:</b>\n"
            f"1. Abra seu app bancário\n"
            f"2. Escaneie o QR Code\n"
            f"3. Ou use o código Pix Copia e Cola\n\n"
            f"⏰ O pagamento será detectado automaticamente!"
        )
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
        )
    
    async def send_address_request(self, chat_id: str):
        """Solicita endereço do usuário"""
        text = (
            "📮 <b>Informe seu endereço de recebimento:</b>\n\n"
            "💡 Digite o endereço da sua carteira onde deseja receber a criptomoeda:"
        )
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
        )
    
    async def send_transaction_completed_message(self, chat_id: str, result: dict):
        """Envia mensagem de transação concluída"""
        text = (
            f"🎉 <b>TRANSAÇÃO CONCLUÍDA!</b>\n\n"
            f"✅ Sua criptomoeda foi enviada com sucesso!\n\n"
            f"🔗 <b>ID da Transação:</b>\n"
            f"<code>{result.get('txid', 'TX_ID_PLACEHOLDER')}</code>\n\n"
            f"💡 Confira na sua carteira!"
        )
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
        )
    
    async def send_invalid_amount_message(self, chat_id: str):
        """Envia mensagem de valor inválido"""
        text = (
            "❌ <b>Valor inválido!</b>\n\n"
            "💵 O valor deve estar entre R$ 10,00 e R$ 4.999,99\n\n"
            "💡 Digite um valor válido:"
        )
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
        )
    
    def calculate_crypto_amount(self, order: dict) -> str:
        """Calcula quantidade de crypto baseada no valor em reais"""
        currency = order['currency']
        amount = order['amount']
        
        # Simulação de cotações
        if currency == 'bitcoin':
            btc_rate = 300000  # R$ 300k por BTC
            btc_amount = amount / btc_rate
            if order['network'] == 'lightning':
                sats = int(btc_amount * 100000000)
                return f"{sats} sats"
            else:
                return f"{btc_amount:.8f} BTC"
        elif currency == 'tether':
            usdt_rate = 5.5  # R$ 5,50 por USDT
            usdt_amount = amount / usdt_rate
            return f"{usdt_amount:.2f} USDT"
        elif currency == 'depix':
            depix_rate = 1.0  # R$ 1,00 por DEPIX
            depix_amount = amount / depix_rate
            return f"{depix_amount:.2f} DEPIX"
        
        return "N/A"

# Função para configurar a integração
def setup_trigger_integration(application):
    """Configura integração do sistema de gatilhos com o bot"""
    integration = TriggerBotIntegration(application)
    integration.setup_handlers()
    
    logger.info("✅ Integração do sistema de gatilhos configurada com sucesso!")
    return integration
