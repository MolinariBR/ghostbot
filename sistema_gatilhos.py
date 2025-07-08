#!/usr/bin/env python3
"""
Sistema de Gatilhos Event-Driven para Fluxo de Compra Automático
Substitui cron jobs por eventos imediatos e responsivos
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from enum import Enum

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)8s | [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('trigger_system')

class TriggerEvent(Enum):
    """Tipos de eventos/gatilhos do sistema"""
    USER_CLICKED_BUY = "user_clicked_buy"
    CURRENCY_SELECTED = "currency_selected"
    NETWORK_SELECTED = "network_selected"
    AMOUNT_ENTERED = "amount_entered"
    PAYMENT_METHOD_SELECTED = "payment_method_selected"
    PIX_QR_GENERATED = "pix_qr_generated"
    PIX_PAYMENT_DETECTED = "pix_payment_detected"
    ADDRESS_REQUESTED = "address_requested"
    ADDRESS_PROVIDED = "address_provided"
    CRYPTO_SENT = "crypto_sent"
    TRANSACTION_COMPLETED = "transaction_completed"

class OrderStatus(Enum):
    """Status do pedido"""
    STARTED = "STARTED"
    CURRENCY_SELECTED = "CURRENCY_SELECTED"
    NETWORK_SELECTED = "NETWORK_SELECTED"
    AMOUNT_DEFINED = "AMOUNT_DEFINED"
    PAYMENT_METHOD_SELECTED = "PAYMENT_METHOD_SELECTED"
    PIX_GENERATED = "PIX_GENERATED"
    PIX_PAID = "PIX_PAID"
    ADDRESS_REQUESTED = "ADDRESS_REQUESTED"
    ADDRESS_PROVIDED = "ADDRESS_PROVIDED"
    CRYPTO_SENDING = "CRYPTO_SENDING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class EventTriggerSystem:
    """Sistema principal de gatilhos por eventos"""
    
    def __init__(self):
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.event_handlers = {
            TriggerEvent.USER_CLICKED_BUY: self.handle_buy_clicked,
            TriggerEvent.CURRENCY_SELECTED: self.handle_currency_selected,
            TriggerEvent.NETWORK_SELECTED: self.handle_network_selected,
            TriggerEvent.AMOUNT_ENTERED: self.handle_amount_entered,
            TriggerEvent.PAYMENT_METHOD_SELECTED: self.handle_payment_method_selected,
            TriggerEvent.PIX_QR_GENERATED: self.handle_pix_qr_generated,
            TriggerEvent.PIX_PAYMENT_DETECTED: self.handle_pix_payment_detected,
            TriggerEvent.ADDRESS_REQUESTED: self.handle_address_requested,
            TriggerEvent.ADDRESS_PROVIDED: self.handle_address_provided,
        }
        
    def trigger_event(self, event: TriggerEvent, chat_id: str, data: Dict[str, Any] = None):
        """Dispara um evento específico"""
        logger.info(f"🎯 GATILHO ATIVADO: {event.value} para chat_id {chat_id}")
        
        if data is None:
            data = {}
            
        # Registrar timestamp do evento
        data['timestamp'] = datetime.now().isoformat()
        data['chat_id'] = chat_id
        
        # Executar handler do evento
        try:
            handler = self.event_handlers.get(event)
            if handler:
                result = handler(chat_id, data)
                logger.info(f"✅ Evento {event.value} processado com sucesso")
                return result
            else:
                logger.error(f"❌ Handler não encontrado para evento: {event.value}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao processar evento {event.value}: {str(e)}")
            return False
    
    def get_or_create_order(self, chat_id: str) -> Dict[str, Any]:
        """Obtém ou cria um pedido para o chat_id"""
        if chat_id not in self.active_orders:
            self.active_orders[chat_id] = {
                'chat_id': chat_id,
                'status': OrderStatus.STARTED.value,
                'created_at': datetime.now().isoformat(),
                'events': [],
                'currency': None,
                'network': None,
                'amount': None,
                'payment_method': None,
                'depix_id': None,
                'blockchain_txid': None,
                'user_address': None,
                'voltz_txid': None
            }
            logger.info(f"📋 Novo pedido criado para chat_id {chat_id}")
        
        return self.active_orders[chat_id]
    
    def update_order_status(self, chat_id: str, status: OrderStatus, additional_data: Dict = None):
        """Atualiza status do pedido"""
        order = self.get_or_create_order(chat_id)
        old_status = order['status']
        order['status'] = status.value
        order['updated_at'] = datetime.now().isoformat()
        
        if additional_data:
            order.update(additional_data)
        
        logger.info(f"📊 Status atualizado: {old_status} → {status.value} (chat_id: {chat_id})")
    
    # ============================================================================
    # HANDLERS DOS EVENTOS
    # ============================================================================
    
    def handle_buy_clicked(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Gatilho: Usuário clicou em Comprar"""
        logger.info(f"🛒 Usuário {chat_id} iniciou processo de compra")
        
        order = self.get_or_create_order(chat_id)
        order['events'].append({
            'event': TriggerEvent.USER_CLICKED_BUY.value,
            'timestamp': data['timestamp']
        })
        
        # Enviar menu de seleção de moeda
        self.send_currency_selection_menu(chat_id)
        
        self.update_order_status(chat_id, OrderStatus.STARTED)
        return True
    
    def handle_currency_selected(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Gatilho: Usuário escolheu a moeda"""
        currency = data.get('currency')  # bitcoin, tether, depix
        
        logger.info(f"💰 Usuário {chat_id} selecionou moeda: {currency}")
        
        order = self.get_or_create_order(chat_id)
        order['currency'] = currency
        order['events'].append({
            'event': TriggerEvent.CURRENCY_SELECTED.value,
            'currency': currency,
            'timestamp': data['timestamp']
        })
        
        # Enviar menu de seleção de rede baseado na moeda
        self.send_network_selection_menu(chat_id, currency)
        
        self.update_order_status(chat_id, OrderStatus.CURRENCY_SELECTED, {'currency': currency})
        return True
    
    def handle_network_selected(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Gatilho: Usuário escolheu a rede"""
        network = data.get('network')  # onchain, lightning, liquid, polygon
        
        logger.info(f"🌐 Usuário {chat_id} selecionou rede: {network}")
        
        order = self.get_or_create_order(chat_id)
        order['network'] = network
        order['events'].append({
            'event': TriggerEvent.NETWORK_SELECTED.value,
            'network': network,
            'timestamp': data['timestamp']
        })
        
        # Solicitar valor
        self.send_amount_request(chat_id)
        
        self.update_order_status(chat_id, OrderStatus.NETWORK_SELECTED, {'network': network})
        return True
    
    def handle_amount_entered(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Gatilho: Usuário informou o valor"""
        amount = data.get('amount')
        
        logger.info(f"💵 Usuário {chat_id} informou valor: R$ {amount}")
        
        # Validar valor (10,00 a 4999,99)
        if not (10.00 <= amount <= 4999.99):
            self.send_invalid_amount_message(chat_id)
            return False
        
        order = self.get_or_create_order(chat_id)
        order['amount'] = amount
        order['events'].append({
            'event': TriggerEvent.AMOUNT_ENTERED.value,
            'amount': amount,
            'timestamp': data['timestamp']
        })
        
        # Mostrar resumo do pedido e opções de pagamento
        self.send_order_summary_and_payment_options(chat_id, order)
        
        self.update_order_status(chat_id, OrderStatus.AMOUNT_DEFINED, {'amount': amount})
        return True
    
    def handle_payment_method_selected(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Gatilho: Usuário escolheu método de pagamento"""
        payment_method = data.get('payment_method')  # PIX, TED, Boleto
        
        logger.info(f"💳 Usuário {chat_id} selecionou pagamento: {payment_method}")
        
        order = self.get_or_create_order(chat_id)
        order['payment_method'] = payment_method
        order['events'].append({
            'event': TriggerEvent.PAYMENT_METHOD_SELECTED.value,
            'payment_method': payment_method,
            'timestamp': data['timestamp']
        })
        
        self.update_order_status(chat_id, OrderStatus.PAYMENT_METHOD_SELECTED, {'payment_method': payment_method})
        
        # Se PIX, gerar QR Code imediatamente
        if payment_method == 'PIX':
            self.trigger_event(TriggerEvent.PIX_QR_GENERATED, chat_id, order)
        
        return True
    
    def handle_pix_qr_generated(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Gatilho: QR Code PIX foi gerado"""
        logger.info(f"📱 Gerando QR Code PIX para chat_id {chat_id}")
        
        order = self.get_or_create_order(chat_id)
        
        # Gerar PIX via sistema bancário
        pix_data = self.generate_pix_payment(order)
        
        if pix_data:
            order['depix_id'] = pix_data.get('depix_id')
            order['pix_qr_code'] = pix_data.get('qr_code')
            order['pix_copy_paste'] = pix_data.get('copy_paste')
            
            # Enviar QR Code para usuário
            self.send_pix_qr_code(chat_id, pix_data)
            
            # IMPORTANTE: Iniciar monitoramento do pagamento
            self.start_payment_monitoring(chat_id, pix_data['depix_id'])
            
            self.update_order_status(chat_id, OrderStatus.PIX_GENERATED, {
                'depix_id': pix_data['depix_id'],
                'pix_qr_code': pix_data['qr_code']
            })
            
            return True
        else:
            logger.error(f"❌ Erro ao gerar PIX para chat_id {chat_id}")
            return False
    
    def handle_pix_payment_detected(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Gatilho: Pagamento PIX foi detectado"""
        depix_id = data.get('depix_id')
        blockchain_txid = data.get('blockchain_txid')
        
        logger.info(f"💰 Pagamento PIX detectado: {depix_id} (chat_id: {chat_id})")
        
        order = self.get_or_create_order(chat_id)
        order['blockchain_txid'] = blockchain_txid
        order['events'].append({
            'event': TriggerEvent.PIX_PAYMENT_DETECTED.value,
            'depix_id': depix_id,
            'blockchain_txid': blockchain_txid,
            'timestamp': data['timestamp']
        })
        
        self.update_order_status(chat_id, OrderStatus.PIX_PAID, {'blockchain_txid': blockchain_txid})
        
        # IMPORTANTE: Solicitar endereço do usuário
        self.trigger_event(TriggerEvent.ADDRESS_REQUESTED, chat_id, {'depix_id': depix_id})
        
        return True
    
    def handle_address_requested(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Gatilho: Solicitar endereço do usuário"""
        depix_id = data.get('depix_id')
        
        logger.info(f"📮 Solicitando endereço para chat_id {chat_id} (depix: {depix_id})")
        
        order = self.get_or_create_order(chat_id)
        order['events'].append({
            'event': TriggerEvent.ADDRESS_REQUESTED.value,
            'depix_id': depix_id,
            'timestamp': data['timestamp']
        })
        
        # Enviar solicitação de endereço
        self.send_address_request(chat_id, order)
        
        self.update_order_status(chat_id, OrderStatus.ADDRESS_REQUESTED)
        return True
    
    def handle_address_provided(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Gatilho: Usuário forneceu endereço"""
        user_address = data.get('address')
        
        logger.info(f"📮 Usuário {chat_id} forneceu endereço: {user_address}")
        
        order = self.get_or_create_order(chat_id)
        order['user_address'] = user_address
        order['events'].append({
            'event': TriggerEvent.ADDRESS_PROVIDED.value,
            'address': user_address,
            'timestamp': data['timestamp']
        })
        
        self.update_order_status(chat_id, OrderStatus.ADDRESS_PROVIDED, {'user_address': user_address})
        
        # IMPORTANTE: Enviar cripto via Voltz
        self.send_crypto_via_voltz(chat_id, order)
        
        return True
    
    # ============================================================================
    # MÉTODOS DE INTEGRAÇÃO
    # ============================================================================
    
    def start_payment_monitoring(self, chat_id: str, depix_id: str):
        """Inicia monitoramento do pagamento PIX"""
        logger.info(f"👁️  Iniciando monitoramento de pagamento: {depix_id}")
        
        # Em vez de cron, usar polling inteligente em background
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.monitor_pix_payment(chat_id, depix_id))
            else:
                loop.run_until_complete(self.monitor_pix_payment(chat_id, depix_id))
        except RuntimeError:
            # Se não há loop, criar um novo
            asyncio.run(self.monitor_pix_payment(chat_id, depix_id))
    
    async def monitor_pix_payment(self, chat_id: str, depix_id: str):
        """Monitora pagamento PIX em background (substitui cron)"""
        max_attempts = 120  # 2 horas (60s * 120)
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Consultar Eulen Depix
                payment_status = await self.check_eulen_depix_status(depix_id)
                
                if payment_status and payment_status.get('blockchain_txid'):
                    logger.info(f"✅ Pagamento confirmado: {depix_id}")
                    
                    # Disparar evento de pagamento detectado
                    self.trigger_event(TriggerEvent.PIX_PAYMENT_DETECTED, chat_id, {
                        'depix_id': depix_id,
                        'blockchain_txid': payment_status['blockchain_txid']
                    })
                    return
                
                # Aguardar 60 segundos antes da próxima verificação
                await asyncio.sleep(60)
                attempt += 1
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                await asyncio.sleep(60)
                attempt += 1
        
        logger.warning(f"⏰ Timeout no monitoramento de pagamento: {depix_id}")
    
    async def check_eulen_depix_status(self, depix_id: str) -> Optional[Dict]:
        """Consulta status no Eulen Depix"""
        try:
            # Implementar consulta real à API do Eulen Depix
            # Por enquanto, usar a API atual
            url = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('deposits'):
                    deposit = data['deposits'][0]
                    if deposit.get('blockchainTxID'):
                        return {
                            'blockchain_txid': deposit['blockchainTxID'],
                            'status': deposit.get('status')
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar Eulen Depix: {e}")
            return None
    
    def send_crypto_via_voltz(self, chat_id: str, order: Dict[str, Any]):
        """Envia criptomoeda via Voltz"""
        logger.info(f"🚀 Enviando {order['currency']} via {order['network']} para {order['user_address']}")
        
        try:
            # Implementar envio via Voltz
            voltz_result = self.call_voltz_api(order)
            
            if voltz_result and voltz_result.get('success'):
                order['voltz_txid'] = voltz_result.get('txid')
                
                # Enviar mensagem de sucesso
                self.send_transaction_completed_message(chat_id, voltz_result)
                
                self.update_order_status(chat_id, OrderStatus.COMPLETED, {
                    'voltz_txid': voltz_result.get('txid'),
                    'completed_at': datetime.now().isoformat()
                })
                
                # Limpar pedido da memória
                if chat_id in self.active_orders:
                    del self.active_orders[chat_id]
                
            else:
                logger.error(f"❌ Erro no envio via Voltz: {voltz_result}")
                self.update_order_status(chat_id, OrderStatus.ERROR)
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar via Voltz: {e}")
            self.update_order_status(chat_id, OrderStatus.ERROR)
    
    # ============================================================================
    # MÉTODOS DE INTERFACE (implementar com bot do Telegram)
    # ============================================================================
    
    def send_currency_selection_menu(self, chat_id: str):
        """Envia menu de seleção de moeda"""
        logger.info(f"📤 Enviando menu de moedas para {chat_id}")
        # Implementar envio via bot do Telegram
        pass
    
    def send_network_selection_menu(self, chat_id: str, currency: str):
        """Envia menu de seleção de rede"""
        logger.info(f"📤 Enviando menu de redes para {currency} → {chat_id}")
        # Implementar envio via bot do Telegram
        pass
    
    def send_amount_request(self, chat_id: str):
        """Solicita valor do usuário"""
        logger.info(f"📤 Solicitando valor para {chat_id}")
        # Implementar envio via bot do Telegram
        pass
    
    def send_order_summary_and_payment_options(self, chat_id: str, order: Dict):
        """Envia resumo do pedido e opções de pagamento"""
        logger.info(f"📤 Enviando resumo do pedido para {chat_id}")
        # Implementar envio via bot do Telegram
        pass
    
    def send_pix_qr_code(self, chat_id: str, pix_data: Dict):
        """Envia QR Code PIX"""
        logger.info(f"📤 Enviando QR Code PIX para {chat_id}")
        # Implementar envio via bot do Telegram
        pass
    
    def send_transaction_completed_message(self, chat_id: str, result: Dict):
        """Envia mensagem de transação concluída"""
        logger.info(f"📤 Enviando confirmação de transação para {chat_id}")
        # Implementar envio via bot do Telegram
        pass
    
    def send_invalid_amount_message(self, chat_id: str):
        """Envia mensagem de valor inválido"""
        logger.info(f"📤 Enviando mensagem de valor inválido para {chat_id}")
        # Implementar envio via bot do Telegram
        pass
    
    def send_address_request(self, chat_id: str, order: Dict):
        """Solicita endereço do usuário"""
        logger.info(f"📤 Solicitando endereço para {chat_id}")
        # Implementar envio via bot do Telegram
        pass
    
    # ============================================================================
    # MÉTODOS DE INTEGRAÇÃO EXTERNA
    # ============================================================================
    
    def generate_pix_payment(self, order: Dict[str, Any]) -> Optional[Dict]:
        """Gera pagamento PIX"""
        # Implementar geração PIX real
        return {
            'depix_id': f"dep_{int(time.time())}",
            'qr_code': "fake_qr_code_data",
            'copy_paste': "fake_copy_paste_data"
        }
    
    def call_voltz_api(self, order: Dict[str, Any]) -> Optional[Dict]:
        """Chama API da Voltz para envio"""
        # Implementar chamada real à Voltz
        return {
            'success': True,
            'txid': f"voltz_{int(time.time())}"
        }

# ============================================================================
# INSTÂNCIA GLOBAL DO SISTEMA
# ============================================================================

trigger_system = EventTriggerSystem()

# Exemplo de uso:
if __name__ == "__main__":
    # Simular fluxo completo
    chat_id = "7910260237"
    
    # 1. Usuário clica em comprar
    trigger_system.trigger_event(TriggerEvent.USER_CLICKED_BUY, chat_id)
    
    # 2. Usuário seleciona Bitcoin
    trigger_system.trigger_event(TriggerEvent.CURRENCY_SELECTED, chat_id, {'currency': 'bitcoin'})
    
    # 3. Usuário seleciona Lightning
    trigger_system.trigger_event(TriggerEvent.NETWORK_SELECTED, chat_id, {'network': 'lightning'})
    
    # 4. Usuário informa valor
    trigger_system.trigger_event(TriggerEvent.AMOUNT_ENTERED, chat_id, {'amount': 50.00})
    
    # 5. Usuário escolhe PIX
    trigger_system.trigger_event(TriggerEvent.PAYMENT_METHOD_SELECTED, chat_id, {'payment_method': 'PIX'})
    
    # 6. Simular pagamento detectado
    trigger_system.trigger_event(TriggerEvent.PIX_PAYMENT_DETECTED, chat_id, {
        'depix_id': 'dep_123456',
        'blockchain_txid': 'tx_789'
    })
    
    # 7. Usuário fornece endereço
    trigger_system.trigger_event(TriggerEvent.ADDRESS_PROVIDED, chat_id, {
        'address': 'bouncyflight79@walletofsatoshi.com'
    })
    
    print("✅ Simulação de fluxo completa!")
