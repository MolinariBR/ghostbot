#!/usr/bin/env python3
"""
Testes para o sistema de gatilhos
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Adicionar diretório principal ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar módulos do sistema
from trigger.config import TriggerEvent, OrderStatus, TriggerConfig
from trigger.sistema_gatilhos import TriggerSystem, Order

class TestTriggerSystem(unittest.TestCase):
    """Testes para o sistema de gatilhos"""
    
    def setUp(self):
        """Configurar testes"""
        self.trigger_system = TriggerSystem()
        self.test_user_id = "test_user_123"
        
    def test_create_order(self):
        """Testar criação de pedido"""
        order = self.trigger_system.create_order(self.test_user_id)
        
        self.assertIsNotNone(order)
        self.assertEqual(order.user_id, self.test_user_id)
        self.assertEqual(order.status, OrderStatus.CREATED)
        self.assertIn(self.test_user_id, self.trigger_system.active_orders)
        
    def test_currency_selection(self):
        """Testar seleção de moeda"""
        # Criar pedido
        order = self.trigger_system.create_order(self.test_user_id)
        
        # Selecionar moeda
        self.trigger_system.handle_currency_selection(self.test_user_id, "bitcoin")
        
        # Verificar se foi atualizado
        updated_order = self.trigger_system.get_order(self.test_user_id)
        self.assertEqual(updated_order.currency, "bitcoin")
        self.assertEqual(updated_order.status, OrderStatus.CURRENCY_SELECTED)
        
    def test_network_selection(self):
        """Testar seleção de rede"""
        # Criar pedido e selecionar moeda
        order = self.trigger_system.create_order(self.test_user_id)
        self.trigger_system.handle_currency_selection(self.test_user_id, "bitcoin")
        
        # Selecionar rede
        self.trigger_system.handle_network_selection(self.test_user_id, "lightning")
        
        # Verificar se foi atualizado
        updated_order = self.trigger_system.get_order(self.test_user_id)
        self.assertEqual(updated_order.network, "lightning")
        self.assertEqual(updated_order.status, OrderStatus.NETWORK_SELECTED)
        
    def test_amount_validation(self):
        """Testar validação de valor"""
        # Criar pedido
        order = self.trigger_system.create_order(self.test_user_id)
        
        # Testar valor válido
        result = self.trigger_system.validate_amount(50.0)
        self.assertTrue(result)
        
        # Testar valor muito baixo
        result = self.trigger_system.validate_amount(5.0)
        self.assertFalse(result)
        
        # Testar valor muito alto
        result = self.trigger_system.validate_amount(5000.0)
        self.assertFalse(result)
        
    def test_amount_entry(self):
        """Testar entrada de valor"""
        # Criar pedido e configurar
        order = self.trigger_system.create_order(self.test_user_id)
        self.trigger_system.handle_currency_selection(self.test_user_id, "bitcoin")
        self.trigger_system.handle_network_selection(self.test_user_id, "lightning")
        
        # Informar valor
        self.trigger_system.handle_amount_entry(self.test_user_id, 50.0)
        
        # Verificar se foi atualizado
        updated_order = self.trigger_system.get_order(self.test_user_id)
        self.assertEqual(updated_order.amount, 50.0)
        self.assertEqual(updated_order.status, OrderStatus.AMOUNT_ENTERED)
        
    def test_payment_method_selection(self):
        """Testar seleção de método de pagamento"""
        # Criar pedido e configurar
        order = self.trigger_system.create_order(self.test_user_id)
        self.trigger_system.handle_currency_selection(self.test_user_id, "bitcoin")
        self.trigger_system.handle_network_selection(self.test_user_id, "lightning")
        self.trigger_system.handle_amount_entry(self.test_user_id, 50.0)
        
        # Selecionar método de pagamento
        self.trigger_system.handle_payment_method_selection(self.test_user_id, "PIX")
        
        # Verificar se foi atualizado
        updated_order = self.trigger_system.get_order(self.test_user_id)
        self.assertEqual(updated_order.payment_method, "PIX")
        self.assertEqual(updated_order.status, OrderStatus.PAYMENT_METHOD_SELECTED)
        
    def test_address_validation(self):
        """Testar validação de endereço"""
        # Testar Lightning Address válido
        valid_address = "user@wallet.com"
        result = self.trigger_system.validate_lightning_address(valid_address)
        self.assertTrue(result)
        
        # Testar Lightning Address inválido
        invalid_address = "invalid_address"
        result = self.trigger_system.validate_lightning_address(invalid_address)
        self.assertFalse(result)
        
    def test_order_completion(self):
        """Testar conclusão de pedido"""
        # Criar pedido completo
        order = self.trigger_system.create_order(self.test_user_id)
        self.trigger_system.handle_currency_selection(self.test_user_id, "bitcoin")
        self.trigger_system.handle_network_selection(self.test_user_id, "lightning")
        self.trigger_system.handle_amount_entry(self.test_user_id, 50.0)
        self.trigger_system.handle_payment_method_selection(self.test_user_id, "PIX")
        
        # Simular pagamento PIX
        self.trigger_system.handle_pix_payment(self.test_user_id, "DEPIX_123")
        
        # Informar endereço
        self.trigger_system.handle_address_provided(self.test_user_id, "user@wallet.com")
        
        # Completar transação
        self.trigger_system.handle_transaction_completed(self.test_user_id, {"txid": "tx123"})
        
        # Verificar se foi completado
        updated_order = self.trigger_system.get_order(self.test_user_id)
        self.assertEqual(updated_order.status, OrderStatus.COMPLETED)
        
    def test_event_handlers(self):
        """Testar registro e disparo de handlers"""
        # Mock handler
        mock_handler = Mock()
        
        # Registrar handler
        self.trigger_system.register_handler(TriggerEvent.CURRENCY_SELECTED, mock_handler)
        
        # Disparar evento
        self.trigger_system.trigger_event(TriggerEvent.CURRENCY_SELECTED, self.test_user_id, {"currency": "bitcoin"})
        
        # Verificar se handler foi chamado
        mock_handler.assert_called_once()
        
    def test_order_cleanup(self):
        """Testar limpeza de pedidos antigos"""
        # Criar pedido
        order = self.trigger_system.create_order(self.test_user_id)
        
        # Verificar se existe
        self.assertIsNotNone(self.trigger_system.get_order(self.test_user_id))
        
        # Limpar pedidos
        self.trigger_system.cleanup_old_orders()
        
        # Verificar se ainda existe (deve existir pois é recente)
        self.assertIsNotNone(self.trigger_system.get_order(self.test_user_id))
        
    def test_error_handling(self):
        """Testar tratamento de erros"""
        # Tentar obter pedido inexistente
        order = self.trigger_system.get_order("inexistent_user")
        self.assertIsNone(order)
        
        # Tentar atualizar pedido inexistente
        result = self.trigger_system.handle_currency_selection("inexistent_user", "bitcoin")
        self.assertFalse(result)

class TestOrder(unittest.TestCase):
    """Testes para a classe Order"""
    
    def setUp(self):
        """Configurar testes"""
        self.order = Order("test_user_123")
        
    def test_order_creation(self):
        """Testar criação de pedido"""
        self.assertEqual(self.order.user_id, "test_user_123")
        self.assertEqual(self.order.status, OrderStatus.CREATED)
        self.assertIsNotNone(self.order.created_at)
        
    def test_order_update(self):
        """Testar atualização de pedido"""
        self.order.update_status(OrderStatus.CURRENCY_SELECTED)
        self.assertEqual(self.order.status, OrderStatus.CURRENCY_SELECTED)
        
    def test_order_to_dict(self):
        """Testar conversão para dict"""
        self.order.currency = "bitcoin"
        self.order.network = "lightning"
        self.order.amount = 50.0
        
        order_dict = self.order.to_dict()
        
        self.assertEqual(order_dict["user_id"], "test_user_123")
        self.assertEqual(order_dict["currency"], "bitcoin")
        self.assertEqual(order_dict["network"], "lightning")
        self.assertEqual(order_dict["amount"], 50.0)
        
    def test_order_validation(self):
        """Testar validação de pedido"""
        # Pedido incompleto
        self.assertFalse(self.order.is_valid())
        
        # Completar pedido
        self.order.currency = "bitcoin"
        self.order.network = "lightning"
        self.order.amount = 50.0
        self.order.payment_method = "PIX"
        
        # Deve ser válido agora
        self.assertTrue(self.order.is_valid())

if __name__ == "__main__":
    # Executar testes
    unittest.main(verbosity=2)
