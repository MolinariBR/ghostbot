"""
Comandos Lightning para o bot Ghost
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from handlers.lightning_payments import get_lightning_manager

logger = logging.getLogger(__name__)

async def lightning_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /lightning_status - Mostra status dos pagamentos Lightning do usuário"""
    try:
        chatid = str(update.effective_chat.id)
        lightning_manager = get_lightning_manager(context.bot)
        
        # Busca pagamentos Lightning do usuário
        payments = await lightning_manager.get_lightning_status(chatid)
        
        if not payments:
            await update.message.reply_text(
                "⚡ **Lightning Status**\n\n"
                "Você não possui pagamentos Lightning registrados.",
                parse_mode='Markdown'
            )
            return
            
        # Monta mensagem com status
        message = "⚡ **Seus Pagamentos Lightning** ⚡\n\n"
        
        for payment in payments:
            status_emoji = {
                'processando': '🔄',
                'completo': '✅',
                'erro_lightning': '❌',
                'pending': '⏳'
            }.get(payment['status'], '❓')
            
            amount = int(float(payment['send'])) if payment['send'] else 0
            
            message += f"{status_emoji} **ID {payment['id']}**\n"
            message += f"   💰 {amount:,} sats\n"
            message += f"   📊 Status: {payment['status']}\n"
            message += f"   📅 {payment['created_at']}\n"
            
            if payment['status'] == 'completo' and payment['address']:
                if payment['address'].startswith('lnurl'):
                    message += f"   ⚡ LNURL: `{payment['address'][:30]}...`\n"
                    
            message += "\n"
            
        message += "💡 *Use /lightning_help para mais informações*"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no comando lightning_status: {e}")
        await update.message.reply_text(
            "❌ Erro ao consultar status Lightning. Tente novamente."
        )

async def lightning_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /lightning_help - Ajuda sobre Lightning Network"""
    help_text = """⚡ **Ajuda - Lightning Network** ⚡

🔹 **O que é Lightning?**
Lightning Network é uma solução de segunda camada do Bitcoin que permite transações instantâneas e com taxas baixíssimas.

🔹 **Como funciona no Ghost Bot?**
1. Você escolhe receber via BTC Lightning
2. Após confirmação do pagamento, recebe um LNURL
3. Use sua carteira Lightning para sacar instantaneamente

🔹 **Carteiras Recomendadas:**
• 📱 **Phoenix** - Fácil de usar
• 📱 **Muun** - Auto-custódia  
• 📱 **Wallet of Satoshi** - Custodial
• 📱 **Blue Wallet** - Versátil

🔹 **Comandos Disponíveis:**
• `/lightning_status` - Ver seus pagamentos
• `/lightning_trigger` - Processar pendentes (admin)

🔹 **Processo de Recebimento:**
1. Abra sua carteira Lightning
2. Toque em "Receber" ou "Saque"
3. Escaneie o QR code enviado pelo bot
4. Confirme o valor
5. Sats creditados instantaneamente!

⚡ **Lightning = Rápido, Barato, Bitcoin Real** ⚡"""

    await update.message.reply_text(help_text, parse_mode='Markdown')

async def lightning_trigger_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /lightning_trigger - Dispara processamento Lightning (admin)"""
    try:
        # Verifica se é administrador (implementar lógica de admin)
        chatid = str(update.effective_chat.id)
        
        # Por enquanto, permite apenas para um chat específico (ajustar conforme necessário)
        admin_chats = ['123456789']  # Substitua pelo seu chat ID
        
        if chatid not in admin_chats:
            await update.message.reply_text("❌ Comando disponível apenas para administradores.")
            return
            
        lightning_manager = get_lightning_manager(context.bot)
        
        # Verifica se foi especificado um ID de transação
        args = context.args
        transaction_id = None
        
        if args:
            try:
                transaction_id = int(args[0])
            except ValueError:
                await update.message.reply_text("❌ ID da transação deve ser um número.")
                return
                
        # Dispara o processamento
        await update.message.reply_text("🔄 Disparando processamento Lightning...")
        
        success = await lightning_manager.trigger_payment_processing(transaction_id)
        
        if success:
            message = "✅ Processamento Lightning disparado com sucesso!"
            if transaction_id:
                message += f"\n🆔 Transação: {transaction_id}"
        else:
            message = "❌ Erro ao disparar processamento Lightning."
            
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Erro no comando lightning_trigger: {e}")
        await update.message.reply_text("❌ Erro interno. Verifique os logs.")

async def lightning_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /lightning_info - Informações técnicas sobre Lightning"""
    info_text = """⚡ **Lightning Network - Informações Técnicas** ⚡

🔧 **Tecnologia:**
• Canais de pagamento off-chain
• Settlement no Bitcoin mainnet
• Roteamento automático via nós
• Liquidez compartilhada na rede

💰 **Vantagens:**
• ⚡ Transações instantâneas (< 1 segundo)
• 💸 Taxas baixíssimas (1-10 sats)
• 🔒 Mesmo nível de segurança do Bitcoin
• 🌐 Funciona globalmente 24/7

🎯 **Ideal para:**
• Micropagamentos
• Compras do dia a dia  
• Remessas internacionais
• Pagamentos entre comerciantes

📊 **Estatísticas da Rede:**
• +5.000 nós públicos
• +80.000 canais ativos
• +5.000 BTC de capacidade
• 99.5% taxa de sucesso

🔗 **Compatibilidade:**
Funciona com qualquer carteira Lightning padrão (BOLT-11/LNURL).

⚠️ **Limitações:**
• Pagamentos limitados pela liquidez
• Requer carteira online
• Melhor para valores pequenos/médios

🤖 **No Ghost Bot:**
Processamento 100% automatizado via Voltz API!"""

    await update.message.reply_text(info_text, parse_mode='Markdown')

# Handlers para registrar no bot
from handlers.lightning_callbacks import comprar_novamente_handler

lightning_handlers = [
    CommandHandler('lightning_status', lightning_status_command),
    CommandHandler('lightning_help', lightning_help_command),
    CommandHandler('lightning_trigger', lightning_trigger_command),
    CommandHandler('lightning_info', lightning_info_command),
    comprar_novamente_handler,  # Handler para botão "Comprar Novamente"
]
