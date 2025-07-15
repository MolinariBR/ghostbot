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

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiais para MarkdownV2, incluindo o cifrão $"""
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r'([_\*\[\]()~`>#+\-=|{}.!$])', r'\\\1', text)

def get_user_data(context, key, default):
    return context.user_data[key] if context and hasattr(context, 'user_data') and context.user_data and key in context.user_data else default

# Fallback para cotação se o módulo não existir
try:
    from api.fallback_cotacao import get_cotacao_fallback_simples
    
    async def obter_cotacao_fallback():
        """Wrapper assíncrono para a função de cotação."""
        try:
            cotacao = get_cotacao_fallback_simples("bitcoin", "brl")
            return {
                'success': True,
                'data': {
                    'preco_btc': cotacao.get('price', 250000),
                    'fonte': cotacao.get('source', 'fallback')
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro na cotação: {str(e)}'
            }

    async def obter_cotacao_completa(valor_brl: float, user_id: int) -> Dict[str, Any]:
        """
        Obtém cotação completa com comissão, parceiro e valor a receber.
        Usa validador.php como fonte principal, fallback_cotacao.py como backup.
        
        Args:
            valor_brl: Valor em reais
            user_id: ID do usuário
            
        Returns:
            Dicionário com dados completos da cotação
        """
        try:
            import requests
            
            # Parâmetros para o validador.php
            params = {
                'moeda': 'bitcoin',
                'vs': 'brl',
                'valor': valor_brl,
                'chatid': str(user_id),
                'compras': 0,  # Número de compras do usuário
                'metodo': 'pix',
                'rede': 'lightning'
            }
            
            print(f"🟡 [COTACAO] Consultando validador.php com valor: R$ {valor_brl:.2f}")
            
            # Tentar primeiro o validador.php
            try:
                response = requests.get(
                    f"{BASE_URL}/cotacao/validador.php",
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and isinstance(data, dict) and data.get('success'):
                        validador = data.get('validador', {})
                        if not isinstance(validador, dict):
                            validador = {}
                        
                        # Extrair dados do validador
                        cotacao_data = validador.get('cotacao', {})
                        if not isinstance(cotacao_data, dict):
                            cotacao_data = {}
                        
                        comissao_data = validador.get('comissao', {})
                        if not isinstance(comissao_data, dict):
                            comissao_data = {}
                        
                        parceiro_data = validador.get('parceiro', {})
                        if not isinstance(parceiro_data, dict):
                            parceiro_data = {}
                        
                        limite_data = validador.get('limite', {})
                        if not isinstance(limite_data, dict):
                            limite_data = {}
                        
                        # Calcular valor a receber em sats
                        valor_recebe_brl = valor_brl
                        comissao_valor = comissao_data.get('comissao', 0)
                        taxa_parceiro = parceiro_data.get('taxa_parceiro', 0)
                        
                        if isinstance(comissao_valor, (int, float)):
                            valor_recebe_brl -= comissao_valor
                        if isinstance(taxa_parceiro, (int, float)):
                            valor_recebe_brl -= taxa_parceiro
                        
                        # Converter para sats
                        preco_btc = cotacao_data.get('valor', 250000)
                        valor_recebe_sats = 0
                        if preco_btc > 0:
                            valor_recebe_sats = (valor_recebe_brl / preco_btc) * 100_000_000
                        
                        print(f"✅ [COTACAO] Dados obtidos do validador.php: {valor_recebe_sats} sats")
                        
                        return {
                            'success': True,
                            'data': {
                                'valor_investimento': valor_brl,
                                'cotacao': {
                                    'preco_btc': preco_btc,
                                    'fonte': cotacao_data.get('origem', 'validador'),
                                    'data_atualizacao': cotacao_data.get('data_atualizacao', '')
                                },
                                'comissao': {
                                    'valor': comissao_valor,
                                    'percentual': comissao_data.get('percentual', 0)
                                },
                                'parceiro': {
                                    'valor': taxa_parceiro,
                                    'percentual': parceiro_data.get('percentual', 0)
                                },
                                'limite': {
                                    'maximo': limite_data.get('limite', 0)
                                },
                                'valor_recebe': {
                                    'brl': valor_recebe_brl,
                                    'sats': int(valor_recebe_sats)
                                },
                                'gtxid': data.get('gtxid', '')
                            }
                        }
                    else:
                        error_msg = data.get('error', 'Erro desconhecido') if data and isinstance(data, dict) else 'Erro desconhecido'
                        print(f"⚠️ [COTACAO] Validador.php retornou erro: {error_msg}")
                        # Continuar para o fallback
                else:
                    print(f"⚠️ [COTACAO] Validador.php retornou status {response.status_code}")
                    # Continuar para o fallback
                    
            except Exception as e:
                print(f"⚠️ [COTACAO] Erro ao consultar validador.php: {e}")
                # Continuar para o fallback
            
            # FALLBACK: Usar api/fallback_cotacao.py
            print("🟡 [COTACAO] Usando fallback_cotacao.py")
            try:
                cotacao_fallback = get_cotacao_fallback_simples("bitcoin", "brl")
                
                if cotacao_fallback and isinstance(cotacao_fallback, dict):
                    preco_btc = cotacao_fallback.get('price', 250000)
                    valor_recebe_sats = (valor_brl / preco_btc) * 100_000_000
                    
                    # Valores estimados para fallback
                    comissao_estimada = valor_brl * 0.025  # 2.5% estimado
                    taxa_parceiro_estimada = valor_brl * 0.01  # 1% estimado
                    valor_recebe_brl = valor_brl - comissao_estimada - taxa_parceiro_estimada
                    
                    return {
                        'success': True,
                        'data': {
                            'valor_investimento': valor_brl,
                            'cotacao': {
                                'preco_btc': preco_btc,
                                'fonte': cotacao_fallback.get('source', 'fallback'),
                                'data_atualizacao': cotacao_fallback.get('timestamp', '')
                            },
                            'comissao': {
                                'valor': comissao_estimada,
                                'percentual': 2.5
                            },
                            'parceiro': {
                                'valor': taxa_parceiro_estimada,
                                'percentual': 1.0
                            },
                            'limite': {
                                'maximo': 10000  # Limite padrão
                            },
                            'valor_recebe': {
                                'brl': valor_recebe_brl,
                                'sats': int(valor_recebe_sats)
                            },
                            'gtxid': 'FALLBACK_' + str(int(datetime.now().timestamp()))
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Fallback também falhou'
                    }
                    
            except Exception as e:
                print(f"❌ [COTACAO] Erro no fallback: {e}")
                return {
                    'success': False,
                    'error': f'Erro no fallback: {str(e)}'
                }
                
        except Exception as e:
            print(f"❌ [COTACAO] Erro geral: {e}")
            return {
                'success': False,
                'error': f'Erro geral: {str(e)}'
            }
            
except ImportError:
    async def obter_cotacao_fallback():
        return {
            'success': False,
            'error': 'Módulo fallback_cotacao não encontrado'
        }
    
    async def obter_cotacao_completa(valor_brl: float, user_id: int) -> Dict[str, Any]:
        """Fallback para cotação completa."""
        return {
            'success': False,
            'error': 'Módulo fallback_cotacao não encontrado'
        }

# Fallback para PedidoManager se o módulo não existir
try:
    from pedido_manager import PedidoManager  # type: ignore
except ImportError:
    class PedidoManager:
        def __init__(self):
            pass
        async def salvar_pedido_e_verificar(self, data):
            return {'success': False, 'error': 'PedidoManager não disponível'}
        async def atualizar_status_pedido(self, pedido_id, status, dados_extras=None):
            return {'success': False, 'error': 'PedidoManager não disponível'}

# Fallback para validador_voltz se o módulo não existir
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

# Inicializar o gerenciador de pedidos
try:
    pedido_manager: Any = PedidoManager()
except Exception as e:
    print(f"⚠️ [MENU] Erro ao inicializar PedidoManager: {e}")
    pedido_manager = None

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
        "🚀 *Bem-vindo ao Ghost P2P!*\n\nEscolha uma opção:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    print("🟢 [START] Retornando ESCOLHER_MOEDA")
    return ESCOLHER_MOEDA

async def escolher_moeda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para escolha de moeda."""
    print(f"🟡 [MOEDA] Handler escolher_moeda chamado")
    print(f"🟡 [MOEDA] Texto recebido: '{update.message.text if update and update.message else 'None'}'")
    
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
            "🪙 *Escolha a moeda:*\n\nQual moeda você deseja comprar?",
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
            "🌐 *Escolha a rede:*\n\nQual rede você deseja usar?",
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
            "💰 *Escolha o valor:*\n\n"
            "Digite um valor em reais (ex: 75.50) ou escolha uma opção:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        print("🟢 [REDE] Retornando ESCOLHER_VALOR após escolher Lightning")
        return ESCOLHER_VALOR
    
    # Se chegou aqui, texto inválido para este estado
    print(f"⚠️ [REDE] Texto não reconhecido: '{update.message.text}', retornando ESCOLHER_REDE")
    await update.message.reply_text(
        "❌ *Opção inválida!*\n\nPor favor, escolha uma das opções do menu.",
        parse_mode='Markdown'
    )
    return ESCOLHER_REDE

