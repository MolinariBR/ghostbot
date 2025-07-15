#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu de Compra para Bot Telegram

Este módulo implementa um menu de compra completo com fluxo:
1. Seleção de moeda (BTC)
2. Seleção de rede (Lightning)
3. Seleção de valor
4. Resumo da compra
5. Forma de pagamento (PIX)
6. Confirmação do pedido
7. Criação do PIX
8. Aguardar endereço Lightning (quando PIX confirmado)
9. Envio do pagamento Lightning
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, Union
import sys
import os

# Garante que o diretório do projeto está no PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config.config import BASE_URL
from api.pedido_manager import PedidoManager
from urllib.parse import urljoin

print(f"[DEBUG] __file__: {__file__}")
print(f"[DEBUG] sys.path: {sys.path}")

def escape_markdown(text: str) -> str:
    """
    Escapa todos os caracteres especiais exigidos pelo MarkdownV2 do Telegram.
    """
    if not isinstance(text, str):
        text = str(text)
    # Lista oficial dos caracteres especiais do MarkdownV2
    return re.sub(r'([_\*\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)

def get_user_data(context, key, default):
    return context.user_data[key] if context and hasattr(context, 'user_data') and context.user_data and key in context.user_data else default

# Remover completamente qualquer fallback antigo de cotação/comissão/parceiro
# O menu só deve funcionar se o validador Python estiver disponível
validar_pedido = None
try:
    from cotacao.validador import validar_pedido
except ImportError:
    try:
        from cotacao.validador import validar_pedido
    except ImportError:
        try:
            from cotacao.validador import validar_pedido
        except ImportError:
            validar_pedido = None

# Fallback para PedidoManager se o módulo não existir
try:
    from core.validador_voltz import configurar as configurar_voltz, consultar_saldo, enviar_pagamento
except ImportError:
    def configurar_voltz(*args, **kwargs):
        pass
    async def consultar_saldo():
        return {'success': False, 'error': 'ValidadorVoltz não disponível'}
    async def enviar_pagamento(payment_request: str):
        return {'success': False, 'error': 'ValidadorVoltz não disponível'}

# Configuração de logging
logger = logging.getLogger(__name__)

# Estados da conversa
ESCOLHER_MOEDA, ESCOLHER_REDE, ESCOLHER_VALOR, RESUMO, FORMA_PAGAMENTO, CONFIRMAR, PAGAMENTO, AGUARDAR_LIGHTNING_ADDRESS = range(8)

# Configuração do Voltz (usar as mesmas credenciais do exemplo)
VOLTZ_CONFIG = {
    'wallet_id': "f3c366b7fb6f43fa9467c4dccedaf824",
    'admin_key': "8fce34f4b0f8446a990418bd167dc644", 
    'invoice_key': "b2f68df91c8848f6a1db26f2e403321f",
    'node_url': "https://lnvoltz.com"
}

# Configurar o validador Voltz globalmente
try:
    configurar_voltz(**VOLTZ_CONFIG)
except Exception as e:
    print(f"⚠️ [MENU] Erro ao configurar Voltz: {e}")

# Importar a instância global do PedidoManager
from api.pedido_manager import pedido_manager

# Dicionário global para salvar o último pedido de cada usuário
ULTIMOS_PEDIDOS = {}

# Função utilitária global para formatar valores monetários
def format_brl(val):
    return f"{val:.2f}".replace('.', ',')

def validar_endereco_lightning(endereco: str) -> bool:
    """
    Valida se o endereço Lightning é válido.
    
    Args:
        endereco: Endereço Lightning a ser validado
        
    Returns:
        True se válido, False caso contrário
    """
    if not endereco or not isinstance(endereco, str):
        return False
    
    # Padrões comuns de endereços Lightning
    padroes = [
        r'^lnbc\d+[a-zA-Z0-9]+$',  # Invoice Lightning
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  # Lightning Address
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+$',  # Lightning Address sem TLD
    ]
    
    for padrao in padroes:
        if re.match(padrao, endereco):
            return True
    
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o menu de compra."""
    print("🟢 [START] Handler start chamado")
    print(f"🟢 [START] Usuário: {update.effective_user.id if update and update.effective_user else 'None'}")
    
    if not update or not update.message:
        print("❌ [START] Update ou message é None")
        return ConversationHandler.END
    
    keyboard = [["Comprar"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        escape_markdown("🚀 *Bem-vindo ao Ghost P2P!*\n\nEscolha uma opção:"),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    print("🟢 [START] Retornando ESCOLHER_MOEDA")
    return ESCOLHER_MOEDA

async def escolher_moeda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para escolha de moeda."""
    print(f"🟡 [MOEDA] Handler escolher_moeda chamado")
    print(f"🟡 [MOEDA] Texto recebido: '{update.message.text if update and update.message else 'None'}'")
    print(f"[DEBUG] context.user_data (escolher_moeda): {context.user_data}")
    
    if not update or not update.message:
        print("❌ [MOEDA] Update ou message é None")
        return ConversationHandler.END
    
    if update.message.text == "Voltar":
        print("🔄 [MOEDA] Usuário clicou em Voltar, voltando para start")
        return await start(update, context)
    
    # Se o usuário clicou em "Comprar", mostrar menu de moeda
    if update.message.text == "Comprar":
        print("🟢 [MOEDA] Usuário clicou em Comprar, mostrando menu de moeda")
        if context and context.user_data:
            context.user_data.clear()
        
        keyboard = [["Bitcoin (BTC)", "Voltar"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await update.message.reply_text(
            escape_markdown("🪙 *Escolha a moeda:*\n\nQual moeda você deseja comprar?"),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        print("🟢 [MOEDA] Retornando ESCOLHER_MOEDA após mostrar menu de moeda")
        return ESCOLHER_MOEDA
    
    # Se o usuário escolheu Bitcoin, ir para escolher rede
    if update.message.text == "Bitcoin (BTC)":
        print("🟢 [MOEDA] Usuário escolheu Bitcoin, indo para escolher rede")
        if context and context.user_data:
            context.user_data['moeda'] = "BTC"
        
        keyboard = [["Lightning", "Voltar"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await update.message.reply_text(
            escape_markdown("🌐 *Escolha a rede:*\n\nQual rede você deseja usar?"),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        print("🟢 [MOEDA] Retornando ESCOLHER_REDE após escolher Bitcoin")
        return ESCOLHER_REDE
    
    print(f"⚠️ [MOEDA] Texto não reconhecido: '{update.message.text}', retornando ESCOLHER_MOEDA")
    return ESCOLHER_MOEDA

async def escolher_rede(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para escolha de rede."""
    print(f"🟡 [REDE] Handler escolher_rede chamado")
    print(f"🟡 [REDE] Texto recebido: '{update.message.text if update and update.message else 'None'}'")
    print(f"[DEBUG] context.user_data (escolher_rede): {context.user_data}")
    
    if not update or not update.message:
        print("❌ [REDE] Update ou message é None")
        return ConversationHandler.END
    
    if update.message.text == "Voltar":
        print("🔄 [REDE] Usuário clicou em Voltar, voltando para escolher_moeda")
        return await escolher_moeda(update, context)
    
    # Se o usuário escolheu Lightning, ir para escolher valor
    if update.message.text == "Lightning":
        print("🟢 [REDE] Usuário escolheu Lightning, indo para escolher valor")
        if context and context.user_data:
            context.user_data['rede'] = "lightning"
        
        keyboard = [
            ["R$ 10,00", "R$ 25,00", "R$ 50,00"],
            ["R$ 100,00", "R$ 250,00", "R$ 500,00"],
            ["Voltar"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await update.message.reply_text(
            escape_markdown("💰 *Escolha o valor:*\n\n"
            "Digite um valor em reais (ex: 75.50) ou escolha uma opção:"),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        print("🟢 [REDE] Retornando ESCOLHER_VALOR após escolher Lightning")
        return ESCOLHER_VALOR
    
    # Se chegou aqui, texto inválido para este estado
    print(f"⚠️ [REDE] Texto não reconhecido: '{update.message.text}', retornando ESCOLHER_REDE")
    await update.message.reply_text(
        escape_markdown("❌ *Opção inválida!*\n\nPor favor, escolha uma das opções do menu."),
        parse_mode='Markdown'
    )
    return ESCOLHER_REDE

async def escolher_valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para escolha de valor."""
    print(f"[DEBUG] context.user_data (escolher_valor): {context.user_data}")
    if not update or not update.message:
        return ConversationHandler.END
    
    if update.message.text == "Voltar":
        return await escolher_rede(update, context)
    
    # Verificar se é um valor personalizado digitado
    if not update.message or not update.message.text:
        return ConversationHandler.END
    
    texto_valor = update.message.text.strip()
    
    # Tentar converter para número
    try:
        valor_digitado = float(texto_valor)
        if valor_digitado >= 10:  # Valor mínimo
            if context and context.user_data:
                context.user_data['valor_personalizado'] = valor_digitado
            print(f"🟢 [MENU] Usuário digitou valor personalizado: R$ {valor_digitado:.2f}")
            return await processar_valor_personalizado(update, context, valor_digitado)
        else:
            if update and update.message:
                await update.message.reply_text(
                    escape_markdown("❌ *Valor muito baixo!*\n\n"
                    "O valor mínimo para compra é R$ 10,00.\n"
                    "Digite um valor maior ou escolha uma opção:"),
                    parse_mode='Markdown'
                )
            return ESCOLHER_VALOR
    except ValueError:
        # Não é um número, verificar se é um dos valores fixos
        pass
    
    # Verificar se é um dos valores fixos
    valores_fixos = {
        "R$ 10,00": 10,
        "R$ 25,00": 25,
        "R$ 50,00": 50,
        "R$ 100,00": 100,
        "R$ 250,00": 250,
        "R$ 500,00": 500
    }
    
    valor_escolhido = valores_fixos.get(texto_valor, 0)
    if valor_escolhido > 0:
        print(f"🟢 [MENU] Usuário escolheu valor fixo: R$ {valor_escolhido:.2f}")
        return await processar_valor_personalizado(update, context, valor_escolhido)
    
    # Se chegou aqui, não é um valor válido
    if update and update.message:
        await update.message.reply_text(
            escape_markdown("❌ *Valor inválido!*\n\n"
            "Digite um valor em reais (ex: 75.50) ou escolha uma opção:"),
            parse_mode='Markdown'
        )
    return ESCOLHER_VALOR

async def processar_valor_personalizado(update: Update, context: ContextTypes.DEFAULT_TYPE, valor_brl: float) -> int:
    print(f"[DEBUG] context.user_data (processar_valor_personalizado): {context.user_data}")
    print(f"[DEBUG] validar_pedido: {validar_pedido}")
    if not validar_pedido:
        await mostrar_erro_cotacao(update, "Erro interno: validador Python não disponível. Avise o suporte.")
        return ESCOLHER_VALOR
    try:
        user_id = str(update.effective_user.id) if update and update.effective_user else '0'
        moeda = 'btc'
        compras = 0
        metodo = 'pix'
        rede = 'lightning'
        print(f"[DEBUG] Chamando validar_pedido com: moeda={moeda}, valor_brl={valor_brl}, user_id={user_id}, compras={compras}, metodo={metodo}, rede={rede}")
        validador = validar_pedido(moeda, valor_brl, user_id, compras, metodo, rede)
        print(f"[DEBUG] Resultado do validar_pedido: {validador}")
        if not validador or not isinstance(validador, dict):
            await mostrar_erro_cotacao(update, "Erro ao validar pedido. Avise o suporte.")
            return ESCOLHER_VALOR
        if context and context.user_data:
            context.user_data['cotacao_completa'] = validador
            context.user_data['valor_real'] = valor_brl
            context.user_data['valor_sats'] = validador.get('valor_recebe', {}).get('sats', 0)
        # Salva o último pedido válido do usuário
        ULTIMOS_PEDIDOS[user_id] = validador
        cotacao_info = validador.get('cotacao', {})
        comissao_info = validador.get('comissao', {})
        parceiro_info = validador.get('parceiro', {})
        valor_recebe_info = validador.get('valor_recebe', {})
        limite_info = validador.get('limite', {})
        percentual = comissao_info.get('percentual', 0)
        percentual_str = f"({percentual}%)"
        valor_brl_fmt = format_brl(valor_brl)
        comissao_fmt = format_brl(comissao_info.get('valor', 0))
        parceiro_fmt = format_brl(parceiro_info.get('valor', 0))
        limite_fmt = format_brl(limite_info.get('maximo', 0))
        valor_liquido_fmt = format_brl(valor_recebe_info.get('brl', valor_brl))
        resumo_texto = (
            escape_markdown("📋 *Resumo da Compra:*\n\n") +
            escape_markdown("🪙 *Moeda:* ") + escape_markdown("BTC") + "\n" +
            escape_markdown("🌐 *Rede:* ") + escape_markdown("Lightning") + "\n\n" +
            escape_markdown("💰 *Valor do Investimento:* ") + escape_markdown(valor_brl_fmt) + "\n" +
            escape_markdown("💱 *Cotação BTC:* ") + escape_markdown(str(cotacao_info.get('preco_btc', 0))) + "\n" +
            escape_markdown("📊 *Fonte:* ") + escape_markdown("Python Validador") + "\n\n" +
            escape_markdown("💸 *Comissão:* ") + escape_markdown(comissao_fmt) + " " + escape_markdown(percentual_str) + "\n" +
            escape_markdown("🤝 *Taxa Parceiro:* ") + escape_markdown(parceiro_fmt) + "\n" +
            escape_markdown("💰 *Limite Máximo:* ") + escape_markdown(limite_fmt) + "\n\n" +
            escape_markdown("⚡ *Você Recebe:* ") + escape_markdown(str(valor_recebe_info.get('sats', 0))) + " sats\n" +
            escape_markdown("💵 *Valor Líquido:* ") + escape_markdown(valor_liquido_fmt) + "\n\n" +
            escape_markdown("🆔 *ID Transação:* ") + escape_markdown(str(validador.get('gtxid', 'N/A')))
        )
        keyboard = [["Confirmar"], ["Voltar"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        if update and update.message:
            await update.message.reply_text(
                resumo_texto,
                reply_markup=reply_markup,
                parse_mode='MarkdownV2'
            )
        return RESUMO
    except Exception as e:
        print(f"❌ [MENU] Erro ao processar valor: {e}")
        await mostrar_erro_cotacao(update, f"Erro inesperado: {str(e)}")
    return ESCOLHER_VALOR

async def mostrar_erro_cotacao(update: Update, mensagem: str):
    """Mostra erro de cotação e volta para escolha de valor."""
    if not update or not update.message:
        return
    
    keyboard = [
        ["R$ 10,00", "R$ 25,00", "R$ 50,00"],
        ["R$ 100,00", "R$ 250,00", "R$ 500,00"],
        ["Voltar"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        escape_markdown(f"❌ *Erro:* {mensagem}\n\n") +
        escape_markdown("Escolha um valor ou digite um valor personalizado:"),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update or not update.message:
        return ConversationHandler.END
    if update.message.text == "Confirmar":
        # Salvar o pedido aqui (garantindo que só salva uma vez)
        if context and context.user_data is not None and context.user_data.get('pedido_salvo'):
            print("[DEBUG] Pedido já salvo, ignorando nova tentativa.")
            return ConversationHandler.END
        user_id = str(update.effective_user.id) if update and update.effective_user else '0'
        validador = get_user_data(context, 'cotacao_completa', None)
        if not validador:
            validador = ULTIMOS_PEDIDOS.get(user_id)
            if validador:
                if context and context.user_data is not None:
                    context.user_data['cotacao_completa'] = validador
        if not validador:
            await mostrar_erro_cotacao(update, "Dados do pedido não encontrados")
            return ConversationHandler.END
        if validador is not None:
            gtxid = validador.get('gtxid', str(update.effective_user.id) if update and update.effective_user else '0' + '_' + datetime.now().strftime('%Y%m%d%H%M%S'))
            chatid = str(update.effective_user.id) if update and update.effective_user else '0'
            moeda = get_user_data(context, 'moeda', 'BTC')
            rede = get_user_data(context, 'rede', 'lightning')
            amount_in_cents = validador.get('amount_in_cents', 0)
            comissao_in_cents = validador.get('comissao', {}).get('valor_in_cents', 0)
            parceiro_in_cents = validador.get('parceiro', {}).get('valor_in_cents', 0)
            limites_in_cents = validador.get('limite', {}).get('maximo_in_cents', 0)
            cotacao = validador.get('cotacao', {}).get('preco_btc', 0)
            send = validador.get('send_in_cents', 0)
            forma_pagamento = 'pix'
            depix_id = ''
            blockchainTxID = ''
            status = 'aguardando_pagamento'
            pagamento_verificado = 0
            tentativas_verificacao = 0
            criado_em = datetime.now().isoformat()
            atualizado_em = datetime.now().isoformat()
            lightning_address = ''
            pedido_data = {
                'gtxid': gtxid,
                'chatid': chatid,
                'moeda': moeda,
                'rede': rede,
                'amount_in_cents': amount_in_cents,
                'comissao_in_cents': comissao_in_cents,
                'parceiro_in_cents': parceiro_in_cents,
                'limites_in_cents': limites_in_cents,
                'cotacao': cotacao,
                'send': send,
                'forma_pagamento': forma_pagamento,
                'depix_id': depix_id,
                'blockchainTxID': blockchainTxID,
                'status': status,
                'pagamento_verificado': pagamento_verificado,
                'tentativas_verificacao': tentativas_verificacao,
                'criado_em': criado_em,
                'atualizado_em': atualizado_em,
                'lightning_address': lightning_address
            }
            print(f"🟡 [MENU] Salvando pedido no banco: {pedido_data}")
            if pedido_manager:
                sucesso_salvar = pedido_manager.salvar_pedido(pedido_data)
            else:
                sucesso_salvar = False
            if sucesso_salvar:
                if context and context.user_data is not None:
                    context.user_data['pedido_salvo'] = True
                pedido_id = pedido_data.get('gtxid', 0)
                if context and context.user_data is not None:
                    context.user_data['pedido_id'] = pedido_id
                print(f"✅ [MENU] Pedido salvo com ID: {pedido_id}")
                # prossegue normalmente para gerar o PIX e enviar ao usuário
                try:
                    import requests
                    pix_data = {
                        'amount_in_cents': int(validador.get('valor_brl', 0) * 100)
                    }
                    url = urljoin(BASE_URL + '/', 'bot_deposit.php')
                    response = requests.post(
                        url,
                        json=pix_data,
                        timeout=30
                    )
                    if response.status_code == 200:
                        pix_response = response.json()
                        print(f"[DEBUG] Resposta do backend: {pix_response}")
                        if pix_response and isinstance(pix_response, dict) and pix_response.get('success'):
                            pix_data_dict = pix_response.get('data', {})
                            print(f"[DEBUG] pix_data_dict: {pix_data_dict}")
                            if not isinstance(pix_data_dict, dict):
                                pix_data_dict = {}
                            qr_code_url = pix_data_dict.get('qr_image_url', '')
                            print(f"[DEBUG] qr_code_url: {qr_code_url}")
                            copia_cola = pix_data_dict.get('qr_copy_paste', '')
                            pix_valor_fmt = escape_markdown(format_brl(validador.get('valor_brl', 0)))
                            pix_valor_sats = escape_markdown(str(validador.get('valor_sats', 0)))
                            pix_pedido_id = escape_markdown(str(pedido_id))
                            pix_texto = (
                                escape_markdown("💳 **Pagamento PIX Criado!**\n\n") +
                                escape_markdown("📋 **Pedido #") + pix_pedido_id + escape_markdown("**\n") +
                                escape_markdown("💰 **Valor:** ") + pix_valor_fmt + "\n" +
                                escape_markdown("⚡ **Valor:** ") + pix_valor_sats + "\n\n" +
                                escape_markdown("📱 **QR Code:**")
                            )
                            print('[DEBUG] Texto enviado (PIX):', pix_texto)
                            if update and update.message:
                                await update.message.reply_text(
                                    pix_texto,
                                    parse_mode='MarkdownV2'
                                )
                            if context and context.bot and update and update.effective_chat:
                                if qr_code_url:
                                    await context.bot.send_photo(
                                        chat_id=update.effective_chat.id,
                                        photo=qr_code_url,
                                        caption="📱 Escaneie o QR Code para pagar"
                                    )
                                else:
                                    await update.message.reply_text(
                                        escape_markdown("❌ Erro ao obter o QR Code do PIX. Tente novamente ou contate o suporte."),
                                        parse_mode='Markdown'
                                    )
                                await context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=escape_markdown("📋 **Copia e Cola:**\n`") + copia_cola + escape_markdown("`\n\n") +
                                         escape_markdown("💡 **Instruções:**\n") +
                                         escape_markdown("1. Copie o código acima\n") +
                                         escape_markdown("2. Abra seu app bancário\n") +
                                         escape_markdown("3. Cole no PIX\n") +
                                         escape_markdown("4. Confirme o pagamento\n\n") +
                                         escape_markdown("⏰ **Tempo limite:** 30 minutos\n\n") +
                                         escape_markdown("🔄 **Verificação automática ativada!**\n") +
                                         escape_markdown("O sistema verificará o pagamento automaticamente."),
                                    parse_mode='Markdown'
                                )
                                keyboard = [
                                    ["🆘 Suporte"]
                                ]
                                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                                await context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=escape_markdown("❓ **Precisa de ajuda?**\nClique no botão abaixo:"),
                                    reply_markup=reply_markup,
                                    parse_mode='Markdown'
                                )
                            print(f"✅ [MENU] PIX criado com sucesso para pedido #{pedido_id}")
                        else:
                            error_msg = pix_response.get('error', 'Erro desconhecido') if pix_response and isinstance(pix_response, dict) else 'Erro desconhecido'
                            if update and update.message:
                                await update.message.reply_text(
                                    escape_markdown("❌ **Erro ao criar PIX:**\n") + error_msg + "\n\n" +
                                    escape_markdown("Tente novamente ou entre em contato com o suporte."),
                                    parse_mode='Markdown'
                                )
                    else:
                        if update and update.message:
                            await update.message.reply_text(
                                escape_markdown("❌ **Erro na API:** Status ") + escape_markdown(str(response.status_code)) + "\n\n" +
                                escape_markdown("Tente novamente ou entre em contato com o suporte."),
                                parse_mode='Markdown'
                            )
                except Exception as e:
                    print(f"❌ [MENU] Erro ao criar PIX: {e}")
                    if update and update.message:
                        await update.message.reply_text(
                            escape_markdown("❌ **Erro ao criar PIX:**\n") + escape_markdown(str(e)) + "\n\n" +
                            escape_markdown("Tente novamente ou entre em contato com o suporte."),
                            parse_mode='Markdown'
                        )
            else:
                error_msg = "Erro interno ao salvar pedido. Tente novamente ou contate o suporte."
                print(f"❌ [MENU] Erro ao salvar pedido: Falha ao salvar no banco. Veja logs do PedidoManager para detalhes.")
                if update and update.message:
                    await update.message.reply_text(
                        escape_markdown("❌ **Erro ao salvar pedido:**\n") + error_msg + "\n\n" +
                        escape_markdown("Tente novamente ou entre em contato com o suporte."),
                        parse_mode='Markdown'
                    )
            return ConversationHandler.END
        else:
            await mostrar_erro_cotacao(update, "Dados do pedido não encontrados")
            return ConversationHandler.END
    elif update.message.text == "Voltar":
        return ESCOLHER_VALOR
    # Exibe o resumo apenas na primeira entrada
    user_id = str(update.effective_user.id) if update and update.effective_user else '0'
    validador = get_user_data(context, 'cotacao_completa', None)
    if not validador:
        validador = ULTIMOS_PEDIDOS.get(user_id)
        if validador:
            if context and context.user_data is not None:
                context.user_data['cotacao_completa'] = validador
    if not validador:
        await mostrar_erro_cotacao(update, "Dados do pedido não encontrados")
        return ConversationHandler.END
    cotacao_info = validador.get('cotacao', {})
    comissao_info = validador.get('comissao', {})
    parceiro_info = validador.get('parceiro', {})
    valor_recebe_info = validador.get('valor_recebe', {})
    limite_info = validador.get('limite', {})
    valor_brl = validador.get('valor_brl', 0)
    valor_sats = valor_recebe_info.get('sats', 0)
    percentual = comissao_info.get('percentual', 0)
    percentual_str = f"({percentual}%)"
    valor_brl_fmt = format_brl(valor_brl)
    comissao_fmt = format_brl(comissao_info.get('valor', 0))
    parceiro_fmt = format_brl(parceiro_info.get('valor', 0))
    limite_fmt = format_brl(limite_info.get('maximo', 0))
    valor_liquido_fmt = format_brl(valor_recebe_info.get('brl', valor_brl))
    resumo_texto = (
        escape_markdown("📋 *Resumo da Compra:*\n\n") +
        escape_markdown("🪙 *Moeda:* ") + escape_markdown("BTC") + "\n" +
        escape_markdown("🌐 *Rede:* ") + escape_markdown("Lightning") + "\n\n" +
        escape_markdown("💰 *Valor do Investimento:* ") + escape_markdown(valor_brl_fmt) + "\n" +
        escape_markdown("💱 *Cotação BTC:* ") + escape_markdown(str(cotacao_info.get('preco_btc', 0))) + "\n" +
        escape_markdown("📊 *Fonte:* ") + escape_markdown("Python Validador") + "\n\n" +
        escape_markdown("💸 *Comissão:* ") + escape_markdown(comissao_fmt) + " " + escape_markdown(percentual_str) + "\n" +
        escape_markdown("🤝 *Taxa Parceiro:* ") + escape_markdown(parceiro_fmt) + "\n" +
        escape_markdown("💰 *Limite Máximo:* ") + escape_markdown(limite_fmt) + "\n\n" +
        escape_markdown("⚡ *Você Recebe:* ") + escape_markdown(str(valor_sats)) + " sats\n" +
        escape_markdown("💵 *Valor Líquido:* ") + escape_markdown(valor_liquido_fmt) + "\n\n" +
        escape_markdown("🆔 *ID Transação:* ") + escape_markdown(str(validador.get('gtxid', 'N/A')))
    )
    keyboard = [["Confirmar"], ["Voltar"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    if update and update.message:
        await update.message.reply_text(
            resumo_texto,
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )
    return RESUMO

async def forma_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para escolha da forma de pagamento."""
    if not update or not update.message:
        return ConversationHandler.END
    
    if update.message.text == "Voltar":
        return await resumo(update, context)
    
    print("🟢 [MENU] Usuário confirmou resumo")
    
    keyboard = [["PIX"], ["Voltar"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        escape_markdown("💳 *Forma de Pagamento:*\n\nEscolha como deseja pagar:"),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return PAGAMENTO

async def pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f"[DEBUG] pedido_manager em pagamento: {pedido_manager} (type: {type(pedido_manager)})")
    print(f"[DEBUG] context.user_data (pagamento): {context.user_data}")
    # Controle de múltiplos cliques e duplicidade de salvamento
    if context and context.user_data is not None and context.user_data.get('pedido_em_processamento'):
        if update and update.message:
            await update.message.reply_text(
                escape_markdown("⏳ Seu pedido já está sendo processado. Aguarde a finalização antes de tentar novamente."),
                parse_mode='Markdown'
            )
        return ConversationHandler.END
    if context and context.user_data is not None:
        context.user_data['pedido_em_processamento'] = True
    try:
        if not update or not update.message:
            return ConversationHandler.END
        if update.message.text == "Cancelar":
            return await start(update, context)
        # Flag para garantir que o pedido só será salvo uma vez
        if context and context.user_data is not None and context.user_data.get('pedido_salvo'):
            print("[DEBUG] Pedido já salvo, ignorando nova tentativa.")
            return ConversationHandler.END
        user_id = str(update.effective_user.id) if update and update.effective_user else '0'
        validador = get_user_data(context, 'cotacao_completa', None)
        if not validador:
            validador = ULTIMOS_PEDIDOS.get(user_id)
            if validador:
                if context and context.user_data is not None:
                    context.user_data['cotacao_completa'] = validador
        if not validador:
            await mostrar_erro_cotacao(update, "Dados do pedido não encontrados")
            return ConversationHandler.END
        if validador is not None:
            gtxid = validador.get('gtxid', str(update.effective_user.id) if update and update.effective_user else '0' + '_' + datetime.now().strftime('%Y%m%d%H%M%S'))
            chatid = str(update.effective_user.id) if update and update.effective_user else '0'
            moeda = get_user_data(context, 'moeda', 'BTC')
            rede = get_user_data(context, 'rede', 'lightning')
            amount_in_cents = validador.get('amount_in_cents', 0)
            comissao_in_cents = validador.get('comissao', {}).get('valor_in_cents', 0)
            parceiro_in_cents = validador.get('parceiro', {}).get('valor_in_cents', 0)
            limites_in_cents = validador.get('limite', {}).get('maximo_in_cents', 0)
            cotacao = validador.get('cotacao', {}).get('preco_btc', 0)
            send = validador.get('send_in_cents', 0)
            forma_pagamento = 'pix'
            depix_id = ''
            blockchainTxID = ''
            status = 'aguardando_pagamento'
            pagamento_verificado = 0
            tentativas_verificacao = 0
            criado_em = datetime.now().isoformat()
            atualizado_em = datetime.now().isoformat()
            lightning_address = ''
            pedido_data = {
                'gtxid': gtxid,
                'chatid': chatid,
                'moeda': moeda,
                'rede': rede,
                'amount_in_cents': amount_in_cents,
                'comissao_in_cents': comissao_in_cents,
                'parceiro_in_cents': parceiro_in_cents,
                'limites_in_cents': limites_in_cents,
                'cotacao': cotacao,
                'send': send,
                'forma_pagamento': forma_pagamento,
                'depix_id': depix_id,
                'blockchainTxID': blockchainTxID,
                'status': status,
                'pagamento_verificado': pagamento_verificado,
                'tentativas_verificacao': tentativas_verificacao,
                'criado_em': criado_em,
                'atualizado_em': atualizado_em,
                'lightning_address': lightning_address
            }
            print(f"🟡 [MENU] Salvando pedido no banco: {pedido_data}")
            if pedido_manager:
                sucesso_salvar = pedido_manager.salvar_pedido(pedido_data)
            else:
                sucesso_salvar = False
            if sucesso_salvar:
                if context and context.user_data is not None:
                    context.user_data['pedido_salvo'] = True
                pedido_id = pedido_data.get('gtxid', 0)
                if context and context.user_data is not None:
                    context.user_data['pedido_id'] = pedido_id
                print(f"✅ [MENU] Pedido salvo com ID: {pedido_id}")
                # prossegue normalmente para gerar o PIX e enviar ao usuário
                try:
                    import requests
                    pix_data = {
                        'amount_in_cents': int(validador.get('valor_brl', 0) * 100)
                    }
                    url = urljoin(BASE_URL + '/', 'bot_deposit.php')
                    response = requests.post(
                        url,
                        json=pix_data,
                        timeout=30
                    )
                    if response.status_code == 200:
                        pix_response = response.json()
                        if pix_response and isinstance(pix_response, dict) and pix_response.get('success'):
                            pix_data_dict = pix_response.get('data', {})
                            if not isinstance(pix_data_dict, dict):
                                pix_data_dict = {}
                            qr_code_url = pix_data_dict.get('qr_image_url', '')
                            print(f"[DEBUG] qr_code_url: {qr_code_url}")
                            copia_cola = pix_data_dict.get('qr_copy_paste', '')
                            pix_valor_fmt = escape_markdown(format_brl(validador.get('valor_brl', 0)))
                            pix_valor_sats = escape_markdown(str(validador.get('valor_sats', 0)))
                            pix_pedido_id = escape_markdown(str(pedido_id))
                            pix_texto = (
                                escape_markdown("💳 **Pagamento PIX Criado!**\n\n") +
                                escape_markdown("📋 **Pedido #") + pix_pedido_id + escape_markdown("**\n") +
                                escape_markdown("💰 **Valor:** ") + pix_valor_fmt + "\n" +
                                escape_markdown("⚡ **Valor:** ") + pix_valor_sats + "\n\n" +
                                escape_markdown("📱 **QR Code:**")
                            )
                            print('[DEBUG] Texto enviado (PIX):', pix_texto)
                            if update and update.message:
                                await update.message.reply_text(
                                    pix_texto,
                                    parse_mode='MarkdownV2'
                                )
                            if context and context.bot and update and update.effective_chat:
                                if qr_code_url:
                                    await context.bot.send_photo(
                                        chat_id=update.effective_chat.id,
                                        photo=qr_code_url,
                                        caption="📱 Escaneie o QR Code para pagar"
                                    )
                                else:
                                    await update.message.reply_text(
                                        escape_markdown("❌ Erro ao obter o QR Code do PIX. Tente novamente ou contate o suporte."),
                                        parse_mode='Markdown'
                                    )
                                await context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=escape_markdown("📋 **Copia e Cola:**\n`") + copia_cola + escape_markdown("`\n\n") +
                                         escape_markdown("💡 **Instruções:**\n") +
                                         escape_markdown("1. Copie o código acima\n") +
                                         escape_markdown("2. Abra seu app bancário\n") +
                                         escape_markdown("3. Cole no PIX\n") +
                                         escape_markdown("4. Confirme o pagamento\n\n") +
                                         escape_markdown("⏰ **Tempo limite:** 30 minutos\n\n") +
                                         escape_markdown("🔄 **Verificação automática ativada!**\n") +
                                         escape_markdown("O sistema verificará o pagamento automaticamente."),
                                    parse_mode='Markdown'
                                )
                                keyboard = [
                                    ["🆘 Suporte"]
                                ]
                                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                                await context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=escape_markdown("❓ **Precisa de ajuda?**\nClique no botão abaixo:"),
                                    reply_markup=reply_markup,
                                    parse_mode='Markdown'
                                )
                            print(f"✅ [MENU] PIX criado com sucesso para pedido #{pedido_id}")
                        else:
                            error_msg = pix_response.get('error', 'Erro desconhecido') if pix_response and isinstance(pix_response, dict) else 'Erro desconhecido'
                            if update and update.message:
                                await update.message.reply_text(
                                    escape_markdown("❌ **Erro ao criar PIX:**\n") + error_msg + "\n\n" +
                                    escape_markdown("Tente novamente ou entre em contato com o suporte."),
                                    parse_mode='Markdown'
                                )
                    else:
                        if update and update.message:
                            await update.message.reply_text(
                                escape_markdown("❌ **Erro na API:** Status ") + escape_markdown(str(response.status_code)) + "\n\n" +
                                escape_markdown("Tente novamente ou entre em contato com o suporte."),
                                parse_mode='Markdown'
                            )
                except Exception as e:
                    print(f"❌ [MENU] Erro ao criar PIX: {e}")
                    if update and update.message:
                        await update.message.reply_text(
                            escape_markdown("❌ **Erro ao criar PIX:**\n") + escape_markdown(str(e)) + "\n\n" +
                            escape_markdown("Tente novamente ou entre em contato com o suporte."),
                            parse_mode='Markdown'
                        )
            else:
                error_msg = "Erro interno ao salvar pedido. Tente novamente ou contate o suporte."
                print(f"❌ [MENU] Erro ao salvar pedido: Falha ao salvar no banco. Veja logs do PedidoManager para detalhes.")
                if update and update.message:
                    await update.message.reply_text(
                        escape_markdown("❌ **Erro ao salvar pedido:**\n") + error_msg + "\n\n" +
                        escape_markdown("Tente novamente ou entre em contato com o suporte."),
                        parse_mode='Markdown'
                    )
            return ConversationHandler.END
        else:
            await mostrar_erro_cotacao(update, "Dados do pedido não encontrados")
            return ConversationHandler.END
    finally:
        if context and context.user_data is not None:
            context.user_data['pedido_em_processamento'] = False

async def aguardar_lightning_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler para aguardar o endereço Lightning do cliente.
    Esta função será chamada quando o pagamento PIX for confirmado.
    """
    if not update or not update.message or not update.message.text:
        return AGUARDAR_LIGHTNING_ADDRESS
    
    endereco_lightning = update.message.text.strip()
    
    print(f"🟢 [LIGHTNING] Usuário enviou endereço: {endereco_lightning}")
    
    # Validar endereço Lightning
    if not validar_endereco_lightning(endereco_lightning):
        await update.message.reply_text(
            escape_markdown("❌ **Endereço Lightning inválido!**\n\n"
            "Por favor, envie um endereço Lightning válido:\n"
            "• Lightning Address (ex: user@domain.com)\n"
            "• Invoice Lightning (ex: lnbc...)\n\n"
            "Tente novamente:"),
            parse_mode='Markdown'
        )
        return AGUARDAR_LIGHTNING_ADDRESS
    
    # Obter dados do pedido do contexto
    pedido_id = 0
    valor_sats = 0
    if context and context.user_data:
        pedido_id = get_user_data(context, 'pedido_id', 0)
        valor_sats = get_user_data(context, 'valor_sats', 0)
    
    if not pedido_id or not valor_sats:
        await update.message.reply_text(
            escape_markdown("❌ **Erro:** Dados do pedido não encontrados.\n"
            "Por favor, inicie uma nova compra."),
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    try:
        print(f"🟡 [LIGHTNING] Iniciando envio de {valor_sats} sats para {endereco_lightning}")
        
        # Consultar saldo antes do envio
        print("🟡 [LIGHTNING] Consultando saldo da carteira...")
        saldo_result = await consultar_saldo()
        
        if not saldo_result or not isinstance(saldo_result, dict) or not saldo_result.get('success'):
            error_msg = saldo_result.get('error', 'Erro desconhecido') if saldo_result and isinstance(saldo_result, dict) else 'Erro desconhecido'
            await update.message.reply_text(
                escape_markdown(f"❌ **Erro ao consultar saldo:**\n{error_msg}\n\n"
                "Entre em contato com o suporte."),
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        saldo_data = saldo_result.get('data', {})
        if not isinstance(saldo_data, dict):
            saldo_data = {}
        
        saldo_atual = saldo_data.get('balance', 0)
        print(f"🟡 [LIGHTNING] Saldo atual: {saldo_atual} sats")
        
        if saldo_atual < valor_sats:
            await update.message.reply_text(
                escape_markdown(f"❌ **Saldo insuficiente!**\n\n"
                "💰 Saldo atual: {saldo_atual:,} sats\n"
                "💸 Valor necessário: {valor_sats:,} sats\n"
                "📉 Diferença: {valor_sats - saldo_atual:,} sats\n\n"
                "Entre em contato com o suporte."),
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        # Enviar pagamento Lightning
        print(f"🟡 [LIGHTNING] Enviando pagamento...")
        pagamento_result = await enviar_pagamento(endereco_lightning)
        
        if pagamento_result and isinstance(pagamento_result, dict) and pagamento_result.get('success'):
            pagamento_data = pagamento_result.get('data', {})
            if not isinstance(pagamento_data, dict):
                pagamento_data = {}
            
            payment_hash = pagamento_data.get('payment_hash', '')
            fee = pagamento_data.get('fee', 0)
            
            print(f"✅ [LIGHTNING] Pagamento enviado! Hash: {payment_hash}")
            
            # Atualizar status do pedido no banco
            try:
                if pedido_manager:
                    pedido_manager.atualizar_status_pedido(
                        str(pedido_id),
                        'pagamento_enviado'
                    )
                    print(f"✅ [LIGHTNING] Status do pedido #{pedido_id} atualizado")
            except Exception as e:
                print(f"⚠️ [LIGHTNING] Erro ao atualizar status: {e}")
            
            # Mensagem de sucesso
            msg_pagamento = (
                escape_markdown("✅ **Pagamento Enviado com Sucesso!**\n\n") +
                escape_markdown("📋 **Pedido #") + escape_markdown(str(pedido_id)) + escape_markdown("**\n") +
                escape_markdown("💰 **Valor:** ") + escape_markdown(str(valor_sats)) + "\n" +
                escape_markdown("⚡ **Para:** ") + escape_markdown(str(endereco_lightning)) + "\n" +
                escape_markdown("🔗 **Hash:** `") + escape_markdown(str(payment_hash)) + escape_markdown("`\n") +
                escape_markdown("💸 **Taxa:** ") + escape_markdown(str(fee)) + escape_markdown(" sats\n\n") +
                escape_markdown("🎉 **Seus satoshis foram enviados!**\n\n") +
                escape_markdown("📱 **Próximos passos:**\n") +
                escape_markdown("1. Verifique seu app Lightning\n") +
                escape_markdown("2. Confirme o recebimento\n") +
                escape_markdown("3. Em caso de dúvidas, contate o suporte")
            )
            await update.message.reply_text(
                msg_pagamento,
                parse_mode='Markdown'
            )
            
            # Botão de suporte
            keyboard = [
                ["🆘 Suporte"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            
            if context and context.bot and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=escape_markdown("❓ **Precisa de ajuda?**\nClique no botão abaixo:"),
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            
        else:
            error_msg = pagamento_result.get('error', 'Erro desconhecido') if pagamento_result and isinstance(pagamento_result, dict) else 'Erro desconhecido'
            await update.message.reply_text(
                escape_markdown(f"❌ **Erro ao enviar pagamento:**\n{error_msg}\n\n"
                "Entre em contato com o suporte."),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        print(f"❌ [LIGHTNING] Erro ao processar pagamento: {e}")
        await update.message.reply_text(
            escape_markdown(f"❌ **Erro inesperado:**\n{str(e)}\n\n"
            "Entre em contato com o suporte."),
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para cancelar a operação."""
    if update and update.message:
        await update.message.reply_text(
            escape_markdown("❌ **Operação cancelada.**\n\n"
            "Use /start para iniciar uma nova compra."),
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

# Configuração do ConversationHandler
def get_conversation_handler():
    """Retorna o ConversationHandler configurado."""
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ESCOLHER_MOEDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_moeda)],
            ESCOLHER_REDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_rede)],
            ESCOLHER_VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_valor)],
            RESUMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, resumo)],
            FORMA_PAGAMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, forma_pagamento)],
            PAGAMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, pagamento)],
            AGUARDAR_LIGHTNING_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, aguardar_lightning_address)
            ]
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
        allow_reentry=True
    )

# Função para ativar o estado de aguardar endereço Lightning
async def ativar_aguardar_lightning_address(context: ContextTypes.DEFAULT_TYPE, user_id: int, pedido_id: int):
    """
    Ativa o estado de aguardar endereço Lightning para um usuário específico.
    Esta função será chamada quando o pagamento PIX for confirmado.
    """
    try:
        print(f"🟢 [LIGHTNING] Ativando aguardar endereço para usuário {user_id}, pedido {pedido_id}")
        
        # Definir o estado da conversa
        if context and context.user_data:
            context.user_data['pedido_id'] = pedido_id
        
        # Enviar mensagem solicitando o endereço Lightning
        if context and context.bot:
            await context.bot.send_message(
                chat_id=user_id,
                text=escape_markdown("🎉 **Pagamento PIX Confirmado!**\n\n"
                "✅ Seu pagamento foi recebido e confirmado!\n\n"
                "⚡ **Agora envie seu endereço Lightning:**\n\n"
                "📱 **Formatos aceitos:**\n" +
                "• Lightning Address: `user@domain.com`\n" +
                "• Invoice Lightning: `lnbc...`\n\n" +
                "💡 **Exemplo:** `sua_carteira@walletofsatoshi.com`\n\n" +
                "Envie seu endereço agora:"),
                parse_mode='Markdown'
            )
            
            print(f"✅ [LIGHTNING] Mensagem enviada para usuário {user_id}")
        
    except Exception as e:
        print(f"❌ [LIGHTNING] Erro ao ativar aguardar endereço: {e}")

# Exportar a função para ser usada pelo pedido_manager
__all__ = ['get_conversation_handler', 'ativar_aguardar_lightning_address']
