#!/usr/bin/env python3
"""
Script para disparar o gatilho diretamente via bot real
"""
import sys
import os
import asyncio
sys.path.append('/home/mau/bot/ghost')

async def send_address_request_to_user():
    """Envia mensagem de solicitação de endereço para o usuário"""
    try:
        # Dados do PIX real
        chat_id = '7910260237'
        depix_id = '0197f6f3c6527dfe9d7ff3bdc3954e93'
        blockchain_txid = 'fabadf97668ed1e6bc943fb41eeef5bf713dbd00a66a25943f1a1cb2a09b89de'
        
        # Mensagem Lightning
        mensagem = (
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
            "🔤 *Digite seu Lightning Address ou Invoice:*"
        )
        
        print(f"🚀 Enviando mensagem para chat_id: {chat_id}")
        print(f"📝 Mensagem: {mensagem[:100]}...")
        
        # Tentar enviar via bot
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
                capture_system.capture_step(chat_id, "ADDRESS_REQUESTED_MANUAL", {
                    "depix_id": depix_id,
                    "blockchain_txid": blockchain_txid,
                    "manual_trigger": True
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
        import traceback
        traceback.print_exc()
        return False

def main():
    print("📱 Disparando mensagem de solicitação de endereço...")
    result = asyncio.run(send_address_request_to_user())
    print(f"✅ Resultado: {result}")
    return result

if __name__ == "__main__":
    main()
