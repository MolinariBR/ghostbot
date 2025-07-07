"""
Integração Lightning Network - Handler para solicitar invoice do cliente
"""
import logging
import requests
import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def solicitar_invoice_lightning(update: Update, context: ContextTypes.DEFAULT_TYPE, depix_id: str, amount_sats: int):
    """
    Solicita invoice Lightning do cliente após PIX confirmado.
    
    Args:
        update: Update do Telegram
        context: Context do bot
        depix_id: ID do depósito
        amount_sats: Valor em satoshis a enviar
    """
    chat_id = update.effective_chat.id
    
    message = f"""
⚡ **PIX CONFIRMADO - LIGHTNING PENDENTE**

💰 **Valor confirmado:** R$ {amount_sats/500:.2f}
⚡ **BTC a receber:** {amount_sats:,} sats

🔗 **PRÓXIMO PASSO:**
Para receber seus bitcoins via Lightning Network, você precisa fornecer um **invoice Lightning** da sua carteira.

📱 **Como gerar invoice:**
• Abra sua carteira Lightning (Phoenix, Wallet of Satoshi, etc.)
• Clique em "Receber"
• Digite o valor: **{amount_sats} sats**
• Copie o invoice gerado
• Cole aqui no chat

⏰ **Aguardando seu invoice Lightning...**
    """
    
    # Keyboard com opções
    keyboard = [
        [InlineKeyboardButton("📋 Como gerar invoice", callback_data=f"help_invoice_{depix_id}")],
        [InlineKeyboardButton("❓ Não tenho carteira Lightning", callback_data=f"help_wallet_{depix_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Salvar estado aguardando invoice
    context.user_data[f'awaiting_invoice_{depix_id}'] = {
        'amount_sats': amount_sats,
        'status': 'awaiting_invoice'
    }

async def processar_invoice_recebido(update: Update, context: ContextTypes.DEFAULT_TYPE, invoice: str, depix_id: str):
    """
    Processa invoice Lightning fornecido pelo cliente.
    
    Args:
        update: Update do Telegram
        context: Context do bot
        invoice: Invoice Lightning fornecido
        depix_id: ID do depósito
    """
    chat_id = update.effective_chat.id
    
    # Validar invoice básico
    if not (invoice.startswith('lnbc') or invoice.startswith('lntb')):
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Invoice inválido! Deve começar com 'lnbc' ou 'lntb'"
        )
        return False
    
    # Mensagem de processamento
    processing_msg = await context.bot.send_message(
        chat_id=chat_id,
        text="⚡ **Processando pagamento Lightning...**\n\n🔄 Enviando bitcoins para sua carteira..."
    )
    
    try:
        # Chamar API para processar pagamento
        url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
        payload = {
            "action": "pay_invoice",
            "depix_id": depix_id,
            "client_invoice": invoice
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                # Pagamento realizado com sucesso
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=processing_msg.message_id,
                    text=f"""
✅ **PAGAMENTO LIGHTNING ENVIADO!**

⚡ **Payment Hash:** `{data.get('payment_hash', 'N/A')}`
💰 **Taxa:** {data.get('fee_msat', 0)} msat
🎯 **Status:** Pagamento concluído

🎉 **Seus bitcoins foram enviados via Lightning Network!**
Verifique sua carteira Lightning - o pagamento deve aparecer em alguns segundos.

📋 **Resumo da transação:**
• Depix ID: `{depix_id}`
• Invoice pago: `{invoice[:50]}...`
                    """,
                    parse_mode='Markdown'
                )
                
                # Limpar estado
                if f'awaiting_invoice_{depix_id}' in context.user_data:
                    del context.user_data[f'awaiting_invoice_{depix_id}']
                
                return True
            else:
                # Erro no pagamento
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=processing_msg.message_id,
                    text=f"""
❌ **FALHA NO PAGAMENTO LIGHTNING**

🔍 **Erro:** {data.get('error', 'Erro desconhecido')}

💡 **Possíveis causas:**
• Invoice expirado
• Valor incorreto
• Problemas de rota Lightning
• Carteira offline

🔄 **Solução:** Gere um novo invoice e tente novamente.
                    """,
                    parse_mode='Markdown'
                )
                return False
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        # Erro de conexão/processamento
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=processing_msg.message_id,
            text=f"""
❌ **ERRO DE PROCESSAMENTO**

🔍 **Detalhes:** {str(e)}

🛠️ **Entre em contato com o suporte:** @seu_suporte
            """,
            parse_mode='Markdown'
        )
        return False

