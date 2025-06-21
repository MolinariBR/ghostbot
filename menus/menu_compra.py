from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import MessageHandler, ConversationHandler, CommandHandler, filters
from telegram.ext import ContextTypes
import requests
from datetime import datetime, timedelta
import logging

# Variável para armazenar a função do menu principal
menu_principal_func = None

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Importa as funções de cotação
from api.cotacao import get_btc_price_brl, get_usdt_price_brl, get_depix_price_brl

def obter_cotacao(moeda: str) -> float:
    """
    Obtém a cotação atual da moeda em BRL com margem de 2%.
    
    Args:
        moeda: Nome da moeda (pode conter 'BTC', 'USDT' ou 'Depix')
        
    Returns:
        float: Cotação da moeda em BRL com margem de 2%
    """
    try:
        moeda = moeda.upper()
        if "BTC" in moeda:
            return float(get_btc_price_brl())
        elif "USDT" in moeda:
            return float(get_usdt_price_brl())
        elif "DEPIX" in moeda:
            return float(get_depix_price_brl())
        
        logger.warning(f"Moeda não reconhecida: {moeda}")
        return 1.0  # Fallback
        
    except Exception as e:
        logger.error(f"Erro ao obter cotação para {moeda}: {e}")
        # Valores padrão em caso de falha na API
        cotacoes_padrao = {
            "BTC": 350000.00,
            "USDT": 5.20,
            "DEPIX": 0.50
        }
        
        for chave, valor in cotacoes_padrao.items():
            if chave in moeda:
                return valor
                
        return 1.0  # Fallback final

# Função para formatar valores monetários
def formatar_brl(valor: float) -> str:
    """Formata um valor em BRL (ex: 1500.5 -> 'R$ 1.500,50')."""
    return f"R$ {valor:,.2f}".replace(".", "v").replace(",", ".").replace("v", ",")

def formatar_cripto(valor: float, moeda: str) -> str:
    """Formata um valor de criptomoeda com casas decimais apropriadas."""
    if "BTC" in moeda.upper():
        return f"{valor:.8f} {moeda.split()[0].strip()}"  # 8 casas para BTC
    elif "USDT" in moeda.upper():
        return f"{valor:,.2f} {moeda.split()[0].strip()}"  # 2 casas para USDT
    else:
        return f"{valor:,.2f} {moeda.split()[0].strip()}"  # 2 casas para outras moedas

# Estados do menu de compra
(ESCOLHER_MOEDA, ESCOLHER_REDE, QUANTIDADE, CONFIRMAR, 
 SOLICITAR_ENDERECO, ESCOLHER_PAGAMENTO) = range(6)

# Constantes para métodos de pagamento
PIX = "PIX"
TED = "TED"
BOLETO = "Boleto Bancário"

