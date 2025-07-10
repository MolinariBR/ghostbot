#!/usr/bin/env python3
"""
Integrador: Sistema de Gatilhos + Bot Telegram
Conecta o sistema de gatilhos event-driven com o bot atual do Telegram
"""
import sys
import os
import logging
import json
from pathlib import Path

# Adicionar diretório principal ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar sistema de gatilhos
try:
    from .sistema_gatilhos import trigger_system, TriggerEvent
except ImportError:
    try:
        from trigger.sistema_gatilhos import trigger_system, TriggerEvent
    except ImportError:
        # Fallback para sistema simplificado
        from trigger.simple_system import simple_trigger_system as trigger_system
        from trigger.config import TriggerEvent

# Importar bot
try:
    from bot import bot
except ImportError:
    print("AVISO: bot não encontrado, usando mock")
    bot = None

# Importar classes do Telegram
try:
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
except ImportError:
    try:
        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    except ImportError:
        # Mock das classes se nenhuma estiver disponível
        class InlineKeyboardMarkup:
            def __init__(self):
                pass
            def row(self, *args):
                pass
        
        class InlineKeyboardButton:
            def __init__(self, text, callback_data=None):
                self.text = text
                self.callback_data = callback_data

logger = logging.getLogger('integrador_bot')

class BotTriggerIntegrator:
    """Integra sistema de gatilhos com bot do Telegram"""
    
    def __init__(self, bot_instance, trigger_system_instance):
        self.bot = bot_instance
        self.trigger_system = trigger_system_instance
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configura handlers do bot para disparar eventos"""
        
        # Handler para comando /comprar
        @self.bot.message_handler(commands=['comprar'])
        def handle_buy_command(message):
            chat_id = str(message.chat.id)
            logger.info(f"🛒 Comando /comprar recebido de {chat_id}")
            
            # Disparar evento de compra
            self.trigger_system.trigger_event(
                TriggerEvent.USER_CLICKED_BUY, 
                chat_id
            )
        
        # Handler para seleção de moeda
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('currency_'))
        def handle_currency_selection(call):
            chat_id = str(call.message.chat.id)
            currency = call.data.replace('currency_', '')
            
            logger.info(f"💰 Moeda selecionada: {currency} por {chat_id}")
            
            # Disparar evento de seleção de moeda
            self.trigger_system.trigger_event(
                TriggerEvent.CURRENCY_SELECTED,
                chat_id,
                {'currency': currency}
            )
            
            # Editar mensagem
            self.bot.edit_message_text(
                f"✅ Moeda selecionada: {currency.upper()}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        
        # Handler para seleção de rede
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('network_'))
        def handle_network_selection(call):
            chat_id = str(call.message.chat.id)
            network = call.data.replace('network_', '')
            
            logger.info(f"🌐 Rede selecionada: {network} por {chat_id}")
            
            # Disparar evento de seleção de rede
            self.trigger_system.trigger_event(
                TriggerEvent.NETWORK_SELECTED,
                chat_id,
                {'network': network}
            )
            
            # Editar mensagem
            self.bot.edit_message_text(
                f"✅ Rede selecionada: {network.upper()}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        
        # Handler para valores
        @self.bot.message_handler(func=lambda message: self.is_waiting_for_amount(message))
        def handle_amount_input(message):
            chat_id = str(message.chat.id)
            
            try:
                # Tentar converter para float
                amount_text = message.text.replace(',', '.')
                amount = float(amount_text)
                
                logger.info(f"💵 Valor informado: R$ {amount} por {chat_id}")
                
                # Disparar evento de valor
                self.trigger_system.trigger_event(
                    TriggerEvent.AMOUNT_ENTERED,
                    chat_id,
                    {'amount': amount}
                )
                
            except ValueError:
                self.bot.send_message(
                    chat_id,
                    "❌ Valor inválido. Digite um número válido (ex: 50.00)"
                )
        
        # Handler para seleção de método de pagamento
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('payment_'))
        def handle_payment_method_selection(call):
            chat_id = str(call.message.chat.id)
            payment_method = call.data.replace('payment_', '')
            
            logger.info(f"💳 Método de pagamento: {payment_method} por {chat_id}")
            
            # Disparar evento de método de pagamento
            self.trigger_system.trigger_event(
                TriggerEvent.PAYMENT_METHOD_SELECTED,
                chat_id,
                {'payment_method': payment_method}
            )
            
            # Editar mensagem
            self.bot.edit_message_text(
                f"✅ Método selecionado: {payment_method}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        
        # Handler para endereços Lightning/crypto
        @self.bot.message_handler(func=lambda message: self.is_waiting_for_address(message))
        def handle_address_input(message):
            chat_id = str(message.chat.id)
            address = message.text.strip()
            
            logger.info(f"📮 Endereço informado por {chat_id}: {address}")
            
            # Disparar evento de endereço fornecido
            self.trigger_system.trigger_event(
                TriggerEvent.ADDRESS_PROVIDED,
                chat_id,
                {'address': address}
            )
    
    def is_waiting_for_amount(self, message):
        """Verifica se o usuário deve informar valor"""
        chat_id = str(message.chat.id)
        order = self.trigger_system.active_orders.get(chat_id)
        
        if order and order['status'] == 'NETWORK_SELECTED':
            return True
        return False
    
    def is_waiting_for_address(self, message):
        """Verifica se o usuário deve informar endereço"""
        chat_id = str(message.chat.id)
        order = self.trigger_system.active_orders.get(chat_id)
        
        if order and order['status'] == 'PIX_PAID':
            return True
        return False

class TriggerUIImplementation:
    """Implementa interface do usuário para o sistema de gatilhos"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        
        # Sobrescrever métodos de interface do sistema de gatilhos
        trigger_system.send_currency_selection_menu = self.send_currency_selection_menu
        trigger_system.send_network_selection_menu = self.send_network_selection_menu
        trigger_system.send_amount_request = self.send_amount_request
        trigger_system.send_order_summary_and_payment_options = self.send_order_summary_and_payment_options
        trigger_system.send_pix_qr_code = self.send_pix_qr_code
        trigger_system.send_transaction_completed_message = self.send_transaction_completed_message
        trigger_system.send_invalid_amount_message = self.send_invalid_amount_message
    
    def send_currency_selection_menu(self, chat_id: str):
        """Envia menu de seleção de moeda"""
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("₿ Bitcoin", callback_data="currency_bitcoin"),
            InlineKeyboardButton("₮ Tether (USDT)", callback_data="currency_tether")
        )
        markup.row(
            InlineKeyboardButton("💰 DEPIX", callback_data="currency_depix")
        )
        
        self.bot.send_message(
            chat_id,
            "💰 <b>Escolha a criptomoeda:</b>\n\n"
            "• <b>Bitcoin (BTC)</b> - A primeira e maior criptomoeda\n"
            "• <b>Tether (USDT)</b> - Stablecoin pareada ao dólar\n"
            "• <b>DEPIX</b> - Token nativo brasileiro",
            reply_markup=markup,
            parse_mode='HTML'
        )
    
    def send_network_selection_menu(self, chat_id: str, currency: str):
        """Envia menu de seleção de rede"""
        markup = InlineKeyboardMarkup()
        
        if currency == 'bitcoin':
            markup.row(
                InlineKeyboardButton("⚡ Lightning", callback_data="network_lightning"),
                InlineKeyboardButton("🔗 On-chain", callback_data="network_onchain")
            )
            markup.row(
                InlineKeyboardButton("🌊 Liquid", callback_data="network_liquid")
            )
        elif currency == 'tether':
            markup.row(
                InlineKeyboardButton("🔷 Polygon", callback_data="network_polygon"),
                InlineKeyboardButton("🌊 Liquid", callback_data="network_liquid")
            )
        elif currency == 'depix':
            markup.row(
                InlineKeyboardButton("🔷 Polygon", callback_data="network_polygon")
            )
        
        networks_info = {
            'bitcoin': {
                'lightning': '⚡ Lightning - Transações instantâneas e taxas baixas',
                'onchain': '🔗 On-chain - Rede principal do Bitcoin',
                'liquid': '🌊 Liquid - Sidechain rápida e confidencial'
            },
            'tether': {
                'polygon': '🔷 Polygon - Rede rápida e taxas baixas',
                'liquid': '🌊 Liquid - Sidechain do Bitcoin'
            },
            'depix': {
                'polygon': '🔷 Polygon - Rede nativa do DEPIX'
            }
        }
        
        info_text = f"🌐 <b>Escolha a rede para {currency.upper()}:</b>\n\n"
        for network, description in networks_info.get(currency, {}).items():
            info_text += f"{description}\n"
        
        self.bot.send_message(
            chat_id,
            info_text,
            reply_markup=markup,
            parse_mode='HTML'
        )
    
    def send_amount_request(self, chat_id: str):
        """Solicita valor do usuário"""
        self.bot.send_message(
            chat_id,
            "💵 <b>Informe o valor da compra:</b>\n\n"
            "• Valor mínimo: R$ 10,00\n"
            "• Valor máximo: R$ 4.999,99\n"
            "• Formato: 50.00 ou 50,00\n\n"
            "💡 Digite o valor desejado:",
            parse_mode='HTML'
        )
    
    def send_order_summary_and_payment_options(self, chat_id: str, order: dict):
        """Envia resumo do pedido e opções de pagamento"""
        currency = order['currency'].upper()
        network = order['network'].upper() if order['network'] else 'N/A'
        amount = order['amount']
        
        # Calcular cotação (simulado)
        crypto_amount = self.calculate_crypto_amount(order)
        
        summary_text = (
            f"📋 <b>RESUMO DO PEDIDO</b>\n\n"
            f"💰 Moeda: {currency}\n"
            f"🌐 Rede: {network}\n"
            f"💵 Valor: R$ {amount:.2f}\n"
            f"⚡ Você receberá: ~{crypto_amount}\n\n"
            f"💳 <b>Escolha o método de pagamento:</b>"
        )
        
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📱 PIX (Recomendado)", callback_data="payment_PIX")
        )
        markup.row(
            InlineKeyboardButton("🏦 TED", callback_data="payment_TED"),
            InlineKeyboardButton("📄 Boleto", callback_data="payment_BOLETO")
        )
        
        self.bot.send_message(
            chat_id,
            summary_text,
            reply_markup=markup,
            parse_mode='HTML'
        )
    
    def send_pix_qr_code(self, chat_id: str, pix_data: dict):
        """Envia QR Code PIX"""
        qr_text = (
            f"📱 <b>PAGAMENTO PIX GERADO</b>\n\n"
            f"🎯 ID do Pedido: <code>{pix_data['depix_id']}</code>\n"
            f"💰 Valor: R$ {pix_data.get('amount', '5.00')}\n\n"
            f"📋 <b>Para pagar:</b>\n"
            f"1. Abra seu app bancário\n"
            f"2. Escaneie o QR Code abaixo\n"
            f"3. Ou use o código Pix Copia e Cola\n\n"
            f"⏰ O pagamento será detectado automaticamente!\n"
            f"💡 Após o pagamento, você receberá uma mensagem solicitando seu endereço."
        )
        
        # Enviar QR Code (implementar geração real)
        self.bot.send_message(
            chat_id,
            qr_text,
            parse_mode='HTML'
        )
        
        # Enviar código Pix Copia e Cola
        self.bot.send_message(
            chat_id,
            f"📋 <b>PIX Copia e Cola:</b>\n\n"
            f"<code>{pix_data.get('copy_paste', 'PIX_CODE_HERE')}</code>\n\n"
            f"👆 Toque para copiar",
            parse_mode='HTML'
        )
    
    def send_transaction_completed_message(self, chat_id: str, result: dict):
        """Envia mensagem de transação concluída"""
        success_text = (
            f"🎉 <b>TRANSAÇÃO CONCLUÍDA!</b>\n\n"
            f"✅ Sua criptomoeda foi enviada com sucesso!\n\n"
            f"🔗 <b>ID da Transação:</b>\n"
            f"<code>{result.get('txid', 'TX_ID_HERE')}</code>\n\n"
            f"💡 <b>Confira na sua carteira!</b>\n"
            f"A transação pode levar alguns minutos para aparecer.\n\n"
            f"📱 Para nova compra, use /comprar novamente."
        )
        
        self.bot.send_message(
            chat_id,
            success_text,
            parse_mode='HTML'
        )
    
    def send_invalid_amount_message(self, chat_id: str):
        """Envia mensagem de valor inválido"""
        self.bot.send_message(
            chat_id,
            "❌ <b>Valor inválido!</b>\n\n"
            "💵 O valor deve estar entre:\n"
            "• Mínimo: R$ 10,00\n"
            "• Máximo: R$ 4.999,99\n\n"
            "💡 Digite um valor válido:",
            parse_mode='HTML'
        )
    
    def calculate_crypto_amount(self, order: dict) -> str:
        """Calcula quantidade de crypto baseada no valor em reais"""
        # Implementar cálculo real baseado em cotações
        currency = order['currency']
        amount = order['amount']
        
        if currency == 'bitcoin':
            # Simular cotação Bitcoin
            btc_rate = 300000  # R$ 300k por BTC
            btc_amount = amount / btc_rate
            if order['network'] == 'lightning':
                sats = int(btc_amount * 100000000)
                return f"{sats} sats"
            else:
                return f"{btc_amount:.8f} BTC"
        elif currency == 'tether':
            # Simular cotação USDT
            usdt_rate = 5.5  # R$ 5,50 por USDT
            usdt_amount = amount / usdt_rate
            return f"{usdt_amount:.2f} USDT"
        elif currency == 'depix':
            # Simular cotação DEPIX
            depix_rate = 1.0  # R$ 1,00 por DEPIX
            depix_amount = amount / depix_rate
            return f"{depix_amount:.2f} DEPIX"
        
        return "N/A"

# Função para ativar o sistema integrado
def activate_trigger_system():
    """Ativa o sistema de gatilhos integrado com o bot"""
    logger.info("🚀 Ativando sistema de gatilhos integrado...")
    
    # Integrar handlers
    integrator = BotTriggerIntegrator(bot, trigger_system)
    
    # Implementar interface
    ui_implementation = TriggerUIImplementation(bot)
    
    logger.info("✅ Sistema de gatilhos ativado com sucesso!")
    
    return integrator, ui_implementation

if __name__ == "__main__":
    # Testar integração
    activate_trigger_system()
    print("✅ Integração pronta para uso!")
    print("💡 Use /comprar no bot para testar o novo fluxo")