async def monitorar_pix_e_processar_lightning(depix_id: str, chat_id: int, is_lightning: bool, bot):
    """
    Monitora pagamento PIX e inicia fluxo Lightning quando confirmado.
    Função equivalente ao antigo fluxo_envio_invoice.
    
    Args:
        depix_id: ID do depósito
        chat_id: ID do chat do usuário
        is_lightning: Se é transação Lightning
        bot: Instância do bot
    """
    if not is_lightning:
        logger.info(f"Depix {depix_id} não é Lightning, ignorando monitoramento")
        return
    
    logger.info(f"🔄 Iniciando monitoramento PIX para Lightning - Depix: {depix_id}")
    
    max_tentativas = 60  # 30 minutos (30s * 60)
    tentativa = 0
    
    while tentativa < max_tentativas:
        try:
            # Verificar status do PIX via API
            url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
            payload = {
                "action": "check_status",
                "depix_id": depix_id
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                
                if status == 'pix_confirmed':
                    # PIX confirmado, solicitar invoice Lightning
                    amount_sats = data.get('amount_sats', 0)
                    
                    logger.info(f"✅ PIX confirmado para Depix {depix_id}, solicitando invoice Lightning")
                    
                    message = f"""
⚡ **PIX CONFIRMADO - LIGHTNING PENDENTE**

💰 **Valor confirmado:** R$ {amount_sats/500:.2f}
⚡ **BTC a receber:** {amount_sats:,} sats

🔗 **PRÓXIMO PASSO:**
Para receber seus bitcoins via Lightning Network, você precisa fornecer um **invoice Lightning** da sua carteira.

📱 **Como gerar invoice:**
• Abra sua carteira Lightning (Phoenix, Wallet of Satoshi, etc.)
• Clique em "Receber"
• Digite o valor: **{amount_sats} sats**
• Copie o invoice gerado
• Cole aqui no chat

⏰ **Aguardando seu invoice Lightning...**

💡 **Dica:** O invoice deve começar com "lnbc" ou "lntb"
                    """
                    
                    # Keyboard com opções
                    keyboard = [
                        [InlineKeyboardButton("📋 Como gerar invoice", callback_data=f"help_invoice_{depix_id}")],
                        [InlineKeyboardButton("❓ Não tenho carteira Lightning", callback_data=f"help_wallet_{depix_id}")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    
                    # TODO: Configurar handler para receber invoice Lightning
                    # Por enquanto, o usuário deve colar o invoice no chat
                    
                    return True
                    
                elif status in ['cancelled', 'expired', 'failed']:
                    # PIX falhou/cancelado
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"❌ **PIX não confirmado**\n\nStatus: {status}\n\nTente novamente ou entre em contato com o suporte."
                    )
                    return False
            
            # Aguardar antes da próxima verificação
            await asyncio.sleep(30)  # 30 segundos
            tentativa += 1
            
        except Exception as e:
            logger.error(f"Erro ao monitorar PIX {depix_id}: {e}")
            await asyncio.sleep(30)
            tentativa += 1
    
    # Timeout - PIX não confirmado
    await bot.send_message(
        chat_id=chat_id,
        text="⏰ **Timeout** - PIX não foi confirmado em 30 minutos.\n\nVerifique o pagamento ou entre em contato com o suporte."
    )
    return False

def setup_lightning_integration(application):
    """
    Configura a integração Lightning Network.
    
    Args:
        application: A aplicação do bot Telegram
    """
    logger.info("✅ Integração Lightning configurada - fluxo PIX → solicitar invoice → pagar Lightning")
    
    # Novo fluxo:
    # 1. PIX payment → Depix webhook confirma
    # 2. Bot solicita invoice Lightning do cliente
    # 3. Cliente fornece invoice
    # 4. Ghost paga invoice via Voltz
    # 5. Cliente recebe BTC na carteira Lightning
    
    return True
