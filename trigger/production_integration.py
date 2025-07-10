#!/usr/bin/env python3
"""
Integração do Sistema de Gatilhos para Produção
Conecta o sistema de gatilhos ao bot principal do Ghost Bot
"""
import sys
import os
import logging
from pathlib import Path
from typing import Optional, Tuple

# Adicionar diretório principal ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar logging específico para produção
logger = logging.getLogger('production_integration')

def setup_trigger_integration(application):
    """
    Configura a integração do sistema de gatilhos para produção
    
    Args:
        application: Instância da aplicação do bot Telegram
        
    Returns:
        Tuple[Optional[object], Optional[object]]: (integrator, ui_implementation)
    """
    try:
        logger.info("🚀 Iniciando integração do sistema de gatilhos para produção...")
        
        # Importar componentes do sistema de gatilhos
        from trigger import (
            trigger_system, 
            TriggerEvent, 
            OrderStatus,
            BotTriggerIntegrator,
            TriggerUIImplementation,
            LightningHandler,
            SmartPixMonitor
        )
        
        logger.info("✅ Módulos do sistema de gatilhos importados com sucesso")
        
        # Criar instância do integrador de bot
        logger.info("🔧 Criando integrador de bot...")
        integrator = ProductionBotIntegrator(application, trigger_system)
        
        # Criar implementação da interface do usuário
        logger.info("🎨 Criando implementação da interface...")
        ui_implementation = ProductionTriggerUI(application)
        
        # Ativar Smart PIX Monitor
        logger.info("💰 Ativando Smart PIX Monitor...")
        pix_monitor = SmartPixMonitor()
        pix_monitor.start_monitoring()
        
        # Ativar Lightning Handler
        logger.info("⚡ Ativando Lightning Handler...")
        lightning_handler = LightningHandler()
        
        # Configurar handlers específicos para produção
        setup_production_handlers(application, integrator, ui_implementation)
        
        logger.info("✅ Sistema de gatilhos integrado com sucesso para produção!")
        
        return integrator, ui_implementation
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar integração de gatilhos: {e}", exc_info=True)
        return None, None

def setup_production_handlers(application, integrator, ui_implementation):
    """
    Configura handlers específicos para produção
    
    Args:
        application: Instância da aplicação do bot
        integrator: Integrador de bot
        ui_implementation: Implementação da interface
    """
    try:
        from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
        from trigger import TriggerEvent, trigger_system
        
        # Handler para comando /comprar (substitui menu antigo)
        async def handle_comprar_command(update, context):
            chat_id = str(update.effective_chat.id)
            logger.info(f"🛒 Comando /comprar recebido de {chat_id}")
            
            # Disparar evento de compra no sistema de gatilhos
            trigger_system.trigger_event(
                TriggerEvent.USER_CLICKED_BUY, 
                chat_id
            )
        
        # Handler para seleção de moeda
        async def handle_currency_selection(update, context):
            query = update.callback_query
            await query.answer()
            
            chat_id = str(query.message.chat.id)
            currency = query.data.replace('currency_', '')
            
            logger.info(f"💰 Moeda selecionada: {currency} por {chat_id}")
            
            # Disparar evento de seleção de moeda
            trigger_system.trigger_event(
                TriggerEvent.CURRENCY_SELECTED,
                chat_id,
                {'currency': currency}
            )
        
        # Handler para seleção de rede
        async def handle_network_selection(update, context):
            query = update.callback_query
            await query.answer()
            
            chat_id = str(query.message.chat.id)
            network = query.data.replace('network_', '')
            
            logger.info(f"🌐 Rede selecionada: {network} por {chat_id}")
            
            # Disparar evento de seleção de rede
            trigger_system.trigger_event(
                TriggerEvent.NETWORK_SELECTED,
                chat_id,
                {'network': network}
            )
        
        # Handler para seleção de método de pagamento
        async def handle_payment_method_selection(update, context):
            query = update.callback_query
            await query.answer()
            
            chat_id = str(query.message.chat.id)
            payment_method = query.data.replace('payment_', '')
            
            logger.info(f"💳 Método de pagamento: {payment_method} por {chat_id}")
            
            # Disparar evento de método de pagamento
            trigger_system.trigger_event(
                TriggerEvent.PAYMENT_METHOD_SELECTED,
                chat_id,
                {'payment_method': payment_method}
            )
        
        # Handler para entrada de valor
        async def handle_amount_input(update, context):
            chat_id = str(update.effective_chat.id)
            message_text = update.message.text
            
            # Verificar se o usuário está esperando por valor
            if integrator.is_waiting_for_amount(chat_id):
                try:
                    # Tentar converter para float
                    amount_text = message_text.replace(',', '.')
                    amount = float(amount_text)
                    
                    logger.info(f"💵 Valor informado: R$ {amount} por {chat_id}")
                    
                    # Disparar evento de valor
                    trigger_system.trigger_event(
                        TriggerEvent.AMOUNT_ENTERED,
                        chat_id,
                        {'amount': amount}
                    )
                    
                except ValueError:
                    await update.message.reply_text(
                        "❌ Valor inválido. Digite um número válido (ex: 50.00)"
                    )
        
        # Handler para entrada de endereço
        async def handle_address_input(update, context):
            chat_id = str(update.effective_chat.id)
            address = update.message.text.strip()
            
            # Verificar se o usuário está esperando por endereço
            if integrator.is_waiting_for_address(chat_id):
                logger.info(f"📮 Endereço informado por {chat_id}: {address}")
                
                # Disparar evento de endereço fornecido
                trigger_system.trigger_event(
                    TriggerEvent.ADDRESS_PROVIDED,
                    chat_id,
                    {'address': address}
                )
        
        # Adicionar handlers à aplicação
        application.add_handler(CommandHandler('comprar', handle_comprar_command))
        application.add_handler(CallbackQueryHandler(handle_currency_selection, pattern='^currency_'))
        application.add_handler(CallbackQueryHandler(handle_network_selection, pattern='^network_'))
        application.add_handler(CallbackQueryHandler(handle_payment_method_selection, pattern='^payment_'))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount_input))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address_input))
        
        logger.info("✅ Handlers de produção configurados com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar handlers de produção: {e}", exc_info=True)