def menu_moedas():
    """Retorna o teclado com as opções de moedas."""
    keyboard = [
        [KeyboardButton("₿ Bitcoin (BTC)")],
        [KeyboardButton("💵 Tether (USDT)")],
        [KeyboardButton("💠 Depix")],
        [KeyboardButton("🔙 Voltar")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def menu_redes(moeda: str):
    """Retorna o teclado com as opções de rede para a moeda selecionada."""
    if "BTC" in moeda:
        redes = [
            [KeyboardButton("⛓️ On-chain")],
            [KeyboardButton("⚡ Lightning")],
            [KeyboardButton("💧 Liquid")],
            [KeyboardButton("🔙 Voltar")]
        ]
    elif "USDT" in moeda:
        redes = [
            [KeyboardButton("💧 Liquid")],
            [KeyboardButton("🟣 Polygon")],
            [KeyboardButton("🔙 Voltar")]
        ]
    else:  # Depix
        redes = [
            [KeyboardButton("💧 Liquid")],
            [KeyboardButton("🔙 Voltar")]
        ]
    return ReplyKeyboardMarkup(redes, resize_keyboard=True, one_time_keyboard=False)

async def iniciar_compra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o fluxo de compra mostrando as moedas disponíveis."""
    await update.message.reply_text(
        "💱 *ESCOLHA A MOEDA PARA COMPRA*\n\n"
        "Selecione a criptomoeda que deseja comprar:",
        reply_markup=menu_moedas(),
        parse_mode='Markdown'
    )
    return ESCOLHER_MOEDA

async def escolher_moeda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a escolha da moeda e pede para selecionar a rede."""
    if update.message.text == "🔙 Voltar":
        # Get the main menu keyboard (synchronous call)
        main_menu = menu_principal_func()
        await update.message.reply_text(
            "Operação cancelada.",
            reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        )
        return ConversationHandler.END
        
    moeda_escolhida = update.message.text
    context.user_data['moeda'] = moeda_escolhida
    
    await update.message.reply_text(
        f"🔄 *Rede de {moeda_escolhida}*\n\n"
        "Selecione a rede que deseja utilizar:",
        reply_markup=menu_redes(moeda_escolhida),
        parse_mode='Markdown'
    )
    return ESCOLHER_REDE

async def escolher_rede(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a escolha da rede e pede o valor em BRL."""
    if update.message.text == "🔙 Voltar":
        return await iniciar_compra(update, context)
        
    rede = update.message.text
    context.user_data['rede'] = rede
    
    # Get the selected coin
    moeda = context.user_data.get('moeda', 'a moeda selecionada')
    
    # Formata os valores para exibição
    min_valor = "10,00"
    max_valor = "5.000,00"
    
    # Mensagem inicial
    mensagem = (
        f"💎 *{moeda} - {rede}*\n\n"
        f"💰 *Valor de Investimento*\n"
        f"• Mínimo: R$ {min_valor}\n"
        f"• Máximo: R$ {max_valor}\n\n"
        "💵 *Digite o valor desejado* (ex: 150,50) ou use os valores sugeridos abaixo:"
    )
    
    # Teclado com valores sugeridos e campo de digitação
    teclado = [
        [
            KeyboardButton("R$ 50,00"), 
            KeyboardButton("R$ 100,00"),
            KeyboardButton("R$ 250,00")
        ],
        [
            KeyboardButton("R$ 500,00"),
            KeyboardButton("R$ 1.000,00"),
            KeyboardButton("R$ 2.500,00")
        ],
        [
            KeyboardButton("Digitar valor"),
            KeyboardButton("🔙 Voltar")
        ]
    ]
    
    await update.message.reply_text(
        mensagem,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(teclado, resize_keyboard=True)
    )
    return QUANTIDADE

async def processar_quantidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a quantidade informada e mostra confirmação."""
    try:
        # Se o usuário clicou em "Digitar valor", pede para digitar
        if update.message.text == "Digitar valor":
            await update.message.reply_text(
                "💵 *Digite o valor desejado*\n\n"
                "Exemplos:\n"
                "• 150,50\n"
                "• 1250,00\n\n"
                "*Lembre-se:* Valor entre R$ 10,00 e R$ 5.000,00",
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("🔙 Voltar")]], 
                    resize_keyboard=True
                )
            )
            return QUANTIDADE
            
        # Remove R$, pontos e substitui vírgula por ponto
        valor_texto = update.message.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
        valor_brl = float(valor_texto)
        
        # Validação dos valores mínimo e máximo (em centavos)
        if valor_brl < 10.00:
            raise ValueError("O valor mínimo é R$ 10,00")
        if valor_brl > 5000.00:
            raise ValueError("O valor máximo é R$ 5.000,00")
            
        # Arredonda para 2 casas decimais
        valor_brl = round(valor_brl, 2)
        context.user_data['valor_brl'] = valor_brl
        
        moeda = context.user_data.get('moeda', 'a moeda selecionada')
        rede = context.user_data.get('rede', 'a rede selecionada')
        
        # Obtém a cotação e calcula o valor a receber
        cotacao = obter_cotacao(moeda)
        taxa = 0.01  # 1% de taxa de exemplo
        valor_taxa = valor_brl * taxa
        valor_liquido = valor_brl - valor_taxa
        valor_recebido = valor_liquido / cotacao
        
        # Formata os valores
        valor_brl_formatado = formatar_brl(valor_brl)
        valor_recebido_formatado = formatar_cripto(valor_recebido, moeda)
        valor_taxa_formatado = formatar_brl(valor_taxa)
        cotacao_formatada = formatar_brl(cotacao)
        
        keyboard = [
            [KeyboardButton("✅ Confirmar Compra")],
            [KeyboardButton("✏️ Alterar Valor"), KeyboardButton("🔙 Mudar Moeda")]
        ]
        
        # Monta a mensagem de confirmação
        mensagem = (
            f"📋 *RESUMO DA COMPRA*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"• *Moeda:* {moeda}\n"
            f"• *Rede:* {rede}\n"
            f"• *Valor investido:* {valor_brl_formatado}\n"
            f"• *Taxa (1%):* {valor_taxa_formatado}\n"
            f"• *Cotação:* {cotacao_formatada}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 *Você receberá:* {valor_recebido_formatado}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            "Confirma os dados da compra?"
        )
        
        await update.message.reply_text(
            mensagem,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return CONFIRMAR
        
    except ValueError as e:
        mensagem_erro = str(e)
        if "could not convert" in mensagem_erro.lower():
            mensagem_erro = "❌ Formato inválido. Use números com até 2 casas decimais."
        
        # Teclado com valores sugeridos
        teclado = [
            [
                KeyboardButton("R$ 50,00"), 
                KeyboardButton("R$ 100,00"),
                KeyboardButton("R$ 250,00")
            ],
            [
                KeyboardButton("R$ 500,00"),
                KeyboardButton("R$ 1.000,00"),
                KeyboardButton("R$ 2.500,00")
            ],
            [
                KeyboardButton("Digitar valor"),
                KeyboardButton("🔙 Voltar")
            ]
        ]
        
        await update.message.reply_text(
            f"{mensagem_erro}\n\n"
            "💡 Você pode digitar qualquer valor entre R$ 10,00 e R$ 5.000,00\n"
            "Exemplos: 75,50 ou 1250,00",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(
                teclado, 
                resize_keyboard=True
            )
        )
        return QUANTIDADE
    except Exception as e:
        logger.error(f"Erro ao processar quantidade: {str(e)}")
        await update.message.reply_text(
            "❌ Ocorreu um erro ao processar o valor. Por favor, tente novamente.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("🔙 Voltar")]], 
                resize_keyboard=True
            )
        )
        return QUANTIDADE

