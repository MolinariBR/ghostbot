"""
Integração Lightning Network - Handler para solicitar invoice do cliente
"""
import logging
import requests
import asyncio
import time
import json
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

💰 **Valor confirmado:** R$ {amount_sats/166.67:.2f}
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
    APENAS executa quando blockchainTxID estiver presente (PIX confirmado).
    
    Args:
        depix_id: ID do depósito
        chat_id: ID do chat do usuário
        is_lightning: Se é transação Lightning
        bot: Instância do bot
    """
    if not is_lightning:
        logger.info(f"Depix {depix_id} não é Lightning, ignorando monitoramento")
        return
    
    logger.info(f"🔄 Verificando se PIX foi confirmado para Lightning - Depix: {depix_id}")
    
    max_tentativas = 60  # 30 minutos (30s * 60)
    tentativa = 0
    
    while tentativa < max_tentativas:
        try:
            # PASSO 1: Verificar se PIX foi confirmado (blockchainTxID presente)
            url_check = "https://useghost.squareweb.app/rest/deposit.php"
            params = {"depix_id": depix_id}
            
            response = requests.get(url_check, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                deposit_found = False
                blockchain_txid = None
                
                # Buscar o depósito específico
                if 'deposits' in data:
                    for deposit in data['deposits']:
                        if deposit.get('depix_id') == depix_id:
                            deposit_found = True
                            blockchain_txid = deposit.get('blockchainTxID')
                            status = deposit.get('status', '')
                            rede = deposit.get('rede', '')
                            
                            logger.info(f"Depósito encontrado - Status: {status}, BlockchainTxID: {blockchain_txid}, Rede: {rede}")
                            break
                
                if not deposit_found:
                    logger.warning(f"Depósito {depix_id} não encontrado")
                    await asyncio.sleep(30)
                    tentativa += 1
                    continue
                
                # CONDIÇÃO CRÍTICA: Só prosseguir se blockchainTxID estiver presente
                if not blockchain_txid or blockchain_txid.strip() == '':
                    logger.info(f"PIX ainda não confirmado para {depix_id} - blockchainTxID vazio (tentativa {tentativa + 1}/{max_tentativas})")
                    await asyncio.sleep(30)
                    tentativa += 1
                    continue
                
                # PASSO 2: PIX confirmado! Verificar se é Lightning
                if 'lightning' not in rede.lower():
                    logger.info(f"Depósito {depix_id} não é Lightning: {rede}")
                    return False
                
                logger.info(f"✅ PIX CONFIRMADO para Lightning - Depix: {depix_id}, BlockchainTxID: {blockchain_txid}")
                
                # PASSO 3: Solicitar invoice do cliente via Voltz
                url_voltz = "https://useghost.squareweb.app/voltz/voltz_rest.php"
                payload = {
                    "action": "process_deposit",
                    "depix_id": depix_id
                }
                
                response_voltz = requests.post(url_voltz, json=payload, timeout=30)
                
                if response_voltz.status_code == 200:
                    # Corrigir problema de JSONs concatenados na resposta Voltz
                    try:
                        data = response_voltz.json()
                    except json.JSONDecodeError:
                        # Se falhar, tentar separar JSONs concatenados
                        content = response_voltz.text
                        split_point = content.find('}{"success"')
                        if split_point != -1:
                            # Pegar o segundo JSON (que tem os dados que precisamos)
                            second_json = content[split_point + 1:]
                            data = json.loads(second_json)
                        else:
                            logger.error(f"Erro ao parsear resposta Voltz: {content}")
                            continue
                    
                    status = data.get('status', 'unknown')
                    message_text = data.get('message', '')
                    
                    logger.info(f"Status Voltz para Depix {depix_id}: {status}, Success: {data.get('success')}, Message: {message_text}")
                    
                    # Condição 1: PIX confirmado, aguardando invoice do cliente
                    if (status == 'awaiting_client_invoice' or 
                        'Invoice do cliente necessário' in message_text or
                        message_text == 'Invoice do cliente necessário para pagamento'):
                        
                        amount_sats = data.get('amount_sats', 0)
                        
                        # Se amount_sats não estiver disponível, calcular baseado no valor do depósito
                        if amount_sats == 0:
                            # Buscar o valor do depósito via API
                            dep_response = requests.get(f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}", timeout=10)
                            if dep_response.status_code == 200:
                                dep_data = dep_response.json()
                                if dep_data.get('deposits'):
                                    dep = dep_data['deposits'][0]
                                    amount_cents = dep.get('amount_in_cents', 0)
                                    # Conversão correta: ~166.67 sats por real (BTC ~R$ 600.000)
                                    amount_sats = int((amount_cents / 100) * 166.67)
                                    logger.info(f"Calculado amount_sats: {amount_sats} para {amount_cents} centavos")
                        
                        logger.info(f"✅ Solicitando invoice Lightning para Depix {depix_id} - {amount_sats} sats")
                        
                        message = f"""
