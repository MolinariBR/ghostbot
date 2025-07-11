#!/usr/bin/env python3
"""
Enviar mensagem para o PIX atual via Telegram API
"""
import sys
import os
import asyncio
sys.path.append('/home/mau/bot/ghost')

async def send_current_pix_message():
    """Envia mensagem para o PIX atual"""
    try:
        # Dados do PIX atual
        chat_id = '7910260237'
        depix_id = '0197f7083e627dfe8532dfb32d576171'
        blockchain_txid = '9616134cac996d5acd7e1ab0a029d7884141cabf5122500aa7837c3f0c1962c0'
        
        # Mensagem Lightning
        mensagem = (
            "⚡ *PIX CONFIRMADO - LIGHTNING PAYMENT* ⚡\n\n"
            "🎉 Seu pagamento PIX foi confirmado com sucesso!\n"
            "⚡ Agora você receberá seus bitcoins via Lightning Network.\n\n"
            f"🆔 *Depix ID:* `{depix_id}`\n"
            f"🔗 *Blockchain TxID:* `{blockchain_txid[:20]}...`\n\n"
            "📮 *Forneça seu endereço Lightning:*\n"
            "• Lightning Address: `usuario@wallet.com`\n"
            "• BOLT11 Invoice: `lnbc1...`\n\n"
            "💡 *Recomendações de carteiras:*\n"
            "• Phoenix Wallet\n"
            "• Wallet of Satoshi\n"
            "• Muun Wallet\n"
            "• BlueWallet\n\n"
            "🔤 *Digite seu Lightning Address ou Invoice:*"
        )
        
        print(f"🚀 Enviando mensagem para chat_id: {chat_id}")
        print(f"📝 PIX: {depix_id}")
        print(f"🔗 TxID: {blockchain_txid}")
        
        # Enviar via bot
        try:
            import telegram
            from tokens import Config
            
            bot = telegram.Bot(token=Config.TELEGRAM_BOT_TOKEN)
            
            # Enviar mensagem
            await bot.send_message(
                chat_id=int(chat_id),
                text=mensagem,
                parse_mode='Markdown'
            )
            
            print("✅ Mensagem enviada com sucesso!")
            
            # Capturar no sistema
            try:
                from captura.capture_system import capture_system
                capture_system.start_session(chat_id, "triacorelabs")
                capture_system.capture_step(chat_id, "ADDRESS_REQUESTED_CURRENT_PIX", {
                    "depix_id": depix_id,
                    "blockchain_txid": blockchain_txid,
                    "manual_trigger": True,
                    "timestamp": "2025-07-10T22:21:00"
                })
                print("✅ Evento capturado no sistema!")
            except Exception as e:
                print(f"⚠️ Erro capturando evento: {e}")
                
            return True
            
        except Exception as e:
            print(f"❌ Erro enviando mensagem: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def main():
    print("📱 Enviando mensagem para o PIX atual...")
    result = asyncio.run(send_current_pix_message())
    print(f"✅ Resultado: {result}")
    return result

if __name__ == "__main__":
    main()
