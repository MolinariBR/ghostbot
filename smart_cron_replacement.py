#!/usr/bin/env python3
"""
Substituto do Cron: Sistema de Monitoramento Inteligente
Mantém toda estrutura atual, apenas substitui cron jobs por monitoramento eficiente
"""
import asyncio
import logging
import time
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
import threading
import sqlite3
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('smart_monitor')

class SmartPaymentMonitor:
    """Substituto inteligente do cron para monitoramento de pagamentos"""
    
    def __init__(self):
        self.monitoring_orders: Dict[str, dict] = {}  # depix_id -> order_info
        self.active_monitors: Set[str] = set()  # depix_ids sendo monitorados
        self.base_url = "https://useghost.squareweb.app"
        self.is_running = False
        self.monitor_thread = None
        
        # Configurações
        self.check_interval = 30  # Verificar a cada 30 segundos (vs cron de 60s)
        self.max_monitor_time = 7200  # 2 horas máximo por pedido
        
    def start_monitoring(self):
        """Inicia o sistema de monitoramento"""
        if self.is_running:
            logger.warning("⚠️  Monitor já está rodando")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🚀 Sistema de monitoramento inteligente iniciado")
    
    def stop_monitoring(self):
        """Para o sistema de monitoramento"""
        self.is_running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join()
        logger.info("🛑 Sistema de monitoramento parado")
    
    def add_payment_to_monitor(self, depix_id: str, chat_id: str, amount: float, 
                              payment_method: str = "PIX", metadata: dict = None):
        """Adiciona um pagamento para monitoramento (substitui necessidade de cron)"""
        if depix_id in self.monitoring_orders:
            logger.warning(f"⚠️  Depix {depix_id} já está sendo monitorado")
            return
        
        order_info = {
            'depix_id': depix_id,
            'chat_id': str(chat_id),
            'amount': amount,
            'payment_method': payment_method,
            'created_at': datetime.now(),
            'last_check': None,
            'check_count': 0,
            'status': 'MONITORING',
            'metadata': metadata or {}
        }
        
        self.monitoring_orders[depix_id] = order_info
        self.active_monitors.add(depix_id)
        
        logger.info(f"👁️  Iniciando monitoramento: {depix_id} (chat: {chat_id}, valor: R$ {amount:.2f})")
    
    def remove_from_monitoring(self, depix_id: str, reason: str = "completed"):
        """Remove pedido do monitoramento"""
        if depix_id in self.monitoring_orders:
            order = self.monitoring_orders.pop(depix_id)
            self.active_monitors.discard(depix_id)
            
            elapsed = datetime.now() - order['created_at']
            logger.info(f"✅ Monitoramento finalizado: {depix_id} - {reason} (tempo: {elapsed})")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento (substitui cron)"""
        logger.info("🔄 Iniciando loop de monitoramento...")
        
        while self.is_running:
            try:
                if self.active_monitors:
                    self._check_all_payments()
                else:
                    logger.debug("💤 Nenhum pagamento para monitorar")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de monitoramento: {e}")
                time.sleep(self.check_interval)
    
    def _check_all_payments(self):
        """Verifica todos os pagamentos em monitoramento"""
        current_time = datetime.now()
        completed_orders = []
        
        for depix_id in list(self.active_monitors):
            order = self.monitoring_orders.get(depix_id)
            if not order:
                continue
            
            # Verificar timeout
            elapsed = current_time - order['created_at']
            if elapsed.total_seconds() > self.max_monitor_time:
                logger.warning(f"⏰ Timeout para pedido {depix_id} após {elapsed}")
                completed_orders.append((depix_id, "timeout"))
                continue
            
            # Verificar pagamento
            try:
                payment_status = self._check_single_payment(depix_id)
                order['last_check'] = current_time
                order['check_count'] += 1
                
                if payment_status:
                    logger.info(f"💰 Pagamento confirmado: {depix_id}")
                    self._process_confirmed_payment(depix_id, payment_status)
                    completed_orders.append((depix_id, "confirmed"))
                
            except Exception as e:
                logger.error(f"❌ Erro ao verificar {depix_id}: {e}")
        
        # Remover pedidos finalizados
        for depix_id, reason in completed_orders:
            self.remove_from_monitoring(depix_id, reason)
    
    def _check_single_payment(self, depix_id: str) -> Optional[dict]:
        """Verifica status de um pagamento específico"""
        try:
            # Usar mesma API que o cron atual
            url = f"{self.base_url}/rest/deposit.php?depix_id={depix_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('deposits'):
                    deposit = data['deposits'][0]
                    blockchain_txid = deposit.get('blockchainTxID')
                    
                    if blockchain_txid and blockchain_txid != 'NULL' and blockchain_txid.strip():
                        return {
                            'depix_id': depix_id,
                            'blockchain_txid': blockchain_txid,
                            'status': deposit.get('status'),
                            'amount': deposit.get('amount'),
                            'chatid': deposit.get('chatid')
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar {depix_id}: {e}")
            return None
    
    def _process_confirmed_payment(self, depix_id: str, payment_data: dict):
        """Processa pagamento confirmado (faz o que o cron fazia)"""
        order = self.monitoring_orders.get(depix_id)
        if not order:
            return
        
        chat_id = order['chat_id']
        
        try:
            # 1. Disparar mesmo endpoint que o cron chamava
            self._trigger_lightning_processing(chat_id, depix_id, payment_data)
            
            # 2. Disparar notifier (como cron fazia)
            self._trigger_notifier(chat_id)
            
            logger.info(f"✅ Processamento concluído para {depix_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar pagamento {depix_id}: {e}")
    
    def _trigger_lightning_processing(self, chat_id: str, depix_id: str, payment_data: dict):
        """Dispara processamento Lightning (substitui cron Lightning)"""
        try:
            # Chamar mesmo endpoint que o cron chamava
            cron_url = f"{self.base_url}/api/lightning_cron_endpoint_final.php?chat_id={chat_id}"
            
            response = requests.get(cron_url, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Lightning processing disparado para {chat_id}")
                try:
                    result = response.json()
                    logger.debug(f"📊 Resultado Lightning: {result}")
                except:
                    pass
            else:
                logger.error(f"❌ Erro no Lightning processing: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao disparar Lightning processing: {e}")
    
    def _trigger_notifier(self, chat_id: str):
        """Dispara notifier (substitui cron notifier)"""
        try:
            # Chamar mesmo endpoint que o cron chamava
            notifier_url = f"{self.base_url}/api/lightning_notifier.php?chat_id={chat_id}"
            
            response = requests.get(notifier_url, timeout=15)
            
            if response.status_code == 200:
                logger.info(f"✅ Notifier disparado para {chat_id}")
            else:
                logger.error(f"❌ Erro no notifier: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao disparar notifier: {e}")
    
    # ============================================================================
    # MÉTODOS DE MIGRAÇÃO GRADUAL
    # ============================================================================
    
    def import_existing_pending_orders(self):
        """Importa pedidos pendentes do sistema atual para monitoramento"""
        logger.info("📥 Importando pedidos pendentes do sistema atual...")
        
        try:
            # Consultar pedidos pendentes no banco
            pending_orders = self._get_pending_orders_from_db()
            
            for order in pending_orders:
                self.add_payment_to_monitor(
                    depix_id=order['depix_id'],
                    chat_id=order['chatid'],
                    amount=order['amount'] / 100,  # Converter centavos para reais
                    payment_method="PIX",
                    metadata={
                        'imported': True,
                        'original_created_at': order.get('created_at')
                    }
                )
            
            logger.info(f"✅ {len(pending_orders)} pedidos importados para monitoramento")
            
        except Exception as e:
            logger.error(f"❌ Erro ao importar pedidos: {e}")
    
    def _get_pending_orders_from_db(self) -> list:
        """Busca pedidos pendentes no banco de dados atual"""
        try:
            # Conectar ao banco SQLite atual
            db_path = "/home/mau/bot/ghostbackend/data/deposit.db"
            
            if not os.path.exists(db_path):
                logger.warning(f"⚠️  Banco não encontrado: {db_path}")
                return []
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Buscar depósitos sem blockchain_txid (ainda não pagos)
            query = """
                SELECT depix_id, chatid, amount, created_at, status
                FROM deposits 
                WHERE (blockchainTxID IS NULL OR blockchainTxID = '' OR blockchainTxID = 'NULL')
                AND status != 'LIGHTNING_PAID'
                AND created_at > datetime('now', '-2 hours')
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            orders = []
            for row in rows:
                orders.append({
                    'depix_id': row[0],
                    'chatid': row[1],
                    'amount': row[2],
                    'created_at': row[3],
                    'status': row[4]
                })
            
            conn.close()
            
            return orders
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar banco: {e}")
            return []
    
    # ============================================================================
    # MÉTODOS DE MONITORAMENTO E MÉTRICAS
    # ============================================================================
    
    def get_monitoring_stats(self) -> dict:
        """Retorna estatísticas do monitoramento"""
        active_count = len(self.active_monitors)
        
        if not self.monitoring_orders:
            return {
                'active_orders': 0,
                'total_monitored': 0,
                'average_check_time': 0,
                'oldest_order_age': 0
            }
        
        current_time = datetime.now()
        ages = []
        check_counts = []
        
        for order in self.monitoring_orders.values():
            age = (current_time - order['created_at']).total_seconds()
            ages.append(age)
            check_counts.append(order['check_count'])
        
        return {
            'active_orders': active_count,
            'total_monitored': len(self.monitoring_orders),
            'average_check_count': sum(check_counts) / len(check_counts) if check_counts else 0,
            'oldest_order_age': max(ages) if ages else 0,
            'youngest_order_age': min(ages) if ages else 0
        }
    
    def log_stats(self):
        """Registra estatísticas no log"""
        stats = self.get_monitoring_stats()
        
        if stats['active_orders'] > 0:
            logger.info(f"📊 STATS: {stats['active_orders']} pedidos ativos, "
                       f"idade mais antiga: {stats['oldest_order_age']:.0f}s, "
                       f"verificações médias: {stats['average_check_count']:.1f}")

