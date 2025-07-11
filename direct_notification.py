#!/usr/bin/env python3
"""
Sistema de Notificação Direta via API Telegram
Substitui o polling por verificações pontuais e notificação direta
"""
import asyncio
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DirectNotificationSystem:
    """Sistema de notificação direta sem polling contínuo"""
    
    def __init__(self):
        self.bot_token = "7105509014:AAENhZArthrysOBoEmdA6vaxE72pobliahI"
        self.telegram_api = f"https://api.telegram.org/bot{self.bot_token}"
        
    async def send_address_request(self, chat_id: str, depix_id: str, blockchain_txid: str):
        """Envia solicitação de endereço Lightning diretamente"""
        try:
            message = (
                "⚡ *PIX CONFIRMADO - LIGHTNING PAYMENT* ⚡\n\n"
                "🎉 Seu pagamento PIX foi confirmado com sucesso!\n"
                "⚡ Agora você receberá seus bitcoins via Lightning Network.\n\n"
                "📮 *Forneça seu endereço Lightning:*\n"
                "• Lightning Address: `usuario@wallet.com`\n"
                "• BOLT11 Invoice: `lnbc1...`\n\n"
                "💡 *Recomendações de carteiras:*\n"
                "• Phoenix Wallet\n"
                "• Wallet of Satoshi\n"
                "• Muun Wallet\n"
                "• BlueWallet\n\n"
                "🔤 *Digite seu Lightning Address ou Invoice:*\n\n"
                f"🆔 PIX ID: `{depix_id}`\n"
                f"🔗 TxID: `{blockchain_txid}`"
            )
            
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(
                f"{self.telegram_api}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info(f"✅ Mensagem enviada para {chat_id}, message_id: {result['result']['message_id']}")
                    return True
                else:
                    logger.error(f"❌ Erro na API Telegram: {result}")
                    return False
            else:
                logger.error(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro enviando mensagem: {e}")
            return False
    
    async def check_and_notify(self, depix_id: str, chat_id: str):
        """Verifica status do PIX e notifica se confirmado"""
        try:
            # Verificar status atual
            import uuid
            api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0"
            headers = {
                "api_key": api_key,
                "Authorization": f"Bearer {api_key}",
                "X-Nonce": str(uuid.uuid4())
            }
            
            url = f"https://depix.eulen.app/api/deposit-status?id={depix_id}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                response_data = data.get('response', data)
                status = response_data.get('status')
                blockchain_txid = response_data.get('blockchainTxID')
                
                logger.info(f"🔍 Status: {status}, TxID: {blockchain_txid is not None}")
                
                if status == 'depix_sent' and blockchain_txid:
                    logger.info(f"🎉 PIX confirmado! Enviando notificação...")
                    success = await self.send_address_request(chat_id, depix_id, blockchain_txid)
                    return success
                else:
                    logger.info(f"⏳ PIX ainda pendente (status: {status})")
                    return False
            else:
                logger.error(f"❌ Erro consultando API: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro verificando PIX: {e}")
            return False

    async def schedule_smart_checks(self, depix_id: str, chat_id: str):
        """Agenda verificações inteligentes em intervalos estratégicos"""
        intervals = [30, 120, 300]  # 30s, 2min, 5min
        
        logger.info(f"🎯 Agendando verificações inteligentes para {depix_id}")
        
        for i, delay in enumerate(intervals, 1):
            try:
                logger.info(f"⏰ Aguardando {delay}s para verificação {i}/3")
                await asyncio.sleep(delay)
                
                logger.info(f"🔍 Verificação {i}/3 iniciada")
                success = await self.check_and_notify(depix_id, chat_id)
                
                if success:
                    logger.info(f"✅ PIX confirmado na verificação {i}/3!")
                    return True
                else:
                    logger.info(f"⏳ Verificação {i}/3: PIX ainda pendente")
                    
            except Exception as e:
                logger.error(f"❌ Erro na verificação {i}/3: {e}")
                
        logger.warning(f"⚠️ Todas as verificações falharam para {depix_id}")
        return False

# Instância global
notification_system = DirectNotificationSystem()

# Função para integração
async def notify_pix_confirmed(depix_id: str, chat_id: str):
    """Verifica e notifica PIX confirmado"""
    return await notification_system.check_and_notify(depix_id, chat_id)

if __name__ == "__main__":
    # Teste
    async def test():
        result = await notify_pix_confirmed(
            "0197f7083e627dfe8532dfb32d576171", 
            "7910260237"
        )
        print(f"Resultado: {result}")
    
    asyncio.run(test())
