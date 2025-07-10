#!/usr/bin/env python3
"""
Sistema de gatilhos simplificado para testes e desenvolvimento
"""
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable

# Adicionar diretório principal ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trigger.config import TriggerEvent, OrderStatus, TriggerConfig

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('simple_trigger_system')

class SimpleOrder:
    """Pedido simplificado"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.status = OrderStatus.CREATED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Dados do pedido
        self.currency = None
        self.network = None
        self.amount = None
        self.payment_method = None
        self.depix_id = None
        self.blockchain_txid = None
        self.lightning_address = None
        self.transaction_result = None
        
    def update_status(self, status: OrderStatus):
        """Atualiza status do pedido"""
        self.status = status
        self.updated_at = datetime.now()
        logger.info(f"📋 Pedido {self.user_id}: {status.value}")
        
    def to_dict(self) -> Dict[str, Any]:
        """Converte pedido para dict"""
        return {
            "user_id": self.user_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "currency": self.currency,
            "network": self.network,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "depix_id": self.depix_id,
            "blockchain_txid": self.blockchain_txid,
            "lightning_address": self.lightning_address,
            "transaction_result": self.transaction_result
        }

class SimpleTriggerSystem:
    """Sistema de gatilhos simplificado"""
    
    def __init__(self):
        self.active_orders: Dict[str, SimpleOrder] = {}
        self.event_handlers: Dict[TriggerEvent, list] = {}
        self.running = False
        
        logger.info("🚀 Simple Trigger System iniciado")
        
    def create_order(self, user_id: str) -> SimpleOrder:
        """Cria um novo pedido"""
        order = SimpleOrder(user_id)
        self.active_orders[user_id] = order
        
        logger.info(f"📋 Novo pedido criado: {user_id}")
        self.trigger_event(TriggerEvent.USER_CLICKED_BUY, user_id)
        
        return order
        
    def get_order(self, user_id: str) -> Optional[SimpleOrder]:
        """Obtém um pedido"""
        return self.active_orders.get(user_id)
        
    def register_handler(self, event: TriggerEvent, handler: Callable):
        """Registra um handler de evento"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
        
    def trigger_event(self, event: TriggerEvent, user_id: str, data: Dict[str, Any] = None):
        """Dispara um evento"""
        if data is None:
            data = {}
            
        logger.info(f"🔔 Evento disparado: {event.value} para {user_id}")
        
        # Chamar handlers registrados
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(user_id, data)
                except Exception as e:
                    logger.error(f"❌ Erro no handler {handler.__name__}: {e}")
                    
    def handle_currency_selection(self, user_id: str, currency: str) -> bool:
        """Manipula seleção de moeda"""
        order = self.get_order(user_id)
        if not order:
            logger.warning(f"⚠️ Pedido não encontrado: {user_id}")
            return False
            
        order.currency = currency
        order.update_status(OrderStatus.CURRENCY_SELECTED)
        
        self.trigger_event(TriggerEvent.CURRENCY_SELECTED, user_id, {"currency": currency})
        return True
        
    def handle_network_selection(self, user_id: str, network: str) -> bool:
        """Manipula seleção de rede"""
        order = self.get_order(user_id)
        if not order:
            logger.warning(f"⚠️ Pedido não encontrado: {user_id}")
            return False
            
        order.network = network
        order.update_status(OrderStatus.NETWORK_SELECTED)
        
        self.trigger_event(TriggerEvent.NETWORK_SELECTED, user_id, {"network": network})
        return True
        
    def handle_amount_entry(self, user_id: str, amount: float) -> bool:
        """Manipula entrada de valor"""
        order = self.get_order(user_id)
        if not order:
            logger.warning(f"⚠️ Pedido não encontrado: {user_id}")
            return False
            
        # Validar valor
        if not self.validate_amount(amount):
            self.trigger_event(TriggerEvent.INVALID_AMOUNT, user_id, {"amount": amount})
            return False
            
        order.amount = amount
        order.update_status(OrderStatus.AMOUNT_ENTERED)
        
        self.trigger_event(TriggerEvent.AMOUNT_ENTERED, user_id, {"amount": amount})
        return True
        
    def handle_payment_method_selection(self, user_id: str, payment_method: str) -> bool:
        """Manipula seleção de método de pagamento"""
        order = self.get_order(user_id)
        if not order:
            logger.warning(f"⚠️ Pedido não encontrado: {user_id}")
            return False
            
        order.payment_method = payment_method
        order.update_status(OrderStatus.PAYMENT_METHOD_SELECTED)
        
        self.trigger_event(TriggerEvent.PAYMENT_METHOD_SELECTED, user_id, {"payment_method": payment_method})
        return True
        
    def handle_pix_payment(self, user_id: str, depix_id: str) -> bool:
        """Manipula pagamento PIX"""
        order = self.get_order(user_id)
        if not order:
            logger.warning(f"⚠️ Pedido não encontrado: {user_id}")
            return False
            
        order.depix_id = depix_id
        order.update_status(OrderStatus.PIX_PAID)
        
        self.trigger_event(TriggerEvent.PIX_PAYMENT_DETECTED, user_id, {"depix_id": depix_id})
        return True
        
    def handle_blockchain_txid(self, user_id: str, blockchain_txid: str) -> bool:
        """Manipula recebimento de blockchain_txid"""
        order = self.get_order(user_id)
        if not order:
            logger.warning(f"⚠️ Pedido não encontrado: {user_id}")
            return False
            
        order.blockchain_txid = blockchain_txid
        order.update_status(OrderStatus.BLOCKCHAIN_TXID_RECEIVED)
        
        self.trigger_event(TriggerEvent.BLOCKCHAIN_TXID_RECEIVED, user_id, {"blockchain_txid": blockchain_txid})
        return True
        
    def handle_address_provided(self, user_id: str, address: str) -> bool:
        """Manipula endereço fornecido"""
        order = self.get_order(user_id)
        if not order:
            logger.warning(f"⚠️ Pedido não encontrado: {user_id}")
            return False
            
        # Validar endereço
        if not self.validate_lightning_address(address):
            self.trigger_event(TriggerEvent.INVALID_ADDRESS, user_id, {"address": address})
            return False
            
        order.lightning_address = address
        order.update_status(OrderStatus.ADDRESS_PROVIDED)
        
        self.trigger_event(TriggerEvent.ADDRESS_PROVIDED, user_id, {"address": address})
        return True
        
    def handle_transaction_completed(self, user_id: str, result: Dict[str, Any]) -> bool:
        """Manipula transação completada"""
        order = self.get_order(user_id)
        if not order:
            logger.warning(f"⚠️ Pedido não encontrado: {user_id}")
            return False
            
        order.transaction_result = result
        order.update_status(OrderStatus.COMPLETED)
        
        self.trigger_event(TriggerEvent.TRANSACTION_COMPLETED, user_id, {"result": result})
        return True
        
    def validate_amount(self, amount: float) -> bool:
        """Valida valor"""
        return TriggerConfig.MIN_AMOUNT <= amount <= TriggerConfig.MAX_AMOUNT
        
    def validate_lightning_address(self, address: str) -> bool:
        """Valida Lightning Address"""
        import re
        pattern = TriggerConfig.LIGHTNING_ADDRESS_REGEX
        return bool(re.match(pattern, address))
        
    def cleanup_old_orders(self):
        """Limpa pedidos antigos"""
        current_time = datetime.now()
        ttl_seconds = TriggerConfig.ACTIVE_ORDERS_TTL
        
        to_remove = []
        for user_id, order in self.active_orders.items():
            if (current_time - order.updated_at).total_seconds() > ttl_seconds:
                to_remove.append(user_id)
                
        for user_id in to_remove:
            del self.active_orders[user_id]
            logger.info(f"🗑️ Pedido expirado removido: {user_id}")
            
    def start(self):
        """Inicia o sistema"""
        self.running = True
        logger.info("✅ Simple Trigger System iniciado")
        
    def stop(self):
        """Para o sistema"""
        self.running = False
        logger.info("🛑 Simple Trigger System parado")
        
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas"""
        return {
            "active_orders": len(self.active_orders),
            "event_handlers": len(self.event_handlers),
            "running": self.running
        }

# Instância global do sistema simplificado
simple_trigger_system = SimpleTriggerSystem()

def test_simple_system():
    """Teste básico do sistema simplificado"""
    print("🧪 Testando Simple Trigger System...")
    
    # Criar pedido
    user_id = "test_user_123"
    order = simple_trigger_system.create_order(user_id)
    
    # Fluxo completo
    simple_trigger_system.handle_currency_selection(user_id, "bitcoin")
    simple_trigger_system.handle_network_selection(user_id, "lightning")
    simple_trigger_system.handle_amount_entry(user_id, 50.0)
    simple_trigger_system.handle_payment_method_selection(user_id, "PIX")
    simple_trigger_system.handle_pix_payment(user_id, "DEPIX_TEST_123")
    simple_trigger_system.handle_blockchain_txid(user_id, "blockchain_tx_123")
    simple_trigger_system.handle_address_provided(user_id, "test@wallet.com")
    simple_trigger_system.handle_transaction_completed(user_id, {"txid": "tx_123"})
    
    # Verificar resultado
    final_order = simple_trigger_system.get_order(user_id)
    print(f"📋 Status final: {final_order.status}")
    print(f"📊 Pedido: {final_order.to_dict()}")
    
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_simple_system()
