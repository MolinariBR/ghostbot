#!/usr/bin/env python3
"""
Sistema de Monitoramento Inteligente PIX
Substitui o cron externo por um sistema interno mais eficiente
Integração mínima com o bot atual - apenas 2 linhas de código necessárias
"""
import asyncio
import logging
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)8s | [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('smart_monitor')

class SmartPixMonitor:
    """Monitor inteligente de pagamentos PIX - substitui cron externo"""
    
    def __init__(self):
        self.active_payments: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.monitor_task = None
        self.stats = {
            'payments_monitored': 0,
            'payments_confirmed': 0,
            'monitor_checks': 0,
            'average_confirmation_time': 0,
            'errors': 0
        }
        
    def start_monitoring(self):
        """Inicia o sistema de monitoramento"""
        if self.is_running:
            logger.warning("Monitor já está rodando")
            return
            
        self.is_running = True
        
        # Criar task em background
        def run_monitor():
            try:
                asyncio.run(self._monitor_loop())
            except Exception as e:
                logger.error(f"Erro no monitor: {e}")
                self.is_running = False
        
        monitor_thread = threading.Thread(target=run_monitor, daemon=True)
        monitor_thread.start()
        
        logger.info("🚀 Smart PIX Monitor iniciado")
        
    def stop_monitoring(self):
        """Para o sistema de monitoramento"""
        self.is_running = False
        logger.info("🛑 Smart PIX Monitor parado")
        
    def register_pix_payment(self, depix_id: str, chat_id: str, amount_brl: float):
        """
        Registra um novo pagamento PIX para monitoramento
        
        Esta é a única função que precisa ser chamada no código atual:
        smart_monitor.register_pix_payment(txid, str(update.effective_user.id), valor_brl)
        """
        payment_data = {
            'depix_id': depix_id,
            'chat_id': str(chat_id),
            'amount_brl': amount_brl,
            'registered_at': datetime.now(),
            'last_check': None,
            'checks_count': 0,
            'status': 'waiting'
        }
        
        self.active_payments[depix_id] = payment_data
        self.stats['payments_monitored'] += 1
        
        logger.info(f"📝 PIX registrado para monitoramento: {depix_id} (chat: {chat_id}, valor: R$ {amount_brl:.2f})")
        
        # Se o monitor não estiver rodando, iniciar automaticamente
        if not self.is_running:
            self.start_monitoring()
    
    async def _monitor_loop(self):
        """Loop principal de monitoramento"""
        logger.info("🔄 Iniciando loop de monitoramento")
        
        while self.is_running:
            try:
                await self._check_all_payments()
                await asyncio.sleep(30)  # Verifica a cada 30 segundos (melhor que 60s do cron)
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                self.stats['errors'] += 1
                await asyncio.sleep(60)  # Aguarda mais tempo em caso de erro
    
    async def _check_all_payments(self):
        """Verifica todos os pagamentos ativos"""
        if not self.active_payments:
            return
            
        logger.debug(f"🔍 Verificando {len(self.active_payments)} pagamentos ativos")
        
        payments_to_remove = []
        
        for depix_id, payment_data in self.active_payments.items():
            try:
                # Verifica se o pagamento não é muito antigo (2 horas)
                if datetime.now() - payment_data['registered_at'] > timedelta(hours=2):
                    logger.info(f"⏰ Timeout para pagamento {depix_id} (2 horas)")
                    payments_to_remove.append(depix_id)
                    continue
                
                # Verifica status do pagamento
                confirmed = await self._check_payment_status(depix_id, payment_data)
                
                if confirmed:
                    logger.info(f"✅ Pagamento confirmado: {depix_id}")
                    await self._process_confirmed_payment(depix_id, payment_data)
                    payments_to_remove.append(depix_id)
                    
                payment_data['last_check'] = datetime.now()
                payment_data['checks_count'] += 1
                self.stats['monitor_checks'] += 1
                
            except Exception as e:
                logger.error(f"Erro ao verificar pagamento {depix_id}: {e}")
                self.stats['errors'] += 1
        
        # Remove pagamentos processados ou expirados
        for depix_id in payments_to_remove:
            if depix_id in self.active_payments:
                del self.active_payments[depix_id]
    
    async def _check_payment_status(self, depix_id: str, payment_data: Dict) -> bool:
        """Verifica se um pagamento específico foi confirmado"""
        try:
            url = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('deposits'):
                    deposit = data['deposits'][0]
                    blockchain_txid = deposit.get('blockchainTxID')
                    
                    if blockchain_txid and blockchain_txid != 'pending':
                        payment_data['blockchain_txid'] = blockchain_txid
                        payment_data['confirmed_at'] = datetime.now()
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao consultar status do PIX {depix_id}: {e}")
            return False
    
    async def _process_confirmed_payment(self, depix_id: str, payment_data: Dict):
        """Processa um pagamento confirmado"""
        try:
            chat_id = payment_data['chat_id']
            confirmed_at = payment_data.get('confirmed_at', datetime.now())
            registered_at = payment_data['registered_at']
            
            # Calcula tempo de confirmação
            confirmation_time = (confirmed_at - registered_at).total_seconds()
            
            # Atualiza estatísticas
            self.stats['payments_confirmed'] += 1
            
            # Calcula tempo médio de confirmação
            if self.stats['payments_confirmed'] == 1:
                self.stats['average_confirmation_time'] = confirmation_time
            else:
                current_avg = self.stats['average_confirmation_time']
                count = self.stats['payments_confirmed']
                self.stats['average_confirmation_time'] = (current_avg * (count - 1) + confirmation_time) / count
            
            logger.info(f"💰 Pagamento {depix_id} confirmado em {confirmation_time:.1f}s (chat: {chat_id})")
            
            # AQUI É ONDE CHAMAMOS O SISTEMA ATUAL
            # Dispara o processamento Lightning (substitui o cron)
            await self._trigger_lightning_processing(chat_id)
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento confirmado {depix_id}: {e}")
    
    async def _trigger_lightning_processing(self, chat_id: str):
        """Dispara o processamento Lightning - substitui o cron atual"""
        try:
            # Chama o endpoint que o cron chamava
            cron_url = f"https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php?chat_id={chat_id}"
            
            response = requests.get(cron_url, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"🔄 Processamento Lightning disparado para chat {chat_id}")
                
                # Opcionalmente, chamar o notifier também
                notifier_url = f"https://useghost.squareweb.app/api/lightning_notifier.php?chat_id={chat_id}"
                requests.get(notifier_url, timeout=15)
                
            else:
                logger.error(f"Erro ao disparar processamento Lightning: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro ao disparar processamento Lightning para {chat_id}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do monitor"""
        stats = self.stats.copy()
        stats['active_payments'] = len(self.active_payments)
        stats['is_running'] = self.is_running
        stats['average_confirmation_time_formatted'] = f"{stats['average_confirmation_time']:.1f}s"
        
        return stats
    
    def get_active_payments(self) -> Dict[str, Dict[str, Any]]:
        """Retorna pagamentos ativos"""
        return self.active_payments.copy()

# Instância global do monitor
smart_monitor = SmartPixMonitor()

# Funções de conveniência para integração
def start_smart_monitor():
    """Inicia o monitor inteligente"""
    smart_monitor.start_monitoring()

def register_pix_payment(depix_id: str, chat_id: str, amount_brl: float):
    """Registra um pagamento PIX para monitoramento"""
    smart_monitor.register_pix_payment(depix_id, chat_id, amount_brl)

def get_monitor_stats():
    """Obtém estatísticas do monitor"""
    return smart_monitor.get_stats()

def stop_smart_monitor():
    """Para o monitor"""
    smart_monitor.stop_monitoring()

# Auto-iniciar quando o módulo for importado
try:
    start_smart_monitor()
    logger.info("✅ Smart PIX Monitor auto-iniciado")
except Exception as e:
    logger.error(f"Erro ao auto-iniciar monitor: {e}")

if __name__ == "__main__":
    # Teste do sistema
    print("🧪 Testando Smart PIX Monitor...")
    
    # Simular registro de pagamento
    test_depix_id = f"test_{int(time.time())}"
    test_chat_id = "123456789"
    test_amount = 50.0
    
    register_pix_payment(test_depix_id, test_chat_id, test_amount)
    
    print(f"📝 Pagamento teste registrado: {test_depix_id}")
    
    # Aguardar um pouco
    time.sleep(5)
    
    # Mostrar estatísticas
    stats = get_monitor_stats()
    print(f"📊 Estatísticas: {stats}")
    
    # Mostrar pagamentos ativos
    active = smart_monitor.get_active_payments()
    print(f"🔄 Pagamentos ativos: {len(active)}")
    
    print("✅ Teste concluído!")
    print("💡 Para integrar no bot, adicione após criar o PIX:")
    print(f"   register_pix_payment('{test_depix_id}', '{test_chat_id}', {test_amount})")
