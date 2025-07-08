"""
EXEMPLO PRÁTICO - Como integrar no Ghost Bot
==========================================

Este arquivo mostra exatamente como usar a integração Voltz 
nos handlers do seu bot do Telegram.
"""

from api.voltz import VoltzAPI
import asyncio

# Configurar a API Voltz
voltz = VoltzAPI(backend_url='https://useghost.squareweb.app')  # URL de produção

async def handle_comprar_lightning(update, context):
    """
    Handler para quando usuário escolhe comprar via Lightning Network
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Exemplo: usuário quer comprar R$ 50,00 em BTC
    valor_brl = 50.0
    valor_sats = 85000  # Calcular baseado na cotação atual
    
    try:
        # 1. Registrar o pedido no backend
        result = voltz.create_deposit_request(
            chatid=str(chat_id),
            userid=str(user_id),
            amount_in_cents=int(valor_brl * 100),  # R$ 50,00 = 5000 centavos
            taxa=0.05,  # 5% de taxa
            moeda='BTC',
            send_amount=valor_sats
        )
        
        # 2. Enviar confirmação para o usuário
        confirmation_msg = voltz.format_deposit_confirmation_message(
            depix_id=result['depix_id'],
            amount_in_cents=int(valor_brl * 100),
            moeda='BTC',
            send_amount=valor_sats
        )
        
        await update.message.reply_text(
            confirmation_msg, 
            parse_mode='Markdown'
        )
        
        # 3. Agendar verificação de status
        context.job_queue.run_repeating(
            callback=check_deposit_status,
            interval=30,  # Verificar a cada 30 segundos
            first=10,     # Primeira verificação em 10 segundos
            context={
                'depix_id': result['depix_id'],
                'chat_id': chat_id,
                'amount_sats': valor_sats
            },
            name=f"check_deposit_{result['depix_id']}"
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Erro ao processar pedido: {str(e)}"
        )

async def check_deposit_status(context):
    """
    Job que verifica o status do depósito periodicamente
    """
    job_context = context.job.context
    depix_id = job_context['depix_id']
    chat_id = job_context['chat_id']
    amount_sats = job_context['amount_sats']
    
    try:
        # Verificar status no backend Voltz
        status = voltz.check_deposit_status(depix_id)
        
        if status.get('success'):
            # Se encontrou invoice, enviar para o usuário
            if 'invoice' in status and status['invoice']:
                invoice_msg = voltz.format_invoice_message(
                    amount_sats=amount_sats,
                    payment_request=status['invoice'],
                    qr_code_url=status.get('qr_code', '')
                )
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=invoice_msg,
                    parse_mode='Markdown'
                )
                
                # Parar de verificar - invoice foi encontrado
                context.job.schedule_removal()
                
            elif status.get('status') == 'error':
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ Erro no processamento do pedido {depix_id}"
                )
                context.job.schedule_removal()
                
        # Parar após 10 minutos (20 verificações * 30seg)
        if context.job.data and context.job.data.get('attempts', 0) > 20:
            await context.bot.send_message(
                chat_id=chat_id,
                text="⏰ Timeout: Invoice não foi gerado. Tente novamente."
            )
            context.job.schedule_removal()
        else:
            # Incrementar contador de tentativas
            if not context.job.data:
                context.job.data = {}
            context.job.data['attempts'] = context.job.data.get('attempts', 0) + 1
            
    except Exception as e:
        print(f"Erro ao verificar status: {e}")

# Exemplo de como adicionar no main do bot
def main():
    """
    Exemplo de como adicionar no seu bot principal
    """
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    
    # Criar aplicação do bot
    app = Application.builder().token("SEU_BOT_TOKEN").build()
    
    # Adicionar handlers
    app.add_handler(CommandHandler("comprar_lightning", handle_comprar_lightning))
    
    # Rodar o bot
    app.run_polling()

# TESTES MANUAIS RÁPIDOS
if __name__ == "__main__":
    print("🧪 Testes Rápidos da Integração Voltz")
    print("=" * 40)
    
    # Testar criação de depósito
    try:
        result = voltz.create_deposit_request(
            chatid="123456789",
            userid="test_user",
            amount_in_cents=2500,
            taxa=0.05,
            moeda="BTC",
            send_amount=42000
        )
        print(f"✅ Depósito criado: {result['depix_id']}")
        
        # Testar verificação de status
        status = voltz.check_deposit_status(result['depix_id'])
        print(f"✅ Status consultado: {status.get('status', 'erro')}")
        
        print("\n🎉 Integração funcionando!")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