# ============================================================================
# INTEGRAÇÃO COM SISTEMA ATUAL
# ============================================================================

class CronReplacement:
    """Substituto direto do cron que mantém compatibilidade total"""
    
    def __init__(self):
        self.monitor = SmartPaymentMonitor()
        self.enabled = False
        
    def enable(self):
        """Ativa o substituto do cron"""
        if self.enabled:
            return
        
        self.enabled = True
        self.monitor.start_monitoring()
        
        # Importar pedidos pendentes
        self.monitor.import_existing_pending_orders()
        
        logger.info("🔄 Substituto do cron ativado - sistema atual mantido")
    
    def disable(self):
        """Desativa o substituto (volta para cron original)"""
        if not self.enabled:
            return
        
        self.enabled = False
        self.monitor.stop_monitoring()
        
        logger.info("🔄 Substituto do cron desativado - voltando para cron original")
    
    def add_new_order(self, depix_id: str, chat_id: str, amount: float):
        """Adiciona novo pedido ao monitoramento (chamar após criar PIX)"""
        if self.enabled:
            self.monitor.add_payment_to_monitor(depix_id, chat_id, amount)
    
    def is_monitoring(self, depix_id: str) -> bool:
        """Verifica se um pedido está sendo monitorado"""
        return depix_id in self.monitor.active_monitors
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do monitoramento"""
        return self.monitor.get_monitoring_stats()

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================
cron_replacement = CronReplacement()

def enable_smart_monitoring():
    """Ativa monitoramento inteligente (substitui cron)"""
    cron_replacement.enable()
    return cron_replacement

def disable_smart_monitoring():
    """Desativa monitoramento inteligente (volta para cron)"""
    cron_replacement.disable()

def add_order_to_monitor(depix_id: str, chat_id: str, amount: float):
    """Função para adicionar novo pedido (usar após criar PIX)"""
    cron_replacement.add_new_order(depix_id, chat_id, amount)

# ============================================================================
# EXEMPLO DE INTEGRAÇÃO
# ============================================================================
if __name__ == "__main__":
    # Teste do sistema
    monitor = enable_smart_monitoring()
    
    print("✅ Monitor inteligente ativado!")
    print("📊 Estatísticas:", monitor.get_stats())
    
    # Simular adição de pedido
    add_order_to_monitor("test_dep_123", "7910260237", 50.0)
    
    print("👁️  Pedido adicionado ao monitoramento")
    print("📊 Estatísticas:", monitor.get_stats())
    
    # Manter rodando por teste
    try:
        print("🔄 Monitorando... (Ctrl+C para parar)")
        while True:
            time.sleep(30)
            monitor.monitor.log_stats()
    except KeyboardInterrupt:
        print("\n🛑 Parando monitor...")
        disable_smart_monitoring()
        print("✅ Monitor parado!")
