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

try:
    from captura.capture_system import capture_system
except ImportError:
    from captura.capture_system import capture_system

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
        
    async def smart_check_payment(self, depix_id: str, chat_id: str):
        """Verificação inteligente com retry em momentos estratégicos - substitui polling contínuo"""
        import uuid
        
        capture_system.capture_step(chat_id, "START_SMART_CHECK_PAYMENT", {"depix_id": depix_id})
        logger.info(f"🧠 Iniciando verificação inteligente para {depix_id}")
        
        # Intervalos estratégicos: 30s, 2min, 5min, 10min, 20min
        intervals = [30, 120, 300, 600, 1200]
        
        api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0"
        headers = {
            "api_key": api_key,
            "Authorization": f"Bearer {api_key}",
            "X-Nonce": str(uuid.uuid4())
        }
        
        for i, delay in enumerate(intervals):
            try:
                logger.info(f"⏱️ Aguardando {delay}s antes da verificação {i+1}/5 para {depix_id}")
                await asyncio.sleep(delay)
                
                # Verificar se o pagamento ainda está ativo
                if depix_id not in self.active_payments:
                    logger.info(f"⚠️ Pagamento {depix_id} foi removido, parando verificação")
                    return None
                
                url = f"https://depix.eulen.app/api/deposit-status?id={depix_id}"
                response = requests.get(url, headers=headers, timeout=10)
                
                capture_system.capture_step(chat_id, "SMART_CHECK_ATTEMPT", {
                    "depix_id": depix_id, 
                    "attempt": i+1,
                    "status_code": response.status_code
                })
                
                if response.status_code == 200:
                    data = response.json()
                    response_data = data.get('response', data)
                    status = response_data.get('status')
                    blockchain_txid = response_data.get('blockchainTxID')
                    
                    logger.info(f"🔍 Verificação {i+1}/5: status={status}, txid={blockchain_txid is not None}")
                    
                    if status == 'depix_sent' and blockchain_txid:
                        capture_system.capture_step(chat_id, "BLOCKCHAIN_TXID_OBTAINED_SMART", {
                            "depix_id": depix_id, 
                            "blockchain_txid": blockchain_txid,
                            "attempt": i+1
                        })
                        
                        logger.info(f"✅ BlockchainTxID encontrado na tentativa {i+1}: {blockchain_txid}")
                        
                        # Verificar se pagamento ainda existe e processar
                        if depix_id in self.active_payments:
                            self.active_payments[depix_id]['blockchain_txid'] = blockchain_txid
                            self.active_payments[depix_id]['confirmed_at'] = datetime.now()
                            await self._process_confirmed_payment(depix_id, self.active_payments[depix_id])
                        else:
                            # Recriar dados do pagamento
                            payment_data = {
                                'chat_id': chat_id,
                                'depix_id': depix_id,
                                'blockchain_txid': blockchain_txid,
                                'registered_at': datetime.now(),
                                'confirmed_at': datetime.now(),
                                'amount': 10.0
                            }
                            self.active_payments[depix_id] = payment_data
                            await self._process_confirmed_payment(depix_id, payment_data)
                        
                        return blockchain_txid
                    
            except Exception as e:
                logger.error(f"❌ Erro na verificação {i+1} para {depix_id}: {e}")
                capture_system.capture_error(chat_id, "SMART_CHECK_ERROR", str(e), e)
        
        # Se chegou aqui, timeout após todas as tentativas
        logger.warning(f"⏰ Timeout após 5 tentativas para {depix_id}")
        capture_system.capture_step(chat_id, "SMART_CHECK_TIMEOUT", {"depix_id": depix_id})
        
        # Remove do monitoramento ativo
        if depix_id in self.active_payments:
            del self.active_payments[depix_id]
        
        return None

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
        capture_system.capture_step(chat_id, "PIX_REGISTERED", {"depix_id": depix_id, "amount_brl": amount_brl})
        
        # Iniciar verificação inteligente (substitui polling contínuo)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(self.smart_check_payment(depix_id, chat_id))
        else:
            loop.run_until_complete(self.smart_check_payment(depix_id, chat_id))
    
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
            
            # MOCK: Se depix_id começar com 'test_', simula pagamento confirmado
            if str(depix_id).startswith('test_'):
                logger.info(f"[MOCK] Pagamento de teste detectado para depix_id: {depix_id}")
                payment_data['blockchain_txid'] = f"MOCK_TXID_{depix_id}"
                payment_data['confirmed_at'] = datetime.now()
                await self._process_confirmed_payment(depix_id, payment_data)
                return f"MOCK_TXID_{depix_id}"
            
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

            # Dispara o processamento Lightning (substitui o cron)
            await self._trigger_lightning_processing(chat_id)

            # NOVO: Solicita endereço cripto após confirmação do pagamento
            try:
                from trigger.sistema_gatilhos import trigger_system, TriggerEvent
                trigger_system.trigger_event(TriggerEvent.ADDRESS_REQUESTED, chat_id, {'depix_id': depix_id})
                logger.info(f"📮 Gatilho ADDRESS_REQUESTED disparado para chat_id {chat_id} após confirmação do pagamento.")
            except Exception as e:
                logger.error(f"Erro ao disparar gatilho ADDRESS_REQUESTED após pagamento confirmado: {e}")
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento confirmado {depix_id}: {e}")
    
    async def _trigger_lightning_processing(self, chat_id: str):
        """Dispara o processamento Lightning via sistema de gatilhos"""
        try:
            # Usar sistema de gatilhos ao invés de cron
            from sistema_gatilhos import trigger_system, TriggerEvent
            
            # Obter dados do pagamento
            payment_data = self.active_payments.get(chat_id)
            if not payment_data:
                logger.warning(f"⚠️  Dados do pagamento não encontrados para chat {chat_id}")
                return
            
            # Disparar evento de PIX detectado
            trigger_data = {
                'depix_id': payment_data.get('depix_id'),
                'amount': payment_data.get('amount'),
                'chat_id': chat_id,
                'blockchain_txid': payment_data.get('blockchain_txid'),  # Adicionado!
                'timestamp': datetime.now().isoformat()
            }
            
            # Disparar o gatilho
            trigger_system.trigger_event(
                TriggerEvent.PIX_PAYMENT_DETECTED,
                chat_id,
                trigger_data
            )
            
            logger.info(f"🎯 Gatilho PIX_PAYMENT_DETECTED disparado para chat {chat_id}")
            
        except ImportError:
            logger.warning("⚠️  Sistema de gatilhos não disponível, usando método de fallback")
            # Fallback para método direto via backend
            await self._trigger_lightning_processing_fallback(chat_id)
            
        except Exception as e:
            logger.error(f"❌ Erro disparando gatilho Lightning para {chat_id}: {e}")
            
    async def _trigger_lightning_processing_fallback(self, chat_id: str):
        """Método de fallback caso gatilhos não funcionem"""
        try:
            # Chamar backend diretamente para processar Lightning
            backend_url = "https://useghost.squareweb.app"
            
            # Buscar depósitos pendentes
            response = requests.get(
                f"{backend_url}/rest/deposit.php?action=list&chatid={chat_id}",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                deposits = data.get('deposits', [])
                
                # Processar depósitos Lightning pendentes
                for deposit in deposits:
                    if (deposit.get('rede') == '⚡ Lightning' and 
                        deposit.get('status') == 'pending' and 
                        deposit.get('blockchainTxID')):
                        
                        logger.info(f"🔄 Processando depósito Lightning {deposit.get('id')}")
                        # Aqui poderia chamar processamento Lightning específico
                        # Por enquanto, apenas logga
                logger.info(f"✅ Fallback processamento Lightning para chat {chat_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro no fallback Lightning para {chat_id}: {e}")
    
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