⚡ **PIX CONFIRMADO - LIGHTNING PENDENTE**

💰 **Valor confirmado:** R$ {amount_sats/166.67:.2f}
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
                        
                        return True
                    
                    # Condição 2: Pagamento já completado (Lightning já enviado)
                    elif data.get('success') and status == 'completed':
                        logger.info(f"✅ Lightning já processado para Depix {depix_id}")
                        return True
                        
                    # Condição 3: Erro ou status inválido
                    elif not data.get('success'):
                        error_msg = data.get('error', f'Status: {status}')
                        logger.warning(f"Erro ao processar Depix {depix_id}: {error_msg}")
                        
                        # Se é erro de depósito não encontrado ou não Lightning, falhar
                        if 'não encontrado' in error_msg or 'não é Lightning' in error_msg:
                            await bot.send_message(
                                chat_id=chat_id,
                                text=f"❌ **Erro no processamento**\n\nDetalhes: {error_msg}\n\nEntre em contato com o suporte."
                            )
                            return False
                        
                    elif status in ['cancelled', 'expired', 'failed'] or not data.get('success'):
                        # PIX falhou/cancelado ou erro no processamento
                        error_msg = data.get('error', f'Status: {status}')
                        await bot.send_message(
                            chat_id=chat_id,
                            text=f"❌ **PIX não confirmado**\n\nDetalhes: {error_msg}\n\nTente novamente ou entre em contato com o suporte."
                        )
                        return False
                else:
                    logger.warning(f"Resposta HTTP {response_voltz.status_code} ao verificar Voltz para Depix {depix_id}")
            else:
                logger.warning(f"Resposta HTTP {response.status_code} ao verificar Depix {depix_id}")
            
            # Aguardar antes da próxima verificação
            await asyncio.sleep(30)  # 30 segundos
            tentativa += 1
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout ao verificar PIX {depix_id} (tentativa {tentativa + 1}/{max_tentativas})")
            await asyncio.sleep(30)
            tentativa += 1
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de rede ao monitorar PIX {depix_id}: {e}")
            await asyncio.sleep(30)
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
    from telegram.ext import MessageHandler, filters
    
    # Handler para capturar invoices Lightning enviados pelo usuário
    async def handle_lightning_invoice(update, context):
        message_text = update.message.text
        
        # Verificar se é um invoice Lightning
        if message_text and (message_text.startswith('lnbc') or message_text.startswith('lntb')):
            chat_id = update.effective_chat.id
            
            # Buscar depósito Lightning pendente para este chat via API REST
            import requests
            try:
                # Usar a API REST em vez do banco SQLite direto
                url = f"https://useghost.squareweb.app/rest/deposit.php?chatid={chat_id}"
                response = requests.get(url, timeout=10)
                
                if response.status_code != 200:
                    await update.message.reply_text(
                        "❌ Erro interno. Tente novamente em alguns instantes."
                    )
                    return
                
                data = response.json()
                deposits = data.get('deposits', [])
                
                # Buscar depósito Lightning pendente
                deposito = None
                for dep in deposits:
                    if (dep.get('rede', '').lower().find('lightning') != -1 and 
                        dep.get('blockchainTxID') and
                        dep.get('status') not in ['completed', 'cancelled', 'failed']):
                        deposito = dep
                        break
                
                if deposito:
                    # Calcular valores reais do depósito
                    amount_cents = deposito.get('amount_in_cents', 0)
                    amount_reais = amount_cents / 100
                    # Estimar sats baseado no valor em reais (aproximação: R$ 1 = ~500 sats)
                    estimated_sats = int(amount_cents * 5)  # 500 sats por real
                    
                    # Processar o invoice usando o depix_id do depósito
                    await processar_invoice_recebido(update, context, message_text, deposito['depix_id'])
                    
                    # Log para debug
                    logger.info(f"Lightning invoice processado - Depix: {deposito['depix_id']}, Valor: R$ {amount_reais:.2f}, Est. Sats: {estimated_sats}")
                else:
                    await update.message.reply_text(
                        "❌ Não encontrei nenhum depósito Lightning pendente para você.\n\n"
                        "Use /start para fazer uma nova compra."
                    )
                    
            except Exception as e:
                logger.error(f"Erro ao buscar depósito Lightning: {e}")
                await update.message.reply_text(
                    "❌ Erro interno. Tente novamente em alguns instantes."
                )
    
    # Registrar o handler
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^ln(bc|tb)[a-zA-Z0-9]+$'), 
        handle_lightning_invoice
    ))
    
    logger.info("✅ Integração Lightning configurada - fluxo PIX → solicitar invoice → pagar Lightning")
    
    # Novo fluxo:
    # 1. PIX payment → Depix webhook confirma
    # 2. Bot solicita invoice Lightning do cliente
    # 3. Cliente fornece invoice
    # 4. Ghost paga invoice via Voltz
    # 5. Cliente recebe BTC na carteira Lightning
    
    return True
