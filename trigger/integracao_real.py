#!/usr/bin/env python3
"""
Integração Real: Sistema de Gatilhos + Bot Telegram Atual
Conecta o sistema de gatilhos com o bot existente em produção
"""
import sys
import os
sys.path.append('/home/mau/bot/ghost')

# Importar módulos existentes
from sistema_gatilhos import trigger_system, TriggerEvent, OrderStatus
import logging
from datetime import datetime
import requests
import json

# Configurar logging
logger = logging.getLogger('integrador_real')

class RealBotIntegration:
    """Integração real com bot do Telegram existente"""
    
    def __init__(self):
        self.base_url = "https://useghost.squareweb.app"
        self.active_users = set()  # Users ativos no novo sistema
        self.migration_enabled = False
        
        # Conectar métodos de interface do sistema de gatilhos
        self.setup_ui_methods()
    
    def setup_ui_methods(self):
        """Conecta métodos de UI do sistema de gatilhos com implementações reais"""
        trigger_system.send_currency_selection_menu = self.send_currency_selection_menu
        trigger_system.send_network_selection_menu = self.send_network_selection_menu
        trigger_system.send_amount_request = self.send_amount_request
        trigger_system.send_order_summary_and_payment_options = self.send_order_summary_and_payment_options
        trigger_system.send_pix_qr_code = self.send_pix_qr_code
        trigger_system.send_address_request = self.send_address_request
        trigger_system.send_transaction_completed_message = self.send_transaction_completed_message
        trigger_system.send_invalid_amount_message = self.send_invalid_amount_message
    
    def enable_for_user(self, chat_id: str):
        """Ativa novo sistema para usuário específico"""
        self.active_users.add(chat_id)
        logger.info(f"✅ Sistema de gatilhos ativado para usuário {chat_id}")
    
    def disable_for_user(self, chat_id: str):
        """Desativa novo sistema para usuário específico"""
        self.active_users.discard(chat_id)
        logger.info(f"❌ Sistema de gatilhos desativado para usuário {chat_id}")
    
    def is_enabled_for_user(self, chat_id: str) -> bool:
        """Verifica se novo sistema está ativo para o usuário"""
        return str(chat_id) in self.active_users or self.migration_enabled
    
    def enable_global_migration(self):
        """Ativa migração global para todos os usuários"""
        self.migration_enabled = True
        logger.info("🌍 Migração global ativada - todos os usuários usarão sistema de gatilhos")
    
    def disable_global_migration(self):
        """Desativa migração global"""
        self.migration_enabled = False
        logger.info("🌍 Migração global desativada - apenas usuários específicos")
    
    # ============================================================================
    # MÉTODOS DE INTERFACE COM TELEGRAM
    # ============================================================================
    
    def send_telegram_message(self, chat_id: str, text: str, reply_markup=None, parse_mode='HTML'):
        """Envia mensagem via API do Telegram"""
        try:
            # Usar API do bot existente
            bot_api_url = f"{self.base_url}/api/send_message.php"
            
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
            
            response = requests.post(bot_api_url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"📤 Mensagem enviada para {chat_id}")
                return True
            else:
                logger.error(f"❌ Erro ao enviar mensagem: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na API Telegram: {e}")
            return False
    
    def send_currency_selection_menu(self, chat_id: str):
        """Envia menu de seleção de moeda"""
        text = (
            "💰 <b>Escolha a criptomoeda para comprar:</b>\n\n"
            "🟠 <b>Bitcoin (BTC)</b>\n"
            "   • A primeira e maior criptomoeda\n"
            "   • Redes: Lightning, On-chain, Liquid\n\n"
            "🟢 <b>Tether (USDT)</b>\n" 
            "   • Stablecoin pareada ao dólar americano\n"
            "   • Redes: Polygon, Liquid\n\n"
            "🔵 <b>DEPIX</b>\n"
            "   • Token brasileiro inovador\n"
            "   • Rede: Polygon\n\n"
            "👆 Selecione uma opção abaixo:"
        )
        
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "₿ Bitcoin", "callback_data": "trig_currency_bitcoin"},
                    {"text": "₮ Tether", "callback_data": "trig_currency_tether"}
                ],
                [
                    {"text": "💰 DEPIX", "callback_data": "trig_currency_depix"}
                ]
            ]
        }
        
        self.send_telegram_message(chat_id, text, reply_markup)
    
    def send_network_selection_menu(self, chat_id: str, currency: str):
        """Envia menu de seleção de rede"""
        networks = {
            'bitcoin': {
                'text': "🌐 <b>Escolha a rede para Bitcoin:</b>\n\n"
                        "⚡ <b>Lightning Network</b>\n"
                        "   • Transações instantâneas\n"
                        "   • Taxas muito baixas\n"
                        "   • Ideal para pequenos valores\n\n"
                        "🔗 <b>On-chain (Bitcoin)</b>\n"
                        "   • Rede principal do Bitcoin\n"
                        "   • Mais segura\n"
                        "   • Taxas variáveis\n\n"
                        "🌊 <b>Liquid Network</b>\n"
                        "   • Sidechain rápida\n"
                        "   • Transações confidenciais\n"
                        "   • Taxas baixas",
                'keyboard': [
                    [
                        {"text": "⚡ Lightning", "callback_data": "trig_network_lightning"},
                        {"text": "🔗 On-chain", "callback_data": "trig_network_onchain"}
                    ],
                    [
                        {"text": "🌊 Liquid", "callback_data": "trig_network_liquid"}
                    ]
                ]
            },
            'tether': {
                'text': "🌐 <b>Escolha a rede para USDT:</b>\n\n"
                        "🔷 <b>Polygon</b>\n"
                        "   • Transações rápidas\n"
                        "   • Taxas muito baixas\n"
                        "   • Rede principal para USDT\n\n"
                        "🌊 <b>Liquid Network</b>\n"
                        "   • Sidechain do Bitcoin\n"
                        "   • Transações confidenciais\n"
                        "   • Alternativa inovadora",
                'keyboard': [
                    [
                        {"text": "🔷 Polygon", "callback_data": "trig_network_polygon"},
                        {"text": "🌊 Liquid", "callback_data": "trig_network_liquid"}
                    ]
                ]
            },
            'depix': {
                'text': "🌐 <b>Rede para DEPIX:</b>\n\n"
                        "🔷 <b>Polygon</b>\n"
                        "   • Rede nativa do DEPIX\n"
                        "   • Transações rápidas\n"
                        "   • Taxas baixas\n"
                        "   • Ecossistema brasileiro",
                'keyboard': [
                    [
                        {"text": "🔷 Polygon", "callback_data": "trig_network_polygon"}
                    ]
                ]
            }
        }
        
        network_info = networks.get(currency)
        if network_info:
            reply_markup = {"inline_keyboard": network_info['keyboard']}
            self.send_telegram_message(chat_id, network_info['text'], reply_markup)
    
    def send_amount_request(self, chat_id: str):
        """Solicita valor do usuário"""
        text = (
            "💵 <b>Informe o valor da compra em reais:</b>\n\n"
            "📊 <b>Limites:</b>\n"
            "   • Valor mínimo: R$ 10,00\n"
            "   • Valor máximo: R$ 4.999,99\n\n"
            "💡 <b>Exemplos válidos:</b>\n"
            "   • 50\n"
            "   • 50.00\n"
            "   • 50,00\n"
            "   • 1000\n\n"
            "💰 Digite o valor desejado:"
        )
        
        self.send_telegram_message(chat_id, text)
    
    def send_order_summary_and_payment_options(self, chat_id: str, order: dict):
        """Envia resumo do pedido e opções de pagamento"""
        currency_names = {
            'bitcoin': 'Bitcoin (BTC)',
            'tether': 'Tether (USDT)', 
            'depix': 'DEPIX'
        }
        
        network_names = {
            'lightning': 'Lightning Network',
            'onchain': 'Bitcoin On-chain',
            'liquid': 'Liquid Network',
            'polygon': 'Polygon'
        }
        
        # Calcular cotação (implementar função real)
        crypto_amount = self.calculate_crypto_amount(order)
        
        text = (
            f"📋 <b>RESUMO DO SEU PEDIDO</b>\n\n"
            f"💰 <b>Moeda:</b> {currency_names.get(order['currency'], order['currency'])}\n"
            f"🌐 <b>Rede:</b> {network_names.get(order['network'], order['network'])}\n"
            f"💵 <b>Valor:</b> R$ {order['amount']:.2f}\n"
            f"⚡ <b>Você receberá:</b> ~{crypto_amount}\n\n"
            f"💳 <b>Escolha o método de pagamento:</b>\n\n"
            f"📱 <b>PIX (Recomendado)</b>\n"
            f"   • Confirmação instantânea\n"
            f"   • Disponível 24/7\n"
            f"   • Sem taxas adicionais\n\n"
            f"🏦 <b>TED</b>\n"
            f"   • Horário bancário\n"
            f"   • Confirmação em até 30 min\n\n"
            f"📄 <b>Boleto</b>\n"
            f"   • Confirmação em até 3 dias úteis\n"
            f"   • Válido por 3 dias"
        )
        
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "📱 PIX (Recomendado)", "callback_data": "trig_payment_PIX"}
                ],
                [
                    {"text": "🏦 TED", "callback_data": "trig_payment_TED"},
                    {"text": "📄 Boleto", "callback_data": "trig_payment_BOLETO"}
                ]
            ]
        }
        
        self.send_telegram_message(chat_id, text, reply_markup)
    
    def send_pix_qr_code(self, chat_id: str, pix_data: dict):
        """Envia QR Code PIX"""
        text = (
            f"📱 <b>PIX GERADO COM SUCESSO!</b>\n\n"
            f"🎯 <b>ID do Pedido:</b> <code>{pix_data['depix_id']}</code>\n"
            f"💰 <b>Valor:</b> R$ {pix_data.get('amount', 0):.2f}\n\n"
            f"📋 <b>Como pagar:</b>\n"
            f"1️⃣ Abra seu app bancário\n"
            f"2️⃣ Escaneie o QR Code ou use Pix Copia e Cola\n"
            f"3️⃣ Confirme o pagamento\n\n"
            f"⏱️ <b>O pagamento será detectado automaticamente!</b>\n"
            f"📢 Após confirmação, solicitaremos seu endereço crypto.\n\n"
            f"⏰ <b>Válido por:</b> 30 minutos"
        )
        
        self.send_telegram_message(chat_id, text)
        
        # Enviar código Pix Copia e Cola
        if pix_data.get('copy_paste'):
            copy_paste_text = (
                f"📋 <b>PIX COPIA E COLA:</b>\n\n"
                f"<code>{pix_data['copy_paste']}</code>\n\n"
                f"👆 Toque na mensagem acima para copiar"
            )
            self.send_telegram_message(chat_id, copy_paste_text)
    
    def send_address_request(self, chat_id: str, order: dict):
        """Solicita endereço crypto do usuário"""
        currency = order['currency']
        network = order['network']
        
        examples = {
            'bitcoin': {
                'lightning': 'usuario@walletofsatoshi.com',
                'onchain': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
                'liquid': 'lq1qq0q4jts5fzywm9vujl0yv9kzj8av3qr3yz9eh9z9uqyf'
            },
            'tether': {
                'polygon': '0x742dF94C5C3b4c6D3B9A8E1f7b3e1d74F7B8c9D5',
                'liquid': 'lq1qq0q4jts5fzywm9vujl0yv9kzj8av3qr3yz9eh9z9uqyf'
            },
            'depix': {
                'polygon': '0x742dF94C5C3b4c6D3B9A8E1f7b3e1d74F7B8c9D5'
            }
        }
        
        example_address = examples.get(currency, {}).get(network, 'endereço_exemplo')
        
        text = (
            f"📮 <b>PAGAMENTO CONFIRMADO!</b>\n\n"
            f"✅ Seu PIX foi processado com sucesso.\n"
            f"🎯 Agora preciso do seu endereço para envio.\n\n"
            f"📝 <b>Envie seu endereço {currency.upper()} ({network.upper()}):</b>\n\n"
            f"💡 <b>Exemplo:</b>\n"
            f"<code>{example_address}</code>\n\n"
            f"⚠️ <b>IMPORTANTE:</b>\n"
            f"• Verifique se o endereço está correto\n"
            f"• Use apenas endereços da rede {network.upper()}\n"
            f"• Transações não podem ser revertidas\n\n"
            f"📱 Digite ou cole seu endereço:"
        )
        
        self.send_telegram_message(chat_id, text)
    
    def send_transaction_completed_message(self, chat_id: str, result: dict):
        """Envia mensagem de transação concluída"""
        text = (
            f"🎉 <b>TRANSAÇÃO CONCLUÍDA COM SUCESSO!</b>\n\n"
            f"✅ Sua criptomoeda foi enviada!\n\n"
            f"🔗 <b>ID da Transação:</b>\n"
            f"<code>{result.get('txid', 'N/A')}</code>\n\n"
        )
        
        if result.get('amount_sent'):
            text += f"💰 <b>Valor enviado:</b> {result['amount_sent']}\n"
        
        if result.get('fee'):
            text += f"💳 <b>Taxa de rede:</b> {result['fee']}\n"
        
        text += (
            f"\n📱 <b>Verifique sua carteira!</b>\n"
            f"A transação pode levar alguns minutos para aparecer.\n\n"
            f"🔄 <b>Para nova compra:</b> /comprar\n"
            f"📞 <b>Suporte:</b> /ajuda"
        )
        
        self.send_telegram_message(chat_id, text)
    
    def send_invalid_amount_message(self, chat_id: str):
        """Envia mensagem de valor inválido"""
        text = (
            "❌ <b>Valor inválido!</b>\n\n"
            "💵 <b>Limites permitidos:</b>\n"
            "   • Mínimo: R$ 10,00\n"
            "   • Máximo: R$ 4.999,99\n\n"
            "💡 <b>Exemplos válidos:</b>\n"
            "   • 25\n"
            "   • 100.50\n"
            "   • 500,00\n\n"
            "🔄 Digite um valor válido:"
        )
        
        self.send_telegram_message(chat_id, text)
    
    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================
    
    def calculate_crypto_amount(self, order: dict) -> str:
        """Calcula quantidade de crypto baseada no valor em reais"""
        try:
            # Consultar cotações reais via API
            cotacao_url = f"{self.base_url}/api/cotacao.php"
            response = requests.get(f"{cotacao_url}?currency={order['currency']}", timeout=5)
            
            if response.status_code == 200:
                cotacao_data = response.json()
                rate = cotacao_data.get('rate_brl', 1.0)
                
                amount_brl = order['amount']
                crypto_amount = amount_brl / rate
                
                if order['currency'] == 'bitcoin':
                    if order['network'] == 'lightning':
                        sats = int(crypto_amount * 100000000)
                        return f"{sats:,} sats"
                    else:
                        return f"{crypto_amount:.8f} BTC"
                elif order['currency'] == 'tether':
                    return f"{crypto_amount:.2f} USDT"
                elif order['currency'] == 'depix':
                    return f"{crypto_amount:.2f} DEPIX"
            
            # Fallback se API não responder
            return "Calculando..."
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular cotação: {e}")
            return "Cotação indisponível"
    
    # ============================================================================
    # MÉTODOS DE MIGRAÇÃO
    # ============================================================================
    
    def handle_legacy_command(self, chat_id: str, command: str, message_data: dict = None):
        """Intercepta comandos do sistema legado e redireciona para gatilhos"""
        if not self.is_enabled_for_user(chat_id):
            return False  # Deixar sistema legado processar
        
        logger.info(f"🔄 Interceptando comando legado '{command}' para {chat_id}")
        
        if command == '/comprar' or command == 'comprar':
            trigger_system.trigger_event(TriggerEvent.USER_CLICKED_BUY, str(chat_id))
            return True
        
        return False
    
    def handle_legacy_callback(self, chat_id: str, callback_data: str):
        """Intercepta callbacks do sistema legado"""
        if not self.is_enabled_for_user(chat_id):
            return False
        
        logger.info(f"🔄 Interceptando callback '{callback_data}' para {chat_id}")
        
        # Converter callbacks legados para eventos de gatilho
        if callback_data.startswith('trig_currency_'):
            currency = callback_data.replace('trig_currency_', '')
            trigger_system.trigger_event(TriggerEvent.CURRENCY_SELECTED, str(chat_id), {'currency': currency})
            return True
        
        elif callback_data.startswith('trig_network_'):
            network = callback_data.replace('trig_network_', '')
            trigger_system.trigger_event(TriggerEvent.NETWORK_SELECTED, str(chat_id), {'network': network})
            return True
        
        elif callback_data.startswith('trig_payment_'):
            payment_method = callback_data.replace('trig_payment_', '')
            trigger_system.trigger_event(TriggerEvent.PAYMENT_METHOD_SELECTED, str(chat_id), {'payment_method': payment_method})
            return True
        
        return False
    
    def handle_legacy_message(self, chat_id: str, message_text: str):
        """Intercepta mensagens de texto do sistema legado"""
        if not self.is_enabled_for_user(chat_id):
            return False
        
        # Verificar se usuário está aguardando valor
        order = trigger_system.active_orders.get(str(chat_id))
        if order and order['status'] == OrderStatus.NETWORK_SELECTED.value:
            try:
                amount = float(message_text.replace(',', '.'))
                trigger_system.trigger_event(TriggerEvent.AMOUNT_ENTERED, str(chat_id), {'amount': amount})
                return True
            except ValueError:
                self.send_invalid_amount_message(str(chat_id))
                return True
        
        # Verificar se usuário está aguardando endereço
        if order and order['status'] == OrderStatus.ADDRESS_REQUESTED.value:
            trigger_system.trigger_event(TriggerEvent.ADDRESS_PROVIDED, str(chat_id), {'address': message_text.strip()})
            return True
        
        return False

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================
real_integration = RealBotIntegration()

# Função para ativar integração
def activate_real_integration():
    """Ativa integração real com APIs"""
    logger.info("🚀 Ativando integração real com APIs...")
    return real_integration

if __name__ == "__main__":
    # Teste da integração
    integration = activate_real_integration()
    
    # Ativar para usuário de teste
    integration.enable_for_user("7910260237")
    
    print("✅ Integração real ativada!")
    print("💡 Use integration.enable_for_user(chat_id) para ativar para usuários específicos")