class ProductionBotIntegrator:
    """Integrador do bot para produção"""
    
    def __init__(self, application, trigger_system):
        self.application = application
        self.trigger_system = trigger_system
        self.logger = logger
        
    def is_waiting_for_amount(self, chat_id: str) -> bool:
        """Verifica se o usuário deve informar valor"""
        order = self.trigger_system.active_orders.get(chat_id)
        return order and order.get('status') == 'NETWORK_SELECTED'
    
    def is_waiting_for_address(self, chat_id: str) -> bool:
        """Verifica se o usuário deve informar endereço"""
        order = self.trigger_system.active_orders.get(chat_id)
        return order and order.get('status') == 'PIX_PAID'

class ProductionTriggerUI:
    """Implementação da interface do usuário para produção"""
    
    def __init__(self, application):
        self.application = application
        self.logger = logger
        
        # Sobrescrever métodos de interface do sistema de gatilhos
        from trigger import trigger_system
        trigger_system.send_currency_selection_menu = self.send_currency_selection_menu
        trigger_system.send_network_selection_menu = self.send_network_selection_menu
        trigger_system.send_amount_request = self.send_amount_request
        trigger_system.send_order_summary_and_payment_options = self.send_order_summary_and_payment_options
        trigger_system.send_pix_qr_code = self.send_pix_qr_code
        trigger_system.send_transaction_completed_message = self.send_transaction_completed_message
        trigger_system.send_invalid_amount_message = self.send_invalid_amount_message
        
    async def send_currency_selection_menu(self, chat_id: str):
        """Envia menu de seleção de moeda"""
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("₿ Bitcoin", callback_data="currency_bitcoin"),
                InlineKeyboardButton("₮ Tether (USDT)", callback_data="currency_tether")
            ],
            [
                InlineKeyboardButton("💰 DEPIX", callback_data="currency_depix")
            ]
        ])
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text="💰 <b>Escolha a criptomoeda:</b>\n\n"
                 "• <b>Bitcoin (BTC)</b> - A primeira e maior criptomoeda\n"
                 "• <b>Tether (USDT)</b> - Stablecoin pareada ao dólar\n"
                 "• <b>DEPIX</b> - Token nativo brasileiro",
            reply_markup=markup,
            parse_mode='HTML'
        )
    
    async def send_network_selection_menu(self, chat_id: str, currency: str):
        """Envia menu de seleção de rede"""
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        
        markup = InlineKeyboardMarkup()
        
        if currency == 'bitcoin':
            markup.inline_keyboard = [
                [
                    InlineKeyboardButton("⚡ Lightning", callback_data="network_lightning"),
                    InlineKeyboardButton("🔗 On-chain", callback_data="network_onchain")
                ],
                [
                    InlineKeyboardButton("🌊 Liquid", callback_data="network_liquid")
                ]
            ]
        elif currency == 'tether':
            markup.inline_keyboard = [
                [
                    InlineKeyboardButton("🔷 Polygon", callback_data="network_polygon"),
                    InlineKeyboardButton("🌊 Liquid", callback_data="network_liquid")
                ]
            ]
        elif currency == 'depix':
            markup.inline_keyboard = [
                [
                    InlineKeyboardButton("🔷 Polygon", callback_data="network_polygon")
                ]
            ]
        
        networks_info = {
            'bitcoin': "⚡ Lightning - Instantâneo e baixo custo\n🔗 On-chain - Rede principal\n🌊 Liquid - Sidechain rápida",
            'tether': "🔷 Polygon - Rede rápida e barata\n🌊 Liquid - Sidechain do Bitcoin",
            'depix': "🔷 Polygon - Rede nativa do DEPIX"
        }
        
        info_text = f"🌐 <b>Escolha a rede para {currency.upper()}:</b>\n\n{networks_info.get(currency, '')}"
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=info_text,
            reply_markup=markup,
            parse_mode='HTML'
        )
    
    async def send_amount_request(self, chat_id: str):
        """Solicita valor do usuário"""
        await self.application.bot.send_message(
            chat_id=chat_id,
            text="💵 <b>Informe o valor da compra:</b>\n\n"
                 "• Valor mínimo: R$ 10,00\n"
                 "• Valor máximo: R$ 4.999,99\n"
                 "• Formato: 50.00 ou 50,00\n\n"
                 "💡 Digite o valor desejado:",
            parse_mode='HTML'
        )
    
    async def send_order_summary_and_payment_options(self, chat_id: str, order: dict):
        """Envia resumo do pedido e opções de pagamento"""
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        
        currency = order['currency'].upper()
        network = order['network'].upper() if order['network'] else 'N/A'
        amount = order['amount']
        
        # Calcular cotação aproximada
        crypto_amount = self.calculate_crypto_amount(order)
        
        summary_text = (
            f"📋 <b>RESUMO DO PEDIDO</b>\n\n"
            f"💰 Moeda: {currency}\n"
            f"🌐 Rede: {network}\n"
            f"💵 Valor: R$ {amount:.2f}\n"
            f"⚡ Você receberá: ~{crypto_amount}\n\n"
            f"💳 <b>Escolha o método de pagamento:</b>"
        )
        
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📱 PIX (Recomendado)", callback_data="payment_PIX")
            ],
            [
                InlineKeyboardButton("🏦 TED", callback_data="payment_TED"),
                InlineKeyboardButton("📄 Boleto", callback_data="payment_BOLETO")
            ]
        ])
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=summary_text,
            reply_markup=markup,
            parse_mode='HTML'
        )
    
    async def send_pix_qr_code(self, chat_id: str, pix_data: dict):
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
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=qr_text,
            parse_mode='HTML'
        )
        
        # Enviar código Pix Copia e Cola
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=f"📋 <b>PIX Copia e Cola:</b>\n\n"
                 f"<code>{pix_data.get('copy_paste', 'PIX_CODE_HERE')}</code>\n\n"
                 f"👆 Toque para copiar",
            parse_mode='HTML'
        )
    
    async def send_transaction_completed_message(self, chat_id: str, result: dict):
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
        
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=success_text,
            parse_mode='HTML'
        )
    
    async def send_invalid_amount_message(self, chat_id: str):
        """Envia mensagem de valor inválido"""
        await self.application.bot.send_message(
            chat_id=chat_id,
            text="❌ <b>Valor inválido!</b>\n\n"
                 "💵 O valor deve estar entre:\n"
                 "• Mínimo: R$ 10,00\n"
                 "• Máximo: R$ 4.999,99\n\n"
                 "💡 Digite um valor válido:",
            parse_mode='HTML'
        )
    
    def calculate_crypto_amount(self, order: dict) -> str:
        """Calcula quantidade aproximada de crypto"""
        currency = order['currency']
        amount = order['amount']
        
        # Cotações simuladas para cálculo aproximado
        rates = {
            'bitcoin': 300000,  # R$ 300k por BTC
            'tether': 5.5,      # R$ 5,50 por USDT
            'depix': 1.0        # R$ 1,00 por DEPIX
        }
        
        rate = rates.get(currency, 1.0)
        crypto_amount = amount / rate
        
        if currency == 'bitcoin':
            if order.get('network') == 'lightning':
                sats = int(crypto_amount * 100000000)
                return f"{sats} sats"
            else:
                return f"{crypto_amount:.8f} BTC"
        elif currency == 'tether':
            return f"{crypto_amount:.2f} USDT"
        elif currency == 'depix':
            return f"{crypto_amount:.2f} DEPIX"
        
        return "N/A"

if __name__ == "__main__":
    print("✅ Módulo de integração de produção carregado!")
    print("💡 Use setup_trigger_integration(application) para ativar")