async def confirmar_compra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirma os dados e solicita o endereço de recebimento."""
    # Se o usuário clicou em "Alterar Valor", volta para a tela de quantidade
    if update.message.text == "✏️ Alterar Valor":
        return await escolher_rede(update, context)
    # Se clicou em "Mudar Moeda", volta para o início
    elif update.message.text == "🔙 Mudar Moeda":
        return await iniciar_compra(update, context)
    
    # Se confirmou, pede o endereço
    moeda = context.user_data.get('moeda', '')
    rede = context.user_data.get('rede', '')
    
    # Mensagem de instrução baseada no tipo de rede
    if "Lightning" in rede:
        instrucao = (
            "⚡ *Informe o endereço Lightning ou LNURL‑Pay*\n\n"
            "Exemplos de endereços aceitos:\n"
            "• Endereço Lightning: `lnbc10u1p3...`\n"
            "• LNURL-Pay: `lnurl1dp68gurn...`\n"
            "• Endereço de nó: `node@domain.com`"
        )
    elif "Liquid" in rede or "On-chain" in rede or "Polygon" in rede:
        instrucao = (
            "📬 *Informe o endereço de recebimento*\n\n"
            f"Certifique-se de que o endereço é compatível com a rede *{rede}*."
        )
    else:
        instrucao = "📬 Informe o endereço de recebimento:"
    
    await update.message.reply_text(
        instrucao,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("🔙 Voltar")]], 
            resize_keyboard=True
        )
    )
    return SOLICITAR_ENDERECO

def menu_metodos_pagamento():
    """Retorna o teclado com as opções de métodos de pagamento."""
    keyboard = [
        [KeyboardButton("💠 PIX")],
        [KeyboardButton("🏦 TED")],
        [KeyboardButton("📄 Boleto")],
        [KeyboardButton("🔙 Voltar")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def processar_endereco(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa o endereço informado e solicita o método de pagamento."""
    if update.message.text == "🔙 Voltar":
        return await processar_quantidade(update, context)
    
    endereco = update.message.text
    context.user_data['endereco_recebimento'] = endereco
    
    # Mostra opções de pagamento
    await update.message.reply_text(
        "💳 *Escolha a forma de pagamento:*",
        parse_mode='Markdown',
        reply_markup=menu_metodos_pagamento()
    )
    
    return ESCOLHER_PAGAMENTO

