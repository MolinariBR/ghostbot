"""
Módulo para gerenciar pagamentos Lightning no bot Ghost
"""
import asyncio
import logging
import sqlite3
import requests
from datetime import datetime
from typing import Optional, Dict, List
from telegram import Bot
from pathlib import Path

logger = logging.getLogger(__name__)

class LightningPaymentManager:
    """Gerenciador de pagamentos Lightning para o bot Ghost"""
    
    def __init__(self, telegram_bot: Bot, backend_url: str = 'https://ghostp2p.squareweb.app'):
        """
        Inicializa o gerenciador de pagamentos Lightning
        
        Args:
            telegram_bot: Instância do bot Telegram
            backend_url: URL base do backend Ghost
        """
        self.bot = telegram_bot
        self.backend_url = backend_url.rstrip('/')
        # Em produção, o banco estará no servidor web
        self.db_path = Path('/var/www/html/data/deposit.db') if Path('/var/www/html/data/deposit.db').exists() else Path(__file__).parent.parent.parent / 'ghostbackend' / 'data' / 'deposit.db'
        self.last_check = datetime.now()
        
    async def start_monitoring(self, interval_seconds: int = 30):
        """
        Inicia o monitoramento contínuo de pagamentos Lightning
        
        Args:
            interval_seconds: Intervalo em segundos entre verificações
        """
        logger.info(f"Iniciando monitoramento Lightning (intervalo: {interval_seconds}s)")
        
        while True:
            try:
                await self.check_completed_payments()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Erro no monitoramento Lightning: {e}")
                await asyncio.sleep(interval_seconds * 2)  # Aguarda mais em caso de erro
                
    async def check_completed_payments(self):
        """Verifica pagamentos Lightning que foram completados"""
        try:
            # Busca transações Lightning completas que ainda não foram notificadas
            completed_payments = self._get_completed_lightning_payments()
            
            for payment in completed_payments:
                await self._send_lightning_notification(payment)
                self._mark_payment_as_notified(payment['id'])
                
        except Exception as e:
            logger.error(f"Erro ao verificar pagamentos completados: {e}")
            
    def _get_completed_lightning_payments(self) -> List[Dict]:
        """Busca pagamentos Lightning completados no banco"""
        try:
            if not self.db_path.exists():
                logger.warning(f"Banco de dados não encontrado: {self.db_path}")
                return []
                
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            
            # Busca transações Lightning completadas mas não notificadas
            query = """
                SELECT id, chatid, send, address, created_at, blockchainTxID
                FROM deposit 
                WHERE moeda = 'BTC' 
                  AND rede = 'lightning' 
                  AND status = 'completo'
                  AND address LIKE 'lnurl%'
                  AND (notified IS NULL OR notified = 0)
                ORDER BY created_at ASC
            """
            
            cursor = conn.execute(query)
            payments = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return payments
            
        except Exception as e:
            logger.error(f"Erro ao buscar pagamentos Lightning: {e}")
            return []
            
    async def _send_lightning_notification(self, payment: Dict):
        """
        Envia notificação de pagamento Lightning para o cliente
        
        Args:
            payment: Dados do pagamento
        """
        try:
            chatid = payment['chatid']
            amount_sats = int(float(payment['send']))
            lnurl = payment['address']
            transaction_id = payment['id']
            
            # Gera QR code para o LNURL
            qr_code_url = self._generate_qr_code(lnurl)
            
            # Monta a mensagem
            message = self._format_lightning_message(amount_sats, lnurl, qr_code_url, transaction_id)
            
            # Envia a mensagem
            await self.bot.send_message(
                chat_id=chatid,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            
            logger.info(f"Notificação Lightning enviada para ChatID {chatid} - {amount_sats} sats")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Lightning: {e}")
            raise
            
    def _format_lightning_message(self, amount_sats: int, lnurl: str, qr_code_url: str, transaction_id: int) -> str:
        """
        Formata a mensagem de pagamento Lightning
        
        Args:
            amount_sats: Valor em satoshis
            lnurl: LNURL para saque
            qr_code_url: URL do QR code
            transaction_id: ID da transação
            
        Returns:
            Mensagem formatada
        """
        return f"""⚡ *Pagamento Lightning Aprovado!* ⚡

💰 **Valor:** {amount_sats:,} sats
🆔 **ID da Transação:** {transaction_id}
⚡ **Rede:** Lightning Network

📱 **Como receber:**
1. Abra sua carteira Lightning
2. Escolha 'Receber' ou 'Saque'  
3. Escaneie o QR code ou cole o link abaixo:

`{lnurl}`

🔗 [Clique aqui para ver o QR Code]({qr_code_url})

⏰ *Link válido por alguns minutos*
✅ *Processamento automático concluído!*

💡 *Dica: Use carteiras como Phoenix, Muun, ou Wallet of Satoshi*"""

    def _generate_qr_code(self, text: str, size: int = 300) -> str:
        """
        Gera URL do QR code para um texto
        
        Args:
            text: Texto para gerar QR code
            size: Tamanho do QR code
            
        Returns:
            URL do QR code
        """
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        return f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={encoded_text}"
        
    def _mark_payment_as_notified(self, payment_id: int):
        """
        Marca um pagamento como notificado
        
        Args:
            payment_id: ID do pagamento
        """
        try:
            if not self.db_path.exists():
                return
                
            conn = sqlite3.connect(str(self.db_path))
            
            # Adiciona coluna notified se não existir
            try:
                conn.execute("ALTER TABLE deposit ADD COLUMN notified INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # Coluna já existe
                
            # Marca como notificado
            conn.execute(
                "UPDATE deposit SET notified = 1 WHERE id = ?",
                (payment_id,)
            )
            conn.commit()
            conn.close()
            
            logger.info(f"Pagamento ID {payment_id} marcado como notificado")
            
        except Exception as e:
            logger.error(f"Erro ao marcar pagamento como notificado: {e}")
            
    async def trigger_payment_processing(self, transaction_id: Optional[int] = None):
        """
        Dispara o processamento de pagamentos Lightning no backend
        
        Args:
            transaction_id: ID específico da transação (opcional)
        """
        try:
            url = f"{self.backend_url}/api/lightning_trigger.php"
            
            if transaction_id:
                # Processar transação específica
                data = {'id': transaction_id}
                response = requests.post(url, json=data, timeout=10)
            else:
                # Processar todos os pagamentos pendentes
                response = requests.get(url, timeout=10)
                
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Processamento Lightning disparado: {result.get('message', 'OK')}")
                return True
            else:
                logger.error(f"Erro ao disparar processamento Lightning: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao comunicar com backend Lightning: {e}")
            return False
            
    async def get_lightning_status(self, chatid: str) -> List[Dict]:
        """
        Obtém status dos pagamentos Lightning para um usuário
        
        Args:
            chatid: ID do chat do usuário
            
        Returns:
            Lista de pagamentos Lightning do usuário
        """
        try:
            if not self.db_path.exists():
                return []
                
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT id, send, status, created_at, address
                FROM deposit 
                WHERE chatid = ? 
                  AND moeda = 'BTC' 
                  AND rede = 'lightning'
                ORDER BY created_at DESC
                LIMIT 10
            """
            
            cursor = conn.execute(query, (chatid,))
            payments = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return payments
            
        except Exception as e:
            logger.error(f"Erro ao buscar status Lightning: {e}")
            return []

# Instância global para ser importada
lightning_manager = None

def get_lightning_manager(bot: Bot) -> LightningPaymentManager:
    """Obtém a instância global do gerenciador Lightning"""
    global lightning_manager
    if lightning_manager is None:
        lightning_manager = LightningPaymentManager(bot)
    return lightning_manager