async def escolher_valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para escolha de valor."""
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
                    "❌ *Valor muito baixo!*\n\n"
                    "O valor mínimo para compra é R$ 10,00.\n"
                    "Digite um valor maior ou escolha uma opção:",
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
            "❌ *Valor inválido!*\n\n"
            "Digite um valor em reais (ex: 75.50) ou escolha uma opção:",
            parse_mode='Markdown'
        )
    return ESCOLHER_VALOR

async def processar_valor_personalizado(update: Update, context: ContextTypes.DEFAULT_TYPE, valor_brl: float) -> int:
    """Processa o valor escolhido (fixo ou personalizado) e mostra o resumo."""
    print(f"🟡 [MENU] Processando valor: R$ {valor_brl:.2f}")
    
    # Obter cotação completa
    try:
        if update.effective_user:
            user_id = update.effective_user.id
            cotacao_completa = await obter_cotacao_completa(valor_brl, user_id)
            
            if cotacao_completa and isinstance(cotacao_completa, dict) and cotacao_completa.get('success'):
                cotacao_data = cotacao_completa.get('data', {})
                if isinstance(cotacao_data, dict):
                    # Salvar dados completos no contexto
                    if context and context.user_data:
                        context.user_data['cotacao_completa'] = cotacao_data
                        context.user_data['valor_real'] = valor_brl
                    
                    # Extrair dados para o resumo
                    cotacao_info = cotacao_data.get('cotacao', {})
                    comissao_info = cotacao_data.get('comissao', {})
                    parceiro_info = cotacao_data.get('parceiro', {})
                    valor_recebe_info = cotacao_data.get('valor_recebe', {})
                    limite_info = cotacao_data.get('limite', {})
                    
                    if not isinstance(cotacao_info, dict):
                        cotacao_info = {}
                    if not isinstance(comissao_info, dict):
                        comissao_info = {}
                    if not isinstance(parceiro_info, dict):
                        parceiro_info = {}
                    if not isinstance(valor_recebe_info, dict):
                        valor_recebe_info = {}
                    if not isinstance(limite_info, dict):
                        limite_info = {}
                    
                    # Montar resumo detalhado
                    resumo_texto = (
                        f"📋 *Resumo da Compra:*\n\n"
                        f"🪙 *Moeda:* {escape_markdown(str(get_user_data(context, 'moeda', 'BTC'))) if context and context.user_data else 'BTC'}\n"
                        f"🌐 *Rede:* {escape_markdown(str(get_user_data(context, 'rede', 'Lightning').title())) if context and context.user_data else 'Lightning'}\n\n"
                        f"💰 *Valor do Investimento:* {escape_markdown(str(valor_brl))}\n"
                        f"💱 *Cotação BTC:* {escape_markdown(str(cotacao_info.get('preco_btc', 250000)))}\n"
                        f"📊 *Fonte:* {escape_markdown(str(cotacao_info.get('fonte', 'API')))}\n\n"
                        f"💸 *Comissão:* {escape_markdown(str(comissao_info.get('valor', 0)))} {escape_markdown(str(comissao_info.get('percentual', 0)))}%\n"
                        f"🤝 *Taxa Parceiro:* {escape_markdown(str(parceiro_info.get('valor', 0)))} {escape_markdown(str(parceiro_info.get('percentual', 0)))}%\n"
                        f"💰 *Limite Máximo:* {escape_markdown(str(limite_info.get('maximo', 0)))}\n\n"
                        f"⚡ *Você Recebe:* {escape_markdown(str(valor_recebe_info.get('sats', 0)))} sats\n"
                        f"💵 *Valor Líquido:* {escape_markdown(str(valor_recebe_info.get('brl', valor_brl)))}\n\n"
                        f"🆔 *ID Transação:* {escape_markdown(str(cotacao_data.get('gtxid', 'N/A')))}"
                    )
                    
                    keyboard = [["Confirmar"], ["Voltar"]]
                    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                    
                    if update and update.message:
                        await update.message.reply_text(
                            resumo_texto,
                            reply_markup=reply_markup,
                            parse_mode='MarkdownV2'
                        )
                    
                    return FORMA_PAGAMENTO
                else:
                    await mostrar_erro_cotacao(update, "Dados de cotação inválidos")
            else:
                error_msg = cotacao_completa.get('error', 'Erro desconhecido') if cotacao_completa and isinstance(cotacao_completa, dict) else 'Erro desconhecido'
                await mostrar_erro_cotacao(update, f"Erro na cotação: {error_msg}")
        else:
            await mostrar_erro_cotacao(update, "Usuário não encontrado")
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
        f"❌ *Erro:* {mensagem}\n\n"
        f"Escolha um valor ou digite um valor personalizado:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para mostrar resumo da compra."""
    if not update or not update.message:
        return ConversationHandler.END
    
    if update.message.text == "Voltar":
        return await escolher_valor(update, context)
    
    # Extrair valor escolhido
    texto_valor = update.message.text
    if not texto_valor or not isinstance(texto_valor, str):
        return ConversationHandler.END
    
    # Mapear texto para valor em sats
    mapeamento_valores = {
        "1.000 sats\n~R$ 2,50": 1000,
        "5.000 sats\n~R$ 12,50": 5000,
        "10.000 sats\n~R$ 25,00": 10000,
        "25.000 sats\n~R$ 62,50": 25000,
        "50.000 sats\n~R$ 125,00": 50000,
        "100.000 sats\n~R$ 250,00": 100000
    }
    
    valor_sats = mapeamento_valores.get(texto_valor, 0)
    if valor_sats == 0:
        return ConversationHandler.END
    
    if context and context.user_data:
        context.user_data['valor_sats'] = valor_sats
    
    print(f"🟢 [MENU] Usuário escolheu valor: {valor_sats} sats")
    
    # Calcular valores básicos
    cotacao = {}
    if context and context.user_data:
        cotacao = get_user_data(context, 'cotacao', {})
    
    if not isinstance(cotacao, dict):
        cotacao = {}
    
    preco_btc = cotacao.get('preco_btc', 250000)  # Fallback se não tiver cotação
    
    valor_btc = valor_sats / 100_000_000
    valor_real = valor_btc * preco_btc
    
    # Salvar valores calculados
    if context and context.user_data:
        context.user_data['valor_btc'] = valor_btc
        context.user_data['valor_real'] = valor_real
    
    # Obter cotação completa com comissão e parceiro
    try:
        if update.effective_user:
            user_id = update.effective_user.id
            cotacao_completa = await obter_cotacao_completa(valor_real, user_id)
            
            if cotacao_completa and isinstance(cotacao_completa, dict) and cotacao_completa.get('success'):
                cotacao_data = cotacao_completa.get('data', {})
                if isinstance(cotacao_data, dict):
                    # Salvar dados completos no contexto
                    if context and context.user_data:
                        context.user_data['cotacao_completa'] = cotacao_data
                    
                    # Extrair dados para o resumo
                    valor_investimento = cotacao_data.get('valor_investimento', valor_real)
                    cotacao_info = cotacao_data.get('cotacao', {})
                    comissao_info = cotacao_data.get('comissao', {})
                    parceiro_info = cotacao_data.get('parceiro', {})
                    valor_recebe_info = cotacao_data.get('valor_recebe', {})
                    limite_info = cotacao_data.get('limite', {})
                    
                    if not isinstance(cotacao_info, dict):
                        cotacao_info = {}
                    if not isinstance(comissao_info, dict):
                        comissao_info = {}
                    if not isinstance(parceiro_info, dict):
                        parceiro_info = {}
                    if not isinstance(valor_recebe_info, dict):
                        valor_recebe_info = {}
                    if not isinstance(limite_info, dict):
                        limite_info = {}
                    
                    # Montar resumo detalhado
                    resumo_texto = (
                        f"📋 **Resumo da Compra:**\n\n"
                        f"🪙 **Moeda:** {escape_markdown(str(get_user_data(context, 'moeda', 'BTC'))) if context and context.user_data else 'BTC'}\n"
                        f"🌐 **Rede:** {escape_markdown(str(get_user_data(context, 'rede', 'Lightning').title())) if context and context.user_data else 'Lightning'}\n"
                        f"💰 **Valor do Investimento:** R$ {escape_markdown(str(valor_investimento))}\n"
                        f"💱 **Cotação BTC:** R$ {escape_markdown(str(cotacao_info.get('preco_btc', preco_btc)))}\n"
                        f"📊 **Fonte:** {escape_markdown(str(cotacao_info.get('fonte', 'API')))}\n\n"
                        f"💸 **Comissão:** R$ {escape_markdown(str(comissao_info.get('valor', 0)))}\n"
                        f"🤝 **Taxa Parceiro:** R$ {escape_markdown(str(parceiro_info.get('valor', 0)))}\n"
                        f"💰 **Limite Máximo:** R$ {escape_markdown(str(limite_info.get('maximo', 0)))}\n\n"
                        f"⚡ **Você Recebe:** {escape_markdown(str(valor_recebe_info.get('sats', valor_sats)))}\n"
                        f"💵 **Valor Líquido:** R$ {escape_markdown(str(valor_recebe_info.get('brl', valor_real)))}\n\n"
                        f"🆔 **ID Transação:** {escape_markdown(str(cotacao_data.get('gtxid', 'N/A')))}"
                    )
                else:
                    # Fallback para resumo básico
                    resumo_texto = (
                        f"📋 **Resumo da Compra:**\n\n"
                        f"🪙 **Moeda:** {escape_markdown(str(get_user_data(context, 'moeda', 'BTC'))) if context and context.user_data else 'BTC'}\n"
                        f"🌐 **Rede:** {escape_markdown(str(get_user_data(context, 'rede', 'Lightning').title())) if context and context.user_data else 'Lightning'}\n"
                        f"💰 **Valor:** {escape_markdown(str(valor_sats))}\n"
                        f"💱 **Valor BTC:** {escape_markdown(str(valor_btc))}\n"
                        f"💵 **Valor R$:** R$ {escape_markdown(str(valor_real))}\n\n"
                        f"💱 **Cotação:** R$ {escape_markdown(str(preco_btc))}\n\n"
                        f"⚠️ **Cotação completa indisponível**"
                    )
            else:
                # Fallback para resumo básico
                resumo_texto = (
                    f"📋 **Resumo da Compra:**\n\n"
                    f"🪙 **Moeda:** {escape_markdown(str(get_user_data(context, 'moeda', 'BTC'))) if context and context.user_data else 'BTC'}\n"
                    f"🌐 **Rede:** {escape_markdown(str(get_user_data(context, 'rede', 'Lightning').title())) if context and context.user_data else 'Lightning'}\n"
                    f"💰 **Valor:** {escape_markdown(str(valor_sats))}\n"
                    f"💱 **Valor BTC:** {escape_markdown(str(valor_btc))}\n"
                    f"💵 **Valor R$:** R$ {escape_markdown(str(valor_real))}\n\n"
                    f"💱 **Cotação:** R$ {escape_markdown(str(preco_btc))}\n\n"
                    f"⚠️ **Cotação completa indisponível**"
                )
        else:
            # Fallback para resumo básico
            resumo_texto = (
                f"📋 **Resumo da Compra:**\n\n"
                f"🪙 **Moeda:** {escape_markdown(str(get_user_data(context, 'moeda', 'BTC'))) if context and context.user_data else 'BTC'}\n"
                f"🌐 **Rede:** {escape_markdown(str(get_user_data(context, 'rede', 'Lightning').title())) if context and context.user_data else 'Lightning'}\n"
                f"💰 **Valor:** {escape_markdown(str(valor_sats))}\n"
                f"💱 **Valor BTC:** {escape_markdown(str(valor_btc))}\n"
                f"💵 **Valor R$:** R$ {escape_markdown(str(valor_real))}\n\n"
                f"💱 **Cotação:** R$ {escape_markdown(str(preco_btc))}\n\n"
                f"⚠️ **Cotação completa indisponível**"
            )
    except Exception as e:
        print(f"❌ [MENU] Erro ao obter cotação completa: {e}")
        # Fallback para resumo básico
        resumo_texto = (
            f"📋 **Resumo da Compra:**\n\n"
            f"🪙 **Moeda:** {escape_markdown(str(get_user_data(context, 'moeda', 'BTC'))) if context and context.user_data else 'BTC'}\n"
            f"🌐 **Rede:** {escape_markdown(str(get_user_data(context, 'rede', 'Lightning').title())) if context and context.user_data else 'Lightning'}\n"
            f"💰 **Valor:** {escape_markdown(str(valor_sats))}\n"
            f"💱 **Valor BTC:** {escape_markdown(str(valor_btc))}\n"
            f"💵 **Valor R$:** R$ {escape_markdown(str(valor_real))}\n\n"
            f"💱 **Cotação:** R$ {escape_markdown(str(preco_btc))}\n\n"
            f"⚠️ **Erro na cotação completa**"
        )
    
    keyboard = [["Confirmar"], ["Voltar"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        resumo_texto,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return FORMA_PAGAMENTO

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
        "💳 *Forma de Pagamento:*\n\nEscolha como deseja pagar:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return CONFIRMAR

async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para confirmação final do pedido."""
    if not update or not update.message:
        return ConversationHandler.END
    
    if update.message.text == "Voltar":
        return await forma_pagamento(update, context)
    
    print("🟢 [MENU] Usuário escolheu PIX")
    
    # Mostrar resumo final para confirmação
    valor_sats = 0
    valor_real = 0
    if context and context.user_data:
        valor_sats = get_user_data(context, 'valor_sats', 0)
        valor_real = get_user_data(context, 'valor_real', 0)
    
    # Verificar se temos cotação completa
    cotacao_completa = {}
    if context and context.user_data:
        cotacao_completa = get_user_data(context, 'cotacao_completa', {})
    
    if cotacao_completa and isinstance(cotacao_completa, dict):
        # Usar resumo completo
        cotacao_info = cotacao_completa.get('cotacao', {})
        comissao_info = cotacao_completa.get('comissao', {})
        parceiro_info = cotacao_completa.get('parceiro', {})
        valor_recebe_info = cotacao_completa.get('valor_recebe', {})
        limite_info = cotacao_completa.get('limite', {})
        
        if not isinstance(cotacao_info, dict):
            cotacao_info = {}
        if not isinstance(comissao_info, dict):
            comissao_info = {}
        if not isinstance(parceiro_info, dict):
            parceiro_info = {}
        if not isinstance(valor_recebe_info, dict):
            valor_recebe_info = {}
        if not isinstance(limite_info, dict):
            limite_info = {}
        
        resumo_final = (
            f"🎯 **Confirmação Final:**\n\n"
            f"📋 **Resumo do Pedido:**\n"
            f"• Moeda: {escape_markdown(str(get_user_data(context, 'moeda', 'BTC'))) if context and context.user_data else 'BTC'}\n"
            f"• Rede: {escape_markdown(str(get_user_data(context, 'rede', 'Lightning').title())) if context and context.user_data else 'Lightning'}\n"
            f"• Valor Investimento: R$ {escape_markdown(str(cotacao_completa.get('valor_investimento', valor_real)))}\n"
            f"• Cotação BTC: R$ {escape_markdown(str(cotacao_info.get('preco_btc', 250000)))}\n"
            f"• Comissão: R$ {escape_markdown(str(comissao_info.get('valor', 0)))}\n"
            f"• Taxa Parceiro: R$ {escape_markdown(str(parceiro_info.get('valor', 0)))}\n"
            f"• Limite Máximo: R$ {escape_markdown(str(limite_info.get('maximo', 0)))}\n"
            f"• Você Recebe: {escape_markdown(str(valor_recebe_info.get('sats', valor_sats)))}\n"
            f"• Valor Líquido: R$ {escape_markdown(str(valor_recebe_info.get('brl', valor_real)))}\n"
            f"• Pagamento: PIX\n"
            f"• ID: `{escape_markdown(str(cotacao_completa.get('gtxid', 'N/A')))}`\n\n"
            f"⚠️ **Atenção:** Após confirmar, você receberá o QR Code PIX para pagamento."
        )
    else:
        # Resumo básico
        resumo_final = (
            f"🎯 **Confirmação Final:**\n\n"
            f"📋 **Resumo do Pedido:**\n"
            f"• Moeda: {escape_markdown(str(get_user_data(context, 'moeda', 'BTC'))) if context and context.user_data else 'BTC'}\n"
            f"• Rede: {escape_markdown(str(get_user_data(context, 'rede', 'Lightning').title())) if context and context.user_data else 'Lightning'}\n"
            f"• Valor: {escape_markdown(str(valor_sats))}\n"
            f"• Valor: R$ {escape_markdown(str(valor_real))}\n"
            f"• Pagamento: PIX\n\n"
            f"⚠️ **Atenção:** Após confirmar, você receberá o QR Code PIX para pagamento."
        )
    
    keyboard = [["Confirmar Pedido"], ["Cancelar"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        resumo_final,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return PAGAMENTO

async def pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para criação do pagamento PIX."""
    if not update or not update.message:
        return ConversationHandler.END
    
    if update.message.text == "Cancelar":
        return await start(update, context)
    
    print("🟢 [MENU] Usuário confirmou pedido - criando PIX")
    
    # Salvar pedido no banco e iniciar verificação
    try:
        if not update.effective_user:
            await update.message.reply_text(
                "❌ **Erro:** Usuário não encontrado.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        user_id = update.effective_user.id
        username = update.effective_user.username or "sem_username"
        
        # Dados do pedido
        cotacao_completa = {}
        if context and context.user_data:
            cotacao_completa = get_user_data(context, 'cotacao_completa', {})
        
        pedido_data = {
            'user_id': user_id,
            'username': username,
            'moeda': get_user_data(context, 'moeda', 'BTC') if context and context.user_data else 'BTC',
            'rede': get_user_data(context, 'rede', 'lightning') if context and context.user_data else 'lightning',
            'valor_sats': get_user_data(context, 'valor_sats', 0) if context and context.user_data else 0,
            'valor_btc': get_user_data(context, 'valor_btc', 0) if context and context.user_data else 0,
            'valor_real': get_user_data(context, 'valor_real', 0) if context and context.user_data else 0,
            'cotacao': get_user_data(context, 'cotacao', {}) if context and context.user_data else {},
            'cotacao_completa': cotacao_completa,
            'status': 'aguardando_pagamento'
        }
        
        print(f"🟡 [MENU] Salvando pedido no banco: {pedido_data}")
        
        # Salvar pedido e iniciar verificação
        if pedido_manager:
            resultado = await pedido_manager.salvar_pedido_e_verificar(pedido_data)
        else:
            resultado = {'success': False, 'error': 'PedidoManager não disponível'}
        
        if resultado and isinstance(resultado, dict) and resultado.get('success'):
            pedido_id = resultado.get('pedido_id', 0)
            if context and context.user_data:
                context.user_data['pedido_id'] = pedido_id
            
            print(f"✅ [MENU] Pedido salvo com ID: {pedido_id}")
            
            # Criar pagamento PIX
            try:
                import requests
                
                pix_data = {
                    'valor': get_user_data(context, 'valor_real', 0) if context and context.user_data else 0,
                    'endereco': 'bouncyflight79@walletofsatoshi.com',
                    'descricao': f'Compra {get_user_data(context, 'valor_sats', 0) if context and context.user_data else 0:,} sats - Pedido #{pedido_id}'
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/bot_deposit.php",
                    json=pix_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    pix_response = response.json()
                    
                    if pix_response and isinstance(pix_response, dict) and pix_response.get('success'):
                        # Mostrar QR Code
                        pix_data_dict = pix_response.get('data', {})
                        if not isinstance(pix_data_dict, dict):
                            pix_data_dict = {}
                        
                        qr_code_url = pix_data_dict.get('qr_code', '')
                        copia_cola = pix_data_dict.get('copia_cola', '')
                        
                        # Primeira mensagem com QR Code
                        await update.message.reply_text(
                            f"💳 **Pagamento PIX Criado!**\n\n"
                            f"📋 **Pedido #{pedido_id}**\n"
                            f"💰 **Valor:** R$ {escape_markdown(str(get_user_data(context, 'valor_real', 0)))}\n"
                            f"⚡ **Valor:** {escape_markdown(str(get_user_data(context, 'valor_sats', 0)))}\n\n"
                            f"📱 **QR Code:**",
                            parse_mode='Markdown'
                        )
                        
                        # Enviar QR Code como imagem
                        if context and context.bot and update.effective_chat:
                            await context.bot.send_photo(
                                chat_id=update.effective_chat.id,
                                photo=qr_code_url,
                                caption="📱 Escaneie o QR Code para pagar"
                            )
                            
                            # Segunda mensagem com copia e cola
                            await context.bot.send_message(
                                chat_id=update.effective_chat.id,
                                text=f"📋 **Copia e Cola:**\n`{copia_cola}`\n\n"
                                     f"💡 **Instruções:**\n"
                                     f"1. Copie o código acima\n"
                                     f"2. Abra seu app bancário\n"
                                     f"3. Cole no PIX\n"
                                     f"4. Confirme o pagamento\n\n"
                                     f"⏰ **Tempo limite:** 30 minutos\n\n"
                                     f"🔄 **Verificação automática ativada!**\n"
                                     f"O sistema verificará o pagamento automaticamente.",
                                parse_mode='Markdown'
                            )
                            
                            # Botão de suporte
                            keyboard = [
                                ["🆘 Suporte"]
                            ]
                            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                            
                            await context.bot.send_message(
                                chat_id=update.effective_chat.id,
                                text="❓ **Precisa de ajuda?**\nClique no botão abaixo:",
                                reply_markup=reply_markup,
                                parse_mode='Markdown'
                            )
                        
                        print(f"✅ [MENU] PIX criado com sucesso para pedido #{pedido_id}")
                        
                    else:
                        error_msg = pix_response.get('error', 'Erro desconhecido') if pix_response and isinstance(pix_response, dict) else 'Erro desconhecido'
                        await update.message.reply_text(
                            f"❌ **Erro ao criar PIX:**\n{error_msg}\n\n"
                            f"Tente novamente ou entre em contato com o suporte.",
                            parse_mode='Markdown'
                        )
                else:
                    await update.message.reply_text(
                        f"❌ **Erro na API:** Status {response.status_code}\n\n"
                        f"Tente novamente ou entre em contato com o suporte.",
                        parse_mode='Markdown'
                    )
                    
            except Exception as e:
                print(f"❌ [MENU] Erro ao criar PIX: {e}")
                await update.message.reply_text(
                    f"❌ **Erro ao criar PIX:**\n{str(e)}\n\n"
                    f"Tente novamente ou entre em contato com o suporte.",
                    parse_mode='Markdown'
                )
        else:
            error_msg = resultado.get('error', 'Erro desconhecido') if resultado and isinstance(resultado, dict) else 'Erro desconhecido'
            print(f"❌ [MENU] Erro ao salvar pedido: {error_msg}")
            await update.message.reply_text(
                f"❌ **Erro ao salvar pedido:**\n{error_msg}\n\n"
                f"Tente novamente ou entre em contato com o suporte.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        print(f"❌ [MENU] Erro geral no pagamento: {e}")
        await update.message.reply_text(
            f"❌ **Erro inesperado:**\n{str(e)}\n\n"
            f"Tente novamente ou entre em contato com o suporte.",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

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
            "❌ **Endereço Lightning inválido!**\n\n"
            "Por favor, envie um endereço Lightning válido:\n"
            "• Lightning Address (ex: user@domain.com)\n"
            "• Invoice Lightning (ex: lnbc...)\n\n"
            "Tente novamente:",
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
            "❌ **Erro:** Dados do pedido não encontrados.\n"
            "Por favor, inicie uma nova compra.",
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
                f"❌ **Erro ao consultar saldo:**\n{error_msg}\n\n"
                f"Entre em contato com o suporte.",
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
                f"❌ **Saldo insuficiente!**\n\n"
                f"💰 Saldo atual: {saldo_atual:,} sats\n"
                f"💸 Valor necessário: {valor_sats:,} sats\n"
                f"📉 Diferença: {valor_sats - saldo_atual:,} sats\n\n"
                f"Entre em contato com o suporte.",
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
                    await pedido_manager.atualizar_status_pedido(
                        pedido_id, 
                        'pagamento_enviado',
                        {
                            'lightning_address': endereco_lightning,
                            'payment_hash': payment_hash,
                            'fee': fee,
                            'enviado_em': datetime.now().isoformat()
                        }
                    )
                    print(f"✅ [LIGHTNING] Status do pedido #{pedido_id} atualizado")
            except Exception as e:
                print(f"⚠️ [LIGHTNING] Erro ao atualizar status: {e}")
            
            # Mensagem de sucesso
            await update.message.reply_text(
                f"✅ **Pagamento Enviado com Sucesso!**\n\n"
                f"📋 **Pedido #{pedido_id}**\n"
                f"💰 **Valor:** {escape_markdown(str(valor_sats))}\n"
                f"⚡ **Para:** {escape_markdown(str(endereco_lightning))}\n"
                f"🔗 **Hash:** `{escape_markdown(str(payment_hash))}`\n"
                f"💸 **Taxa:** {escape_markdown(str(fee))} sats\n\n"
                f"🎉 **Seus satoshis foram enviados!**\n\n"
                f"📱 **Próximos passos:**\n"
                f"1. Verifique seu app Lightning\n"
                f"2. Confirme o recebimento\n"
                f"3. Em caso de dúvidas, contate o suporte",
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
                    text="❓ **Precisa de ajuda?**\nClique no botão abaixo:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            
        else:
            error_msg = pagamento_result.get('error', 'Erro desconhecido') if pagamento_result and isinstance(pagamento_result, dict) else 'Erro desconhecido'
            await update.message.reply_text(
                f"❌ **Erro ao enviar pagamento:**\n{error_msg}\n\n"
                f"Entre em contato com o suporte.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        print(f"❌ [LIGHTNING] Erro ao processar pagamento: {e}")
        await update.message.reply_text(
            f"❌ **Erro inesperado:**\n{str(e)}\n\n"
            f"Entre em contato com o suporte.",
            parse_mode='Markdown'
        )
    
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para cancelar a operação."""
    if update and update.message:
        await update.message.reply_text(
            "❌ **Operação cancelada.**\n\n"
            "Use /start para iniciar uma nova compra.",
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
            FORMA_PAGAMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, forma_pagamento)],
            CONFIRMAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar)],
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
                text="🎉 **Pagamento PIX Confirmado!**\n\n"
                     "✅ Seu pagamento foi recebido e confirmado!\n\n"
                     "⚡ **Agora envie seu endereço Lightning:**\n\n"
                     "📱 **Formatos aceitos:**\n"
                     "• Lightning Address: `user@domain.com`\n"
                     "• Invoice Lightning: `lnbc...`\n\n"
                     "💡 **Exemplo:** `sua_carteira@walletofsatoshi.com`\n\n"
                     "Envie seu endereço agora:",
                parse_mode='Markdown'
            )
            
            print(f"✅ [LIGHTNING] Mensagem enviada para usuário {user_id}")
        
    except Exception as e:
        print(f"❌ [LIGHTNING] Erro ao ativar aguardar endereço: {e}")

# Exportar a função para ser usada pelo pedido_manager
__all__ = ['get_conversation_handler', 'ativar_aguardar_lightning_address']