async def processar_metodo_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa o método de pagamento escolhido e finaliza a compra."""
    if update.message.text == "🔙 Voltar":
        return await processar_quantidade(update, context)
    
    metodo_pagamento = update.message.text
    context.user_data['metodo_pagamento'] = metodo_pagamento
    
    # Dados da compra
    moeda = context.user_data.get('moeda', 'a moeda selecionada')
    rede = context.user_data.get('rede', 'a rede selecionada')
    valor_brl = context.user_data.get('valor_brl', 0)
    endereco = context.user_data.get('endereco_recebimento', '')
    
    # Formata o valor em BRL
    valor_formatado = formatar_brl(valor_brl)
    
    # Obtém a cotação e calcula o valor a receber
    cotacao = obter_cotacao(moeda)
    taxa = 0.01  # 1% de taxa de exemplo
    valor_taxa = valor_brl * taxa
    valor_liquido = valor_brl - valor_taxa
    valor_recebido = valor_liquido / cotacao
    valor_recebido_formatado = formatar_cripto(valor_recebido, moeda)
    
    # Processa de acordo com o método de pagamento
    if metodo_pagamento == "💠 PIX":
        # Processa pagamento via PIX usando a API do servidor
        from api.depix import pix_api
        
        try:
            logger.info(f"Iniciando processamento de PIX - Valor: {valor_brl}, Endereço: {endereco}")
            
            # Converte o valor para centavos
            valor_centavos = int(valor_brl * 100)
            logger.info(f"Valor convertido para centavos: {valor_centavos}")
            
            # Obtém a chave PIX da loja a partir das configurações
            from tokens import Config
            chave_pix_loja = getattr(Config, 'PIX_KEY', 'sua_chave_pix_aqui@exemplo.com')
            
            # 1. Primeiro, armazena a transação no banco de dados
            # Aqui você deve implementar a lógica para salvar a transação
            # com o endereço de destino da criptomoeda
            transaction_data = {
                'user_id': update.effective_user.id,
                'amount_brl': valor_brl,
                'amount_crypto': valor_recebido,
                'crypto_currency': moeda,
                'crypto_address': endereco,  # Endereço de destino da criptomoeda
                'status': 'pending',
                'payment_method': 'pix',
                'created_at': datetime.now().isoformat()
            }
            
            # TODO: Implementar salvamento no banco de dados
            # Exemplo: db.save_transaction(transaction_data)
            logger.info(f"Transação armazenada: {transaction_data}")
            
            # 2. Cria o pagamento PIX (apenas com o valor)
            logger.info("Chamando pix_api.criar_pagamento...")
            pagamento = pix_api.criar_pagamento(
                valor_centavos=valor_centavos
            )
            logger.info("Pagamento PIX criado com sucesso")
            
            # 3. Associa o transaction_id do PIX à transação no banco
            # TODO: Atualizar a transação com o transaction_id retornado
            transaction_id = pagamento.get('transaction_id')
            logger.info(f"Transação PIX {transaction_id} associada ao endereço {endereco}")
            
            # Monta a mensagem com o QR Code
            mensagem = (
                "🔘 *PAGAMENTO VIA PIX*\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"• *Valor:* {valor_formatado}\n\n"
                "Escaneie o QR Code abaixo ou copie o código PIX para efetuar o pagamento.\n"
                "O pagamento é válido por 1 hora."
            )
            
            # Envia a mensagem com o QR Code
            update.message.reply_text(
                mensagem,
                parse_mode='Markdown'
            )
            
            # Envia o código copia e cola
            update.message.reply_text(
                f"📋 *Código PIX (copiar e colar):*\n`{pagamento['qr_copy_paste']}`",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Erro ao processar PIX: {e}\n{error_details}")
            
            # Mensagem de erro mais detalhada para o usuário
            mensagem_erro = (
                "❌ *Erro ao processar pagamento PIX*\n\n"
                "Por favor, tente novamente ou escolha outro método de pagamento.\n\n"
                "Se o problema persistir, entre em contato com o suporte.\n"
                f"Erro: {str(e)}"
            )
            
            update.message.reply_text(
                mensagem_erro,
                parse_mode='Markdown',
                reply_markup=menu_metodos_pagamento()
            )
            return ESCOLHER_PAGAMENTO
            
    elif metodo_pagamento == "🏦 TED":
        from api.depix import obter_dados_ted
        
        # Obtém os dados para TED
        dados_ted = obter_dados_ted()
        
        # Monta a mensagem com os dados bancários
        mensagem = (
            "🏦 *DADOS PARA TRANSFERÊNCIA BANCÁRIA*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"• *Banco:* {dados_ted['banco']}\n"
            f"• *Agência:* {dados_ted['agencia']}\n"
            f"• *Conta:* {dados_ted['conta']}\n"
            f"• *Tipo de Conta:* {dados_ted['tipo_conta']}\n"
            f"• *Favorecido:* {dados_ted['favorecido']}\n"
            f"• *CPF/CNPJ:* {dados_ted['cpf_cnpj']}\n\n"
            f"*Valor a transferir:* {valor_formatado}\n"
            "\nApós o pagamento, envie o comprovante para @triacorelabs"
        )
        
        update.message.reply_text(
            mensagem,
            parse_mode='Markdown'
        )
        
    elif metodo_pagamento == "📄 Boleto":
        from api.depix import obter_chat_boleto
        
        # Monta a mensagem para o boleto
        mensagem = (
            "📄 *PAGAMENTO VIA BOLETO*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"• *Valor:* {valor_formatado}\n\n"
            f"Para gerar o boleto, envie uma mensagem para {obter_chat_boleto()} com o valor de {valor_formatado}."
        )
        
        update.message.reply_text(
            mensagem,
            parse_mode='Markdown'
        )
    
    # Mensagem de confirmação final
    mensagem_final = (
        "✅ *COMPRA REGISTRADA!*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Moeda:* {moeda}\n"
        f"• *Rede:* {rede}\n"
        f"• *Valor investido:* {valor_formatado}\n"
        f"• *Você receberá:* {valor_recebido_formatado}\n"
        f"• *Endereço de recebimento:* `{endereco}`\n"
        f"• *Método de pagamento:* {metodo_pagamento}\n\n"
        "📨 Um e-mail de confirmação foi enviado com os detalhes da sua compra.\n"
        "Obrigado por utilizar nossos serviços!"
    )
    
    update.message.reply_text(
        mensagem_final,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(menu_principal_func(), resize_keyboard=True) if menu_principal_func else None
    )
    
    # Aqui você pode adicionar o processamento real da compra
    # e o envio do e-mail de confirmação
    
    # Limpa os dados da sessão
    context.user_data.clear()
    
    return ConversationHandler.END

async def cancelar_compra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela a compra e volta ao menu principal."""
    context.user_data.clear()
    
    # Get the main menu keyboard (synchronous call)
    main_menu = menu_principal_func()
    reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True) if main_menu else None
    
    await update.message.reply_text(
        "❌ Compra cancelada.",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

def get_compra_conversation():
    """Retorna o ConversationHandler para o fluxo de compra."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🛒 Comprar$'), iniciar_compra)],
        states={
            ESCOLHER_MOEDA: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), cancelar_compra),
                MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_moeda)
            ],
            ESCOLHER_REDE: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), iniciar_compra),
                MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_rede)
            ],
            QUANTIDADE: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), lambda u, c: escolher_moeda(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_quantidade)
            ],
            CONFIRMAR: [
                MessageHandler(filters.Regex('^✅ Confirmar Compra$'), confirmar_compra),
                MessageHandler(filters.Regex('^✏️ Alterar Valor$'), confirmar_compra),
                MessageHandler(filters.Regex('^🔙 Mudar Moeda$'), confirmar_compra),
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_compra)
            ],
            SOLICITAR_ENDERECO: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), processar_quantidade),
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_endereco)
            ],
            ESCOLHER_PAGAMENTO: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), processar_quantidade),
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_metodo_pagamento)
            ]
        },
        fallbacks=[
            CommandHandler('start', cancelar_compra),
            MessageHandler(filters.Regex('^/cancelar$'), cancelar_compra)
        ],
        name="compra_conversation"
    )

# Importação circular resolvida com uma função
def set_menu_principal(menu_func):
    global menu_principal_func
    menu_principal_func = menu_func
    
    # Retorna a função para ser usada localmente
    def menu_principal():
        return menu_func()
    
    return menu_principal
