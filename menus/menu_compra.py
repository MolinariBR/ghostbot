from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, ConversationHandler, CommandHandler, filters
from telegram.ext import ContextTypes
import requests
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Any, Optional
import os

# Importa o módulo para integração com a API Voltz (Lightning Network)
from api.voltz import VoltzAPI

# Variável para armazenar a função do menu principal
menu_principal_func = None

def menu_principal():
    """Retorna o teclado do menu principal como uma lista de listas de strings."""
    if menu_principal_func:
        try:
            menu = menu_principal_func()
            # Garante que o menu seja uma lista de listas de strings
            if isinstance(menu, list) and all(isinstance(row, list) for row in menu):
                return menu
            logger.warning("menu_principal não retornou uma lista de listas válida")
        except Exception as e:
            logger.error(f"Erro ao obter menu principal: {str(e)}")
    # Retorna um menu padrão em caso de erro
    return [['/start']]

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Importa as funções de cotação
from api.cotacao import get_btc_price_brl, get_usdt_price_brl, get_depix_price_brl

async def obter_cotacao(moeda: str) -> float:
    """
    Obtém a cotação atual da moeda em BRL com margem de 2%.
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
    """Retorna as opções de moedas como lista de listas de KeyboardButton."""
    teclado = [
        [KeyboardButton("₿ Bitcoin (BTC)")],
        [KeyboardButton("💵 Tether (USDT)")],
        [KeyboardButton("💠 Depix")],
        [KeyboardButton("🔙 Voltar")]
    ]
    return teclado

def menu_redes(moeda: str):
    """Retorna as opções de rede para a moeda selecionada como lista de listas de KeyboardButton."""
    if "BTC" in moeda.upper():
        teclado = [
            [KeyboardButton("⛓️ On-chain")],
            [KeyboardButton("⚡ Lightning")],
            [KeyboardButton("💧 Liquid")],
            [KeyboardButton("🔙 Voltar")]
        ]
    elif "USDT" in moeda.upper():
        teclado = [
            [KeyboardButton("💧 Liquid")],
            [KeyboardButton("🟣 Polygon")],
            [KeyboardButton("🔙 Voltar")]
        ]
    else:  # Depix
        teclado = [
            [KeyboardButton("💧 Liquid")],
            [KeyboardButton("🔙 Voltar")]
        ]
    return teclado

async def iniciar_compra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o fluxo de compra mostrando as moedas disponíveis."""
    try:
        # Obtém as opções de moedas
        opcoes_moedas = menu_moedas()
        # Cria o ReplyKeyboardMarkup a partir da lista de opções
        reply_markup = ReplyKeyboardMarkup(opcoes_moedas, resize_keyboard=True)
        await update.message.reply_text(
            "💱 *ESCOLHA A MOEDA PARA COMPRA*\n\n"
            "Selecione a criptomoeda que deseja comprar:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Erro ao exibir opções de moedas: {str(e)}")
        # Tenta enviar uma mensagem de erro
        try:
            opcoes_moedas = menu_moedas()
            reply_markup = ReplyKeyboardMarkup(opcoes_moedas, resize_keyboard=True)
            await update.message.reply_text(
                "💱 *ESCOLHA A MOEDA PARA COMPRA*\n\n"
                "Selecione a criptomoeda que deseja comprar:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e2:
            logger.error(f"Falha ao enviar mensagem de erro: {str(e2)}")
    
    return ESCOLHER_MOEDA

async def escolher_moeda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a escolha da moeda e pede para selecionar a rede."""
    if update.message.text == "🔙 Voltar":
        try:
            # Obtém o menu principal
            main_menu = menu_principal_func()
            # Cria o ReplyKeyboardMarkup a partir da lista de opções
            reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True) if main_menu else None
            
            await update.message.reply_text(
                "Operação cancelada.",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Erro ao exibir menu principal: {str(e)}")
            try:
                await update.message.reply_text(
                    "Operação cancelada.",
                    parse_mode='Markdown'
                )
            except Exception as e2:
                logger.error(f"Falha ao enviar mensagem de cancelamento: {str(e2)}")
        return ConversationHandler.END
    
    try:
        moeda_escolhida = update.message.text
        context.user_data['moeda'] = moeda_escolhida
        
        # Obtém as opções de rede para a moeda selecionada
        opcoes_rede = menu_redes(moeda_escolhida)
        # Cria o ReplyKeyboardMarkup a partir da lista de opções
        reply_markup = ReplyKeyboardMarkup(opcoes_rede, resize_keyboard=True)
        
        await update.message.reply_text(
            f"🔄 *Rede de {moeda_escolhida}*\n\n"
            "Selecione a rede que deseja utilizar:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Erro ao processar escolha de moeda: {str(e)}")
        # Tenta enviar uma mensagem de erro
        try:
            await update.message.reply_text(
                "❌ *Erro ao processar a moeda selecionada*\n\n"
                "Por favor, tente novamente.",
                parse_mode='Markdown'
            )
            # Volta para o menu de moedas
            opcoes_moedas = menu_moedas()
            reply_markup = ReplyKeyboardMarkup(opcoes_moedas, resize_keyboard=True) if opcoes_moedas else None
            await update.message.reply_text(
                "💱 *ESCOLHA A MOEDA PARA COMPRA*\n\n"
                "Selecione a criptomoeda que deseja comprar:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return ESCOLHER_MOEDA
        except Exception as e2:
            logger.error(f"Falha ao enviar mensagem de erro: {str(e2)}")
            return ConversationHandler.END
    
    return ESCOLHER_REDE

async def escolher_rede(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a escolha da rede e pede o valor em BRL."""
    if update.message.text == "🔙 Voltar":
        return await iniciar_compra(update, context)
    
    try:
        rede = update.message.text
        context.user_data['rede'] = rede
        
        # Obtém a moeda selecionada
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
            ["R$ 50,00", "R$ 100,00", "R$ 250,00"],
            ["R$ 500,00", "R$ 1.000,00", "R$ 2.500,00"],
            ["Digitar valor", "🔙 Voltar"]
        ]
        
        # Cria o ReplyKeyboardMarkup a partir da lista de opções
        reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
        
        await update.message.reply_text(
            mensagem,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Erro ao processar escolha de rede: {str(e)}")
        # Tenta enviar uma mensagem de erro
        try:
            await update.message.reply_text(
                "❌ *Erro ao processar a rede selecionada*\n\n"
                "Por favor, tente novamente.",
                parse_mode='Markdown'
            )
            # Volta para o menu de redes
            moeda = context.user_data.get('moeda', '')
            opcoes_rede = menu_redes(moeda)
            reply_markup = ReplyKeyboardMarkup(opcoes_rede, resize_keyboard=True) if opcoes_rede else None
            await update.message.reply_text(
                f"🔄 *Rede de {moeda}*\n\n"
                "Selecione a rede que deseja utilizar:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return ESCOLHER_REDE
        except Exception as e2:
            logger.error(f"Falha ao enviar mensagem de erro: {str(e2)}")
            return ConversationHandler.END
    
    return QUANTIDADE

async def processar_quantidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a quantidade informada e mostra confirmação."""
    try:
        print("\n" + "="*50)
        print("DEBUG - INÍCIO processar_quantidade")
        print(f"update.message.text: {update.message.text}")
        print(f"context.user_data: {context.user_data}")
        print(f"context.bot_data: {getattr(context, 'bot_data', 'N/A')}")
        print(f"context.chat_data: {getattr(context, 'chat_data', 'N/A')}")
        print("-"*50)
        
        # Se o usuário clicou em "Digitar valor", pede para digitar
        if update.message.text == "Digitar valor":
            try:
                # Cria um teclado com o botão de voltar
                teclado_voltar = [["🔙 Voltar"]]
                reply_markup = ReplyKeyboardMarkup(teclado_voltar, resize_keyboard=True)
                
                await update.message.reply_text(
                    "💵 *Digite o valor desejado*\n\n"
                    "Exemplos:\n"
                    "• 150,50\n"
                    "• 1250,00\n\n"
                    "*Lembre-se:* Valor entre R$ 10,00 e R$ 5.000,00",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Erro ao exibir teclado de digitar valor: {str(e)}")
                # Tenta enviar sem teclado em caso de erro
                await update.message.reply_text(
                    "💵 *Digite o valor desejado*\n\n"
                    "Exemplos:\n"
                    "• 150,50\n"
                    "• 1250,00\n\n"
                    "*Lembre-se:* Valor entre R$ 10,00 e R$ 5.000,00\n\n"
                    "Digite 'voltar' para retornar.",
                    parse_mode='Markdown'
                )
            return QUANTIDADE
            
        # Remove R$ e espaços em branco
        valor_texto = update.message.text.replace('R$', '').strip()
        
        # Verifica se tem vírgula como separador decimal
        if ',' in valor_texto:
            # Se tiver vírgula, remove pontos de milhar e substitui vírgula por ponto
            valor_texto = valor_texto.replace('.', '').replace(',', '.')
        
        print(f"DEBUG - processar_quantidade - Valor convertido: {valor_texto}")
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
        
        print(f"DEBUG - processar_quantidade - Moeda: {moeda}, Rede: {rede}")
        print(f"DEBUG - processar_quantidade - Valor BRL: {valor_brl}")
        
        # Obtém a cotação e calcula o valor a receber
        cotacao = await obter_cotacao(moeda)
        print(f"DEBUG - processar_quantidade - Cotação: {cotacao}")
        # Salva a cotação no user_data para uso posterior
        context.user_data['cotacao'] = cotacao
        
        taxa = 0.01  # 1% de taxa de exemplo
        valor_taxa = valor_brl * taxa
        valor_liquido = valor_brl - valor_taxa
        valor_recebido = valor_liquido / cotacao
        
        print(f"DEBUG - processar_quantidade - Valor recebido: {valor_recebido}")
        
        # Formata os valores
        valor_brl_formatado = formatar_brl(valor_brl)
        valor_recebido_formatado = formatar_cripto(valor_recebido, moeda)
        valor_taxa_formatado = formatar_brl(valor_taxa)
        cotacao_formatada = formatar_brl(cotacao)
        
        print(f"DEBUG - processar_quantidade - Valores formatados:")
        print(f"- BRL: {valor_brl_formatado}")
        print(f"- Recebido: {valor_recebido_formatado}")
        print(f"- Taxa: {valor_taxa_formatado}")
        print(f"- Cotação: {cotacao_formatada}")
        
        try:
            # Cria o teclado de confirmação
            teclado_confirmacao = [
                ["✅ Confirmar Compra"],
                ["✏️ Alterar Valor", "🔙 Mudar Moeda"]
            ]
            reply_markup = ReplyKeyboardMarkup(teclado_confirmacao, resize_keyboard=True)
            
            # Monta a mensagem de confirmação
            mensagem = (
                f"📋 *RESUMO DA COMPRA*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"• *Moeda:* {moeda}\n"
                f"• *Rede:* {rede}\n"
                f"• *Valor investido:* {valor_brl_formatado}\n"
                f"• *Taxa (1%):* {valor_taxa_formatado}\n"
                f"• *Cotação:* {cotacao_formatada}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                "Confirma os dados da compra?"
            )
            
            print("DEBUG - processar_quantidade - Mensagem de confirmação montada")
            
            await update.message.reply_text(
                mensagem,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Erro ao exibir confirmação de compra: {str(e)}")
            # Tenta enviar sem teclado em caso de erro
            await update.message.reply_text(
                "❌ *Ocorreu um erro ao processar sua solicitação.*\n\n"
                "Por favor, tente novamente mais tarde.",
                parse_mode='Markdown'
            )
            # Volta para o menu de redes
            moeda = context.user_data.get('moeda', '')
            opcoes_rede = menu_redes(moeda)
            reply_markup = ReplyKeyboardMarkup(opcoes_rede, resize_keyboard=True) if opcoes_rede else None
            await update.message.reply_text(
                f"🔄 *Rede de {moeda}*\n\n"
                "Selecione a rede que deseja utilizar:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return ESCOLHER_REDE
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
    """Confirma os dados e solicita o endereço de recebimento (se não for Lightning) ou já exibe o menu de pagamento."""
    if update.message.text == "✏️ Alterar Valor":
        return await escolher_rede(update, context)
    elif update.message.text == "🔙 Mudar Moeda":
        return await iniciar_compra(update, context)

    rede = context.user_data.get('rede', '').lower()
    if 'lightning' in rede:
        # Não pede endereço, vai direto para o menu de métodos de pagamento
        try:
            opcoes_pagamento = menu_metodos_pagamento()
            reply_markup = ReplyKeyboardMarkup(opcoes_pagamento, resize_keyboard=True)
            await update.message.reply_text(
                "💳 *Escolha a forma de pagamento:*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            import traceback
            logger.error(f"Erro ao exibir métodos de pagamento: {str(e)}\n{traceback.format_exc()}")
            await update.message.reply_text(
                "❌ Ocorreu um erro ao exibir as opções de pagamento. Por favor, tente novamente.",
                reply_markup=ReplyKeyboardMarkup([["🔙 Voltar"]], resize_keyboard=True)
            )
            return SOLICITAR_ENDERECO
        return ESCOLHER_PAGAMENTO
    else:
        # Pede o endereço normalmente
        try:
            teclado_voltar = [["🔙 Voltar"]]
            reply_markup = ReplyKeyboardMarkup(teclado_voltar, resize_keyboard=True)
            await update.message.reply_text(
                "📬 Informe o endereço de recebimento:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Erro ao exibir teclado de endereço: {str(e)}")
            await update.message.reply_text(
                "📬 Informe o endereço de recebimento:\n\nDigite 'voltar' para retornar.",
                parse_mode='Markdown'
            )
        return SOLICITAR_ENDERECO

def menu_metodos_pagamento():
    """Retorna as opções de métodos de pagamento como uma lista de listas de strings."""
    return [
        ["💠 PIX"],
        ["🏦 TED"],
        ["📄 Boleto"],
        ["🔙 Voltar"]
    ]

async def processar_endereco(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa o endereço informado e solicita o método de pagamento."""
    if update.message.text == "🔙 Voltar":
        return await processar_quantidade(update, context)
    endereco = update.message.text
    context.user_data['endereco_recebimento'] = endereco
    try:
        opcoes_pagamento = menu_metodos_pagamento()
        reply_markup = ReplyKeyboardMarkup(opcoes_pagamento, resize_keyboard=True)
        await update.message.reply_text(
            "💳 *Escolha a forma de pagamento:*",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Erro ao exibir métodos de pagamento: {str(e)}")
        await update.message.reply_text(
            "❌ Ocorreu um erro ao exibir as opções de pagamento. Por favor, tente novamente.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Voltar"]], resize_keyboard=True)
        )
        return SOLICITAR_ENDERECO
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
    # Para Lightning, preenche endereço padrão
    if 'lightning' in rede.lower():
        endereco = 'voltzapi@tria.com'
        context.user_data['endereco_recebimento'] = endereco
    else:
        endereco = context.user_data.get('endereco_recebimento', '')

    valor_formatado = formatar_brl(valor_brl)
    cotacao = await obter_cotacao(moeda)
    taxa = 0.01  # 1% de taxa de exemplo
    valor_taxa = valor_brl * taxa
    valor_liquido = valor_brl - valor_taxa
    valor_recebido = valor_liquido / cotacao
    valor_recebido_formatado = formatar_cripto(valor_recebido, moeda)

    # FLUXO ESPECIAL PARA LIGHTNING: NÃO ACIONA VOLTZ, SÓ EXIBE INSTRUÇÃO
    # Só exibe a mensagem especial se NÃO for PIX
    if 'lightning' in rede.lower() and metodo_pagamento != '💠 PIX':
        from telegram import ReplyKeyboardMarkup as GlobalReplyKeyboardMarkup
        await update.message.reply_text(
            '''⚡ *Pagamento registrado!*

Seu pagamento tradicional foi recebido. Aguarde a confirmação manual do pagamento.\nAssim que for confirmado, você receberá instruções para saque via Lightning (LNURL).''',
            parse_mode='Markdown',
            reply_markup=GlobalReplyKeyboardMarkup([['/start']], resize_keyboard=True)
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Processa pagamento via PIX usando a API Depix (cliente paga em BRL)
    from api.depix import pix_api
    logger.info(f"Iniciando processamento de PIX - Valor: {valor_brl}, Endereço: {endereco}")
    # Garante que o endereço correto será usado para o pagamento
    endereco = context.user_data.get('endereco_recebimento', '')
    valor_centavos = int(round(valor_brl * 100))
    try:
        cobranca = pix_api.criar_pagamento(valor_centavos=valor_centavos, endereco=endereco)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Erro ao criar pagamento PIX: {e}\n{error_details}")
        mensagem_erro = (
            "❌ *Erro ao criar pagamento PIX*\n\n"
            "Por favor, tente novamente ou escolha outro método de pagamento.\n\n"
            "Se o problema persistir, entre em contato com o suporte.\n"
            f"Erro: {str(e)}"
        )
        await update.message.reply_text(
            mensagem_erro,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
        )
        if 'lightning' in rede.lower():
            return ConversationHandler.END
        return ESCOLHER_PAGAMENTO

    # Validação dos campos essenciais
    if cobranca.get('success') and 'data' in cobranca:
        data = cobranca['data']
        qr_code = data.get('qr_image_url')
        txid = data.get('transaction_id')
        copia_e_cola = data.get('qr_code_text') or data.get('qr_code')
    else:
        qr_code = cobranca.get('qr_image_url') or cobranca.get('qr_code')
        txid = cobranca.get('transaction_id') or cobranca.get('txid')
        copia_e_cola = cobranca.get('qr_code_text') or cobranca.get('copia_e_cola')

    if not qr_code or not copia_e_cola:
        logger.error(f"Resposta da API Depix incompleta: {cobranca}")
        await update.message.reply_text(
            "❌ *Erro ao gerar QR Code PIX. Tente novamente ou contate o suporte.*",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
        )
        if 'lightning' in rede.lower():
            return ConversationHandler.END
        return ESCOLHER_PAGAMENTO

    # Exibe QR Code e chave para o cliente pagar
    await update.message.reply_photo(
        photo=qr_code,
        caption='📱 *QR Code para pagamento*\n\nAponte a câmera do seu app de pagamento para escanear o QR Code acima.',
        parse_mode='Markdown'
    )
    # Removido o envio duplicado do Copia e Cola para evitar mensagens repetidas
    # await update.message.reply_text(
    #     f"🔗 *Copia e Cola:*\n`{copia_e_cola}`",
    #     parse_mode='Markdown'
    # )
    # --- PONTO DE INTEGRAÇÃO PARA CONFIRMAÇÃO AUTOMÁTICA DEPAGAMENTO PIX ---
    # Aqui, futuramente, implemente a verificação automática do pagamento via Depix.
    # Quando o pagamento for confirmado, libere o saque via Voltz para o cliente.
    # ------------------------------------------------------------------------
    mensagem_confirmacao = (
        '✅ *SOLICITAÇÃO DE DEPÓSITO RECEBIDA!*\n'
        '━━━━━━━━━━━━━━━━━━━━\n'
        f'• *Valor:* {valor_formatado}\n'
        f'• *Criptomoeda:* {moeda.upper()}\n'
        f'• *Endereço de destino:* `{endereco}`\n'
        f'• *ID da transação:* `{txid}`\n\n'
        '📱 *Pague o PIX usando o QR Code acima ou o código copia e cola:*\n\n'
        f'`{copia_e_cola}`\n\n'
        'Após o pagamento, aguarde alguns instantes para a confirmação.\n'
        'Obrigado pela preferência!'
    )
    await update.message.reply_text(
        mensagem_confirmacao,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
    )
    return ConversationHandler.END

async def cancelar_compra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancela a compra e volta ao menu principal.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto da conversa
        
    Returns:
        int: ConversationHandler.END para finalizar a conversa
    """
    try:
        user_id = update.effective_user.id
        logger.info(f"Usuário {user_id} cancelou o fluxo de compra")
        
        # Limpa os dados da sessão
        context.user_data.clear()
        
        # Obtém o menu principal de forma síncrona
        reply_markup = None
        try:
            if menu_principal_func:
                main_menu = menu_principal_func()
                if main_menu:
                    reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        except Exception as e:
            logger.error(f"Erro ao obter menu principal: {str(e)}")
        
        # Envia mensagem de confirmação
        try:
            await update.message.reply_text(
                "❌ *Compra cancelada.*\n\nVocê pode iniciar uma nova compra a qualquer momento.",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"Fluxo de compra cancelado para o usuário {user_id}")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de cancelamento: {str(e)}")
            # Tenta enviar sem o reply_markup
            try:
                await update.message.reply_text(
                    "❌ Compra cancelada.\n\nVocê pode iniciar uma nova compra a qualquer momento.",
                    parse_mode='Markdown'
                )
            except Exception as e2:
                logger.error(f"Falha ao enviar mensagem de cancelamento alternativa: {str(e2)}")
        
    except Exception as e:
        logger.error(f"Erro ao cancelar compra: {str(e)}")
        
        # Tenta enviar uma mensagem de erro genérica
        try:
            reply_markup = None
            if menu_principal_func:
                try:
                    main_menu = menu_principal_func()
                    if main_menu:
                        reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
                except Exception as e_menu:
                    logger.error(f"Erro ao obter menu principal para mensagem de erro: {str(e_menu)}")
            
            await update.message.reply_text(
                "❌ Ocorreu um erro ao cancelar a compra. Por favor, tente novamente.",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e2:
            logger.error(f"Falha ao enviar mensagem de erro de cancelamento: {str(e2)}")
            # Última tentativa sem reply_markup
            try:
                await update.message.reply_text(
                    "❌ Ocorreu um erro ao cancelar a compra. Por favor, tente novamente.",
                    parse_mode='Markdown'
                )
            except:
                pass  # Se falhar, não há mais o que fazer
    
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
