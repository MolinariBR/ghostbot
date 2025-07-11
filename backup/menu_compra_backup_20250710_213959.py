# ATENÇÃO: Execute sempre o projeto via 'python -m ghost.bot' na raiz do projeto para que imports funcionem corretamente.
# Não execute diretamente este arquivo.

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, ConversationHandler, CommandHandler, filters
from telegram.ext import ContextTypes
import requests
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Any, Optional
import os
import re
import traceback
import aiohttp

# 🎯 SISTEMA DE CAPTURA - IMPORT
try:
    from captura.capture_system import capture_system
    CAPTURE_ENABLED = True
    print("✅ Sistema de captura importado com sucesso no menu_compra.py")
except Exception as e:
    print(f"⚠️ Sistema de captura não disponível no menu_compra.py: {e}")
    CAPTURE_ENABLED = False
    capture_system = None

# Imports do sistema Ghost
from api.voltz import VoltzAPI

# 🚀 NOVA INTEGRAÇÃO: Smart PIX Monitor (substitui cron externo)
from trigger.smart_pix_monitor import register_pix_payment

# 🚀 NOVA INTEGRAÇÃO: Sistema de Limites de Valor
from limites.limite_valor import LimitesValor
from limites.gerenciador_usuario import validar_compra_usuario, registrar_compra_usuario
from limites.redirecionamentos import redirecionar_para_ted_boleto

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
(SOLICITAR_CPF, ESCOLHER_MOEDA, ESCOLHER_REDE, QUANTIDADE, RESUMO_COMPRA, CONFIRMAR_COMPRA,
 SOLICITAR_ENDERECO, ESCOLHER_PAGAMENTO, AGUARDAR_TED_COMPROVANTE) = range(9)

# Constantes para métodos de pagamento
PIX = "💠 PIX"
TED = "🏦 TED"
BOLETO = "📄 Boleto"

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

async def iniciar_compra(update: Update, context) -> int:
    """Inicia o fluxo de compra mostrando as moedas disponíveis."""
    
    # 🎯 CAPTURA: Início da compra
    user = update.effective_user
    chatid = str(user.id)
    username = user.username or user.first_name or "Unknown"
    
    # Iniciar sessão de captura
    capture_user_session(chatid, username)
    capture_step(chatid, "INICIAR_COMPRA", {
        "user_id": user.id,
        "username": username,
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        # Envia dados do usuário para o backend PHP
        try:
            payload = {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
            url = "https://useghost.squareweb.app/api/user_api.php"
            headers = {"Content-Type": "application/json"}
            requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
            
            # 🎯 CAPTURA: Dados enviados ao backend
            capture_step(chatid, "BACKEND_USER_DATA", {
                "success": True,
                "url": url
            })
            
        except Exception as e:
            logger.warning(f"Não foi possível enviar dados do usuário ao backend: {e}")
            capture_error(chatid, f"Backend user data failed: {e}", "iniciar_compra")
        
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
        
        # 🎯 CAPTURA: Menu de moedas exibido
        capture_step(chatid, "MENU_MOEDAS_EXIBIDO", {
            "opcoes_moedas": [row[0].text if hasattr(row[0], 'text') else str(row[0]) for row in opcoes_moedas],
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Erro ao exibir opções de moedas: {str(e)}")
        capture_error(chatid, f"Erro ao exibir moedas: {e}", "iniciar_compra")
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

async def escolher_moeda(update: Update, context) -> int:
    """Processa a escolha da moeda e pede para selecionar a rede."""
    
    # 🎯 CAPTURA: Escolha da moeda
    chatid = str(update.effective_user.id)
    choice = update.message.text
    
    capture_step(chatid, "ESCOLHER_MOEDA", {
        "choice": choice,
        "timestamp": datetime.now().isoformat()
    })
    
    if update.message.text == "🔙 Voltar":
        capture_step(chatid, "VOLTAR_MENU_PRINCIPAL", {"from": "escolher_moeda"})
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
            capture_error(chatid, f"Erro menu principal: {e}", "escolher_moeda")
            try:
                await update.message.reply_text(
                    "Operação cancelada.",
                    parse_mode='Markdown'
                )
            except Exception as e2:
                logger.error(f"Falha ao enviar mensagem de cancelamento: {str(e2)}")
                capture_error(chatid, f"Falha cancelamento: {e2}", "escolher_moeda")
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

async def escolher_rede(update: Update, context) -> int:
    """Processa a escolha da rede e pede o valor em BRL."""
    
    # 🎯 CAPTURA: Escolha da rede
    chatid = str(update.effective_user.id)
    choice = update.message.text
    
    capture_step(chatid, "ESCOLHER_REDE", {
        "choice": choice,
        "timestamp": datetime.now().isoformat()
    })
    
    if update.message.text == "🔙 Voltar":
        capture_step(chatid, "VOLTAR_ESCOLHA_MOEDA", {"from": "escolher_rede"})
        return await iniciar_compra(update, context)
    
    try:
        rede = update.message.text
        context.user_data['rede'] = rede
        
        # Obtém a moeda selecionada
        moeda = context.user_data.get('moeda', 'a moeda selecionada')
        
        # 🎯 CAPTURA: Rede selecionada
        capture_step(chatid, "REDE_SELECIONADA", {
            "rede": rede,
            "moeda": moeda,
            "timestamp": datetime.now().isoformat()
        })
        
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
        
        # 🎯 CAPTURA: Menu de valores exibido
        capture_step(chatid, "MENU_VALORES_EXIBIDO", {
            "min_valor": min_valor,
            "max_valor": max_valor,
            "valores_sugeridos": [opt for row in teclado for opt in row],
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar escolha de rede: {str(e)}")
        capture_error(chatid, f"Erro escolha rede: {e}", "escolher_rede")
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
            capture_error(chatid, f"Falha ao enviar erro: {e2}", "escolher_rede")
            return ConversationHandler.END
    
    return QUANTIDADE

async def processar_quantidade(update: Update, context) -> int:
    """Processa a quantidade informada, aplica limites progressivos e solicita CPF se necessário."""
    
    # 🎯 CAPTURA: Processar quantidade
    chatid = str(update.effective_user.id)
    valor_str = update.message.text.replace('R$', '').replace(',', '.').strip()
    
    capture_step(chatid, "PROCESSAR_QUANTIDADE", {
        "valor_str": valor_str,
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        valor = float(re.sub(r'[^0-9.]', '', valor_str))
        
        # 🎯 CAPTURA: Valor convertido
        capture_step(chatid, "VALOR_CONVERTIDO", {
            "valor": valor,
            "valor_original": valor_str
        })
        
        # Obtém CPF se já foi fornecido anteriormente
        cpf = context.user_data.get('cpf')
        
        # 🚀 NOVA INTEGRAÇÃO: Validação com sistema de usuário
        chatid = str(update.effective_user.id)
        validacao = validar_compra_usuario(chatid, valor, cpf)
        
        # 🎯 CAPTURA: Validação de limite
        capture_step(chatid, "VALIDACAO_LIMITE", {
            "valido": validacao['valido'],
            "erro": validacao.get('erro'),
            "limite_atual": validacao.get('limite_atual'),
            "precisa_cpf": validacao.get('precisa_cpf', False)
        })
        
        if not validacao['valido']:
            capture_step(chatid, "LIMITE_EXCEDIDO", validacao)
            if validacao['erro'] == 'LIMITE_DIARIO':
                # Mensagem específica para limite diário
                mensagem = f"❌ {validacao['mensagem']}\n\n"
                mensagem += f"💡 {validacao['dica']}\n\n"
                
                if validacao['primeira_compra']:
                    mensagem += "🎯 *Primeira compra*\n"
                    mensagem += "• Limite: R$ 500,00\n"
                    mensagem += "• Para valores maiores, forneça seu CPF\n\n"
                else:
                    mensagem += f"� *Compras realizadas*: {validacao['num_compras']}\n"
                    mensagem += f"🎯 *Limite atual*: R$ {validacao['limite_atual']:.2f}\n\n"
                
                if validacao['precisa_cpf']:
                    mensagem += "🔒 *Para aumentar o limite*:\n"
                    mensagem += "• Forneça seu CPF válido\n"
                    mensagem += "• Limite será liberado para R$ 4.999,99\n\n"
                
                mensagem += "💵 *Digite o valor desejado* (ex: 150,50):"
                
                await update.message.reply_text(
                    mensagem,
                    parse_mode='Markdown'
                )
            else:
                # Mensagem para outros erros (PIX, etc.)
                await update.message.reply_text(
                    f"❌ {validacao['mensagem']}\n\n"
                    f"💡 {validacao['dica']}\n\n"
                    "💵 *Digite o valor desejado* (ex: 150,50):",
                    parse_mode='Markdown'
                )
            return QUANTIDADE
        
        context.user_data['valor_brl'] = valor
        context.user_data['validacao_limite'] = validacao
        
        # 🎯 CAPTURA: Dados salvos
        capture_step(chatid, "DADOS_SALVOS", {
            "valor_brl": valor,
            "precisa_cpf": validacao.get('precisa_cpf', False)
        })
        
        # Se valor está acima do limite e ainda não tem CPF, solicita CPF
        if validacao.get('precisa_cpf', False) and not cpf:
            context.user_data['solicitar_cpf'] = True
            await update.message.reply_text(
                f"🔒 Para compras acima do seu limite atual, é necessário informar o CPF.\n\n"
                f"💡 Seu limite atual: R$ {validacao['limite_atual']:.2f}\n"
                f"💡 Com CPF: R$ 4.999,99\n\n"
                "Por favor, digite seu CPF (apenas números):"
            )
            return SOLICITAR_CPF
        else:
            context.user_data['cpf'] = cpf
            return await resumo_compra(update, context)
    except ValueError:
        capture_error(chatid, f"Erro conversão valor: {valor_str}", "processar_quantidade")
        # Trata erro de conversão de valor
        await update.message.reply_text(
            "❌ Formato de valor inválido. Por favor, digite um valor numérico válido (ex: 150,50).\n\n"
            "💵 *Digite o valor desejado* (ex: 150,50) ou use os valores sugeridos abaixo:",
            parse_mode='Markdown'
        )
        return QUANTIDADE
    except Exception as e:
        capture_error(chatid, f"Erro processar quantidade: {e}", "processar_quantidade")
        logger.error(f"Erro ao processar quantidade e aplicar limites: {e}")
        await update.message.reply_text(
            "❌ Erro ao processar o valor informado. Por favor, tente novamente ou digite um valor válido."
        )
        return QUANTIDADE

async def solicitar_cpf(update: Update, context) -> int:
    """Recebe o CPF do usuário, valida e segue para o resumo da compra."""
    cpf = re.sub(r'[^0-9]', '', update.message.text)
    if len(cpf) != 11:
        await update.message.reply_text("CPF inválido. Por favor, digite um CPF válido (11 dígitos, apenas números):")
        return SOLICITAR_CPF
    context.user_data['cpf'] = cpf
    return await resumo_compra(update, context)

async def resumo_compra(update: Update, context) -> int:
    """Mostra o resumo da compra antes da confirmação."""
    
    # 🎯 CAPTURA: Início do resumo da compra
    chatid = str(update.effective_user.id)
    capture_step(chatid, "RESUMO_COMPRA", {
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        moeda = context.user_data.get('moeda', 'a moeda selecionada')
        rede = context.user_data.get('rede', 'a rede selecionada')
        valor_brl = context.user_data.get('valor_brl', 0)
        
        # 🎯 CAPTURA: Dados do resumo
        capture_step(chatid, "DADOS_RESUMO", {
            "moeda": moeda,
            "rede": rede,
            "valor_brl": valor_brl
        })
        
        # Obtém a cotação
        cotacao = await obter_cotacao(moeda)
        
        # 🚀 NOVA INTEGRAÇÃO: Sistema de Comissões
        from limites.comissao import calcular_comissao, calcular_comissao_fallback
        
        # Extrai a sigla da moeda do texto do menu
        moeda_calc = moeda
        if "BTC" in moeda.upper():
            moeda_calc = "BTC"
        elif "USDT" in moeda.upper():
            moeda_calc = "USDT"
        elif "DEPIX" in moeda.upper():
            moeda_calc = "DEPIX"
        
        # Calcula a comissão baseada na moeda e valor
        resultado_comissao = calcular_comissao(valor_brl, moeda_calc)
        
        if resultado_comissao and resultado_comissao.get('comissao', {}).get('total') is not None:
            # Usa os valores calculados pelo sistema de comissões
            comissao_total = resultado_comissao['comissao']['total']
            valor_liquido = resultado_comissao['valor_liquido']
            valor_recebido = valor_liquido / cotacao
            
            # Informações da comissão
            comissao_info = resultado_comissao['comissao']
            percentual = comissao_info['percentual']
            taxa_fixa = comissao_info['fixo']
            
            logger.info(f"Comissão calculada via API: {percentual}% para {moeda_calc}, valor R$ {valor_brl:.2f}")
        else:
            # Fallback robusto baseado nas regras de negócio
            logger.warning(f"Sistema de comissões falhou para {moeda} valor R$ {valor_brl}, usando fallback robusto")
            
            resultado_fallback = calcular_comissao_fallback(valor_brl, moeda_calc)
            
            comissao_total = resultado_fallback['comissao']['total']
            valor_liquido = resultado_fallback['valor_liquido']
            valor_recebido = valor_liquido / cotacao
            percentual = resultado_fallback['comissao']['percentual']
            taxa_fixa = resultado_fallback['comissao']['fixo']
            
            logger.info(f"Fallback aplicado: {percentual}% para {moeda_calc}, valor R$ {valor_brl:.2f}, comissão R$ {comissao_total:.2f}")
        
        # Formata os valores
        valor_brl_formatado = formatar_brl(valor_brl)
        valor_recebido_formatado = formatar_cripto(valor_recebido, moeda)
        comissao_formatada = formatar_brl(comissao_total)
        cotacao_formatada = formatar_brl(cotacao)
        
        # 💡 NOVA FUNCIONALIDADE: Verifica se método de pagamento já foi escolhido
        metodo_pagamento = context.user_data.get('metodo_pagamento', '')
        
        # Mapeia métodos de pagamento para taxa do parceiro
        mapeamento_taxas = {
            'PIX': 1.00,
            '💠 PIX': 1.00,
            'DEPIX': 1.00,
            'TED': 0.00,  # Será redirecionado
            'Boleto': 0.00,  # Será redirecionado
            'Lightning': 0.00  # Sem taxa adicional
        }
        
        # Determina a taxa do parceiro
        if metodo_pagamento in mapeamento_taxas:
            taxa_parceiro = mapeamento_taxas[metodo_pagamento]
            taxa_parceiro_info = f"R$ {taxa_parceiro:.2f}"
        else:
            # Método não escolhido ainda - mostra informação transparente
            taxa_parceiro_info = "R$ 1,00 (para PIX)"
        
        # Cria o teclado de confirmação
        teclado_confirmacao = [
            ["✅ Confirmar Compra"],
            ["✏️ Alterar Valor", "🔙 Mudar Moeda"]
        ]
        reply_markup = ReplyKeyboardMarkup(teclado_confirmacao, resize_keyboard=True)
        
        # 📋 NOVO RESUMO DETALHADO DA COMPRA
        mensagem = (
            f"📋 *RESUMO DA COMPRA*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"• *Moeda:* {moeda}\n"
            f"• *Rede:* {rede}\n"
            f"• *Valor Investido:* {valor_brl_formatado}\n"
            f"• *Parceiro:* {taxa_parceiro_info}\n"
            f"• *Comissão:* {percentual:.1f}% + R$ {taxa_fixa:.2f} = {comissao_formatada}\n"
            f"• *Cotação:* {cotacao_formatada}\n"
            f"• *Você receberá:* {valor_recebido_formatado}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        # Adiciona nota explicativa se método não foi escolhido
        if not metodo_pagamento or metodo_pagamento not in mapeamento_taxas:
            mensagem += (
                "ℹ️ *Nota:* A taxa do parceiro (R$ 1,00 para PIX) será "
                "exibida após a escolha do método de pagamento.\n\n"
            )
        
        mensagem += "Confirma os dados da compra?"
        
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
        
    except Exception as e:
        # 🎯 CAPTURA: Erro no resumo da compra
        capture_error(chatid, f"Erro no resumo da compra: {str(e)}", "resumo_compra")
        logger.error(f"Erro no resumo da compra: {e}")
        await update.message.reply_text(
            "❌ *Erro ao processar resumo da compra*\n\n"
            "Tente novamente ou volte ao menu principal.",
            parse_mode='Markdown'
        )
        return ESCOLHER_REDE
        
    return RESUMO_COMPRA

async def confirmar_compra(update: Update, context) -> int:
    """Confirma os dados e verifica se precisa solicitar endereço ou vai direto para pagamento."""
    
    if update.message.text == "🔙 Mudar Moeda":
        # Volta para a escolha de moeda
        try:
            opcoes_moedas = menu_moedas()
            reply_markup = ReplyKeyboardMarkup(opcoes_moedas, resize_keyboard=True)
            await update.message.reply_text(
                "💱 *ESCOLHA A MOEDA PARA COMPRA*\n\n"
                "Selecione a criptomoeda que deseja comprar:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Erro ao exibir moedas: {str(e)}")
        return ESCOLHER_MOEDA
    
    elif update.message.text == "✏️ Alterar Valor":
        # Volta para digitar o valor
        try:
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
            reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
            await update.message.reply_text(
                "💵 *Qual valor deseja investir?*\n\n"
                "Escolha uma das opções ou digite um valor personalizado:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Erro ao exibir valores: {str(e)}")
        return QUANTIDADE
    
    elif update.message.text == "✅ Confirmar Compra":
        # Verifica se é Lightning (não precisa de endereço)
        rede = context.user_data.get('rede', '').lower()
        
        if 'lightning' in rede:
            # Lightning: vai direto para escolha de pagamento
            context.user_data['endereco_recebimento'] = 'voltzapi@tria.com'
            return await mostrar_metodos_pagamento(update, context)
        else:
            # Outras redes: precisa do endereço primeiro
            return await solicitar_endereco(update, context)
    
    # Se chegou aqui, volta para quantidade
    return await processar_quantidade(update, context)

async def solicitar_endereco(update: Update, context) -> int:
    """Solicita o endereço de recebimento para redes que não são Lightning."""
    try:
        moeda = context.user_data.get('moeda', '')
        rede = context.user_data.get('rede', '')
        
        # Mensagem específica por tipo de endereço
        if 'btc' in moeda.lower():
            if 'onchain' in rede.lower() or 'on-chain' in rede.lower():
                exemplo_endereco = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
                tipo_endereco = "Bitcoin On-chain"
            elif 'liquid' in rede.lower():
                exemplo_endereco = "VJLCpK7W1T6qydyj7V5wLtJxV8K1TdGnJ2"
                tipo_endereco = "Bitcoin Liquid"
            else:
                exemplo_endereco = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
                tipo_endereco = "Bitcoin"
        elif 'usdt' in moeda.lower():
            exemplo_endereco = "VJLCpK7W1T6qydyj7V5wLtJxV8K1TdGnJ2"
            tipo_endereco = "USDT Liquid"
        elif 'depix' in moeda.lower():
            exemplo_endereco = "VJLCpK7W1T6qydyj7V5wLtJxV8K1TdGnJ2"
            tipo_endereco = "Depix Liquid"
        else:
            exemplo_endereco = "Endereço da carteira"
            tipo_endereco = "Cripto"
        
        teclado_voltar = [["🔙 Voltar"]]
        reply_markup = ReplyKeyboardMarkup(teclado_voltar, resize_keyboard=True)
        
        mensagem = f"""📬 *ENDEREÇO DE RECEBIMENTO*

🎯 *Tipo:* {tipo_endereco}
📍 *Rede:* {rede}

Por favor, informe o endereço onde deseja receber suas criptomoedas:

💡 *Exemplo:*
`{exemplo_endereco}`

⚠️ *IMPORTANTE:* Verifique se o endereço está correto. Envios para endereços errados não podem ser revertidos."""
        
        await update.message.reply_text(
            mensagem,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Erro ao solicitar endereço: {str(e)}")
        await update.message.reply_text(
            "📬 Informe o endereço de recebimento:\n\nDigite 'voltar' para retornar.",
            parse_mode='Markdown'
        )
    
    return SOLICITAR_ENDERECO

async def processar_endereco(update: Update, context) -> int:
    """Processa o endereço informado e vai para escolha de pagamento."""
    if update.message.text == "🔙 Voltar":
        return await confirmar_compra(update, context)

    endereco = update.message.text.strip()
    
    # Validação básica do endereço
    if len(endereco) < 20:
        await update.message.reply_text(
            "❌ *Endereço muito curto*\n\n"
            "Por favor, verifique se o endereço está completo e tente novamente.",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([["🔙 Voltar"]], resize_keyboard=True)
        )
        return SOLICITAR_ENDERECO
    
    context.user_data['endereco_recebimento'] = endereco
    
    # Confirma o endereço e vai para pagamento
    await update.message.reply_text(
        f"✅ *Endereço confirmado!*\n\n"
        f"📍 `{endereco}`\n\n"
        "Prosseguindo para escolha do método de pagamento...",
        parse_mode='Markdown'
    )
    
    return await mostrar_metodos_pagamento(update, context)

async def mostrar_metodos_pagamento(update: Update, context) -> int:
    """Mostra as opções de métodos de pagamento."""
    try:
        opcoes_pagamento = menu_metodos_pagamento()
        reply_markup = ReplyKeyboardMarkup(opcoes_pagamento, resize_keyboard=True)
        
        await update.message.reply_text(
            "💳 *ESCOLHA A FORMA DE PAGAMENTO*\n\n"
            "Selecione como deseja efetuar o pagamento:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Erro ao mostrar métodos de pagamento: {str(e)}")
        await update.message.reply_text(
            "❌ Erro ao carregar métodos de pagamento. Tente novamente.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Voltar"]], resize_keyboard=True)
        )
        return SOLICITAR_ENDERECO if 'endereco_recebimento' not in context.user_data else ESCOLHER_PAGAMENTO
    
    return ESCOLHER_PAGAMENTO

def menu_metodos_pagamento():
    """Retorna as opções de métodos de pagamento como uma lista de listas de strings."""
    return [
        ["💠 PIX"],
        ["🏦 TED"],
        ["📄 Boleto"],
        ["🔙 Voltar"]
    ]
    
async def processar_metodo_pagamento(update: Update, context) -> int:
    """Processa o método de pagamento escolhido."""
    if update.message.text == "🔙 Voltar":
        # Se é Lightning, volta para confirmação; senão volta para endereço
        rede = context.user_data.get('rede', '').lower()
        if 'lightning' in rede:
            return await confirmar_compra(update, context)
        else:
            return await solicitar_endereco(update, context)
    
    metodo_pagamento = update.message.text
    context.user_data['metodo_pagamento'] = metodo_pagamento
    
    # FLUXO TED - Redirecionamento para @GhosttP2P
    if metodo_pagamento == TED:
        await redirecionar_para_ted_boleto(update, context)
        return ConversationHandler.END
    
    # FLUXO BOLETO - Redirecionamento para @GhosttP2P
    elif metodo_pagamento == BOLETO:
        await redirecionar_para_ted_boleto(update, context)
        return ConversationHandler.END
    
    # FLUXO PIX (padrão)
    elif metodo_pagamento == PIX:
        return await processar_pix(update, context)
    
    # Se chegou aqui, método inválido
    await update.message.reply_text(
        "❌ Método de pagamento não reconhecido. Tente novamente.",
        reply_markup=ReplyKeyboardMarkup(menu_metodos_pagamento(), resize_keyboard=True)
    )
    return ESCOLHER_PAGAMENTO

async def registrar_pedido_backend(context, status: str = "pending"):
    """
    Registra o pedido no backend (tabela deposit) para TED e Boleto.
    Salva o id do depósito criado em context.user_data['deposit_id'].
    """
    try:
        from tokens import Config
        user_data = context.user_data
        metodo = user_data.get('metodo_pagamento', '')
        # Decide o endpoint conforme o método de pagamento
        if metodo == PIX:
            url = getattr(Config, 'PIX_API_URL', 'https://useghost.squareweb.app/rest/deposit.php')
        else:
            url = 'https://useghost.squareweb.app/rest/deposit.php'
        payload = {
            'amount_in_cents': int(round(user_data.get('valor_brl', 0) * 100)),
            'address': user_data.get('endereco_recebimento', 'manual'),
            'moeda': user_data.get('moeda', ''),
            'rede': user_data.get('rede', ''),
            'chatid': str(context._user_id if hasattr(context, '_user_id') else user_data.get('chatid', '')),
            'user_id': int(context._user_id if hasattr(context, '_user_id') else user_data.get('chatid', 0)),
            'status': status,
            'metodo_pagamento': metodo,
            'forma_pagamento': metodo,  # 🚀 CAMPO OBRIGATÓRIO ADICIONADO
            'taxa': float(user_data.get('valor_brl', 0)) * 0.01,
            'send': user_data.get('valor_liquido', 0),
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            logger.info(f"Pedido registrado no backend: {payload}")
            try:
                resp_json = response.json()
                if 'id' in resp_json:
                    context.user_data['deposit_id'] = resp_json['id']
            except Exception as e:
                logger.warning(f"Não foi possível obter o id do depósito: {e}")
        else:
            logger.error(f"Erro ao registrar pedido no backend: {response.text}")
    except Exception as e:
        logger.error(f"Falha ao registrar pedido no backend: {e}")

# FUNÇÃO COMENTADA - Substituída por redirecionamento para @GhosttP2P
# async def processar_ted(update: Update, context) -> int:
#     await registrar_pedido_backend(context, status="pending")
#     """Processa pagamento via TED."""
#     try:
#         # Importa as configurações TED dos tokens
#         from tokens import Config
#         
#         # Dados bancários para TED
#         ted_info = f"""🏦 *DADOS PARA TED*
#
# 👤 *Favorecido:* {getattr(Config, 'TED_FAVORECIDO', 'Ghost P2P LTDA')}
# 🏦 *Banco:* {getattr(Config, 'TED_BANCO', 'Banco do Brasil')}
# 🏢 *Agência:* {getattr(Config, 'TED_AGENCIA', '0000-1')}
# 💳 *Conta:* {getattr(Config, 'TED_CONTA', '12345-6')}
# 📄 *CPF/CNPJ:* {getattr(Config, 'TED_CPF_CNPJ', '000.000.000-00')}
#
# 💰 *Valor a transferir:* {formatar_brl(context.user_data.get('valor_brl', 0))}
#
# 📋 *INSTRUÇÕES:*
# 1. Faça a TED usando os dados acima
# 2. Após o pagamento, envie o comprovante
# 3. Aguarde a confirmação
#
# ⚠️ *IMPORTANTE:* O comprovante deve ser em formato .PDF, .JPG, .PNG ou .JPEG"""
#
#         # Teclado para aguardar comprovante
#         teclado = [["📎 Enviar Comprovante"], ["🔙 Voltar"]]
#         reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
#         
#         await update.message.reply_text(
#             ted_info,
#             parse_mode='Markdown',
#             reply_markup=reply_markup
#         )
#         
#         # Envia segunda mensagem
#         await update.message.reply_text(
#             "📨 *Após o pagamento, envie o comprovante do TED para agilizar o processo.*",
#             parse_mode='Markdown'
#         )
#         
#         return AGUARDAR_TED_COMPROVANTE
#         
#     except Exception as e:
#         logger.error(f"Erro ao processar TED: {e}")
#         await update.message.reply_text(
#             "❌ Erro ao processar TED. Tente outro método de pagamento.",
#             reply_markup=ReplyKeyboardMarkup(menu_metodos_pagamento(), resize_keyboard=True)
#         )
#         return ESCOLHER_PAGAMENTO

# FUNÇÃO COMENTADA - Substituída por redirecionamento para @GhosttP2P
# async def processar_comprovante_ted(update: Update, context) -> int:
#     """Processa o comprovante de TED enviado."""
#     if update.message.text == "🔙 Voltar":
#         return await mostrar_metodos_pagamento(update, context)
# 
#     # Verifica se é um documento/foto
#     if update.message.document or update.message.photo:
#         try:
#             # Salva informações do arquivo
#             if update.message.document:
#                 file_info = update.message.document
#                 file_name = file_info.file_name or "comprovante_ted"
#                 file_id = file_info.file_id
#             else:
#                 file_info = update.message.photo[-1]  # Maior resolução
#                 file_name = "comprovante_ted.jpg"
#                 file_id = file_info.file_id
# 
#             # Verifica extensão do arquivo
#             extensoes_validas = ['.pdf', '.jpg', '.jpeg', '.png']
#             file_ext = '.' + file_name.split('.')[-1].lower() if '.' in file_name else '.jpg'
#             if file_ext not in extensoes_validas:
#                 await update.message.reply_text(
#                     "❌ *Formato não suportado*\n\n"
#                     "Por favor, envie o comprovante em formato PDF, JPG, PNG ou JPEG.",
#                     parse_mode='Markdown'
#                 )
#                 return AGUARDAR_TED_COMPROVANTE
# 
#             # Baixa o arquivo do Telegram
#             bot = context.bot
#             new_file = await bot.get_file(file_id)
#             file_path = f"/tmp/{file_name}"
#             await new_file.download_to_drive(file_path)
# 
#             # Prepara dados para upload
#             user_data = context.user_data
#             chatid = str(context._user_id if hasattr(context, '_user_id') else user_data.get('chatid', ''))
#             deposit_id = user_data.get('deposit_id')
#             url = 'https://useghost.squareweb.app/api/upload_comprovante.php'
#             files = {'comprovante': (file_name, open(file_path, 'rb'))}
#             data = {'chatid': chatid}
#             if deposit_id:
#                 data['deposit_id'] = str(deposit_id)
#             try:
#                 import requests
#                 response = requests.post(url, files=files, data=data, timeout=20)
#                 if response.status_code == 200 and 'success' in response.text:
#                     await update.message.reply_text(
#                         "✅ *Comprovante recebido e enviado para análise!*\n\n"
#                         "🔄 Transação em processamento, aguarde a confirmação.\n\n"
#                         "Você receberá uma notificação assim que o pagamento for confirmado.",
#                         parse_mode='Markdown',
#                         reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
#                     )
#                 else:
#                     await update.message.reply_text(
#                         "⚠️ *Comprovante recebido, mas houve um erro ao enviar ao sistema.*\n\n"
#                         "Tente novamente ou contate o suporte.",
#                         parse_mode='Markdown',
#                         reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
#                     )
#             except Exception as e:
#                 logger.error(f"Erro ao enviar comprovante para backend: {e}")
#                 await update.message.reply_text(
#                     "❌ Erro ao enviar comprovante ao sistema. Tente novamente ou envie para o suporte.",
#                     parse_mode='Markdown',
#                     reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
#                 )
#             finally:
#                 try:
#                     os.remove(file_path)
#                 except Exception:
#                     pass
#             context.user_data.clear()
#             return ConversationHandler.END
#         except Exception as e:
#             logger.error(f"Erro ao processar comprovante: {e}")
#             await update.message.reply_text(
#                 "❌ Erro ao processar o comprovante. Tente novamente.",
#                 parse_mode='Markdown'
#             )
#             return AGUARDAR_TED_COMPROVANTE
#     else:
#         await update.message.reply_text(
#             "📎 *Por favor, envie o comprovante como arquivo ou foto.*\n\n"
#             "Formatos aceitos: PDF, JPG, PNG, JPEG",
#             parse_mode='Markdown'
#         )
#         return AGUARDAR_TED_COMPROVANTE

# FUNÇÃO COMENTADA - Substituída por redirecionamento para @GhosttP2P
# async def processar_boleto(update: Update, context) -> int:
#     await registrar_pedido_backend(context, status="pending")
#     """Processa pagamento via Boleto - direciona para admin."""
#     try:
#         # Importa as configurações do boleto
#         from tokens import Config
#         admin_contact = getattr(Config, 'BOLETO_CHAT_ID', '@triacorelabs')
#         
#         mensagem = f"""📄 *PAGAMENTO VIA BOLETO*
# 
# Para efetuar o pagamento via boleto bancário, entre em contato com nosso administrador:
# 
# 👤 *Contato:* {admin_contact}
# 
# 💰 *Valor:* {formatar_brl(context.user_data.get('valor_brl', 0))}
# 💎 *Moeda:* {context.user_data.get('moeda', '')}
# ⚡ *Rede:* {context.user_data.get('rede', '')}
# 
# 📋 *O administrador irá:*
# • Gerar o boleto bancário
# • Enviar as instruções de pagamento
# • Processar sua compra após confirmação
# 
# ⏰ *Prazo:* Até 2 dias úteis para processamento"""
# 
#         await update.message.reply_text(
#             mensagem,
#             parse_mode='Markdown',
#             reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
#         )
#         
#         context.user_data.clear()
#         return ConversationHandler.END
#         
#     except Exception as e:
#         logger.error(f"Erro ao processar boleto: {e}")
#         await update.message.reply_text(
#             "❌ Erro ao processar boleto. Tente outro método de pagamento.",
#             reply_markup=ReplyKeyboardMarkup(menu_metodos_pagamento(), resize_keyboard=True)
#         )
#         return ESCOLHER_PAGAMENTO

# Flag para modo de teste (pode ser ativada por variável de ambiente ou config)
TESTE_PIX_MOCK = True  # Altere para False para desativar o mock

async def processar_pix(update: Update, context) -> int:
    """Processa pagamento via PIX."""
    # 🎯 CAPTURA: Início do processamento PIX
    chatid = str(update.effective_user.id)
    capture_step(chatid, "PROCESSAR_PIX", {
        "timestamp": datetime.now().isoformat()
    })
    try:
        # Dados da compra
        moeda = context.user_data.get('moeda', 'a moeda selecionada')
        rede = context.user_data.get('rede', 'a rede selecionada')
        valor_brl = context.user_data.get('valor_brl', 0)
        endereco = context.user_data.get('endereco_recebimento', '')
        # 🎯 CAPTURA: Dados da compra capturados
        capture_step(chatid, "DADOS_COMPRA_PIX", {
            "moeda": moeda,
            "rede": rede,
            "valor_brl": valor_brl,
            "endereco": endereco[:20] + "..." if len(endereco) > 20 else endereco
        })
        valor_formatado = formatar_brl(valor_brl)
        cotacao = await obter_cotacao(moeda)
        taxa = 0.05  # 5% de taxa
        valor_taxa = valor_brl * taxa
        valor_liquido = valor_brl - valor_taxa
        valor_recebido = valor_liquido / cotacao
        valor_recebido_formatado = formatar_cripto(valor_recebido, moeda)
        # FLUXO ESPECIAL PARA LIGHTNING: Usa integração Voltz
        if 'lightning' in rede.lower():
            try:
                voltz = VoltzAPI(backend_url='https://useghost.squareweb.app')
                result = voltz.create_deposit_request(
                    chatid=chatid,
                    userid=chatid,  # Remover userid, usar apenas chatid
                    amount_in_cents=int(valor_brl * 100),
                    taxa=taxa,
                    moeda=moeda.upper(),
                    send_amount=int(valor_recebido * 100000000) if 'BTC' in moeda.upper() else valor_recebido
                )
                await update.message.reply_text(
                    f"⚡ *COMPRA LIGHTNING NETWORK* ⚡\n\n"
                    f"💰 *Valor:* {valor_formatado}\n"
                    f"⚡ *Você receberá:* {int(valor_recebido * 100000000)} sats\n"
                    f"🆔 *ID:* `{result['depix_id']}`\n\n"
                    f"📋 *PRÓXIMOS PASSOS:*\n"
                    f"1️⃣ Pague o PIX abaixo\n"
                    f"2️⃣ Após confirmação, forneça seu Lightning Address ou Invoice\n"
                    f"3️⃣ Receba os bitcoins instantaneamente!\n\n"
                    f"🎯 *Formatos aceitos:* Lightning Address (`usuario@wallet.com`) ou BOLT11 Invoice (`lnbc...`)\n\n"
                    f"💡 *O sistema detectará automaticamente o formato e processará o pagamento!*",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Erro no fluxo Lightning Voltz: {e}")
                await update.message.reply_text(
                    "❌ *Erro ao processar pagamento Lightning*\n\n"
                    "Tente novamente ou escolha outro método de pagamento.",
                    parse_mode='Markdown',
                    reply_markup=ReplyKeyboardMarkup(menu_metodos_pagamento(), resize_keyboard=True)
                )
                return ESCOLHER_PAGAMENTO
        # FLUXO NORMAL PARA OUTRAS REDES
        from api.depix import pix_api
        logger.info(f"Iniciando processamento de PIX - Valor: {valor_brl}, Endereço: {endereco}")
        valor_centavos = int(round(valor_brl * 100))
        try:
            cobranca = pix_api.criar_pagamento(
                valor_centavos=valor_centavos,
                endereco=endereco,
                chatid=chatid,
                moeda=moeda.upper(),
                rede=rede,
                taxa=round(taxa * 100, 2),
                forma_pagamento="PIX",
                send=float(valor_recebido),
                user_id=chatid,  # Remover user_id, usar apenas chatid
                comprovante="Lightning Invoice" if 'lightning' in rede.lower() else None,
                cpf=context.user_data.get('cpf')
            )
        except Exception as e:
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
            return ConversationHandler.END
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
            return ConversationHandler.END
        # --- REGISTRO DO DEPÓSITO NO BACKEND (DEPIX) ---
        try:
            payload = {
                "chatid": chatid,
                "moeda": moeda.upper(),
                "rede": rede,
                "amount_in_cents": valor_centavos,
                "taxa": round(taxa * 100, 2),
                "address": endereco,
                "forma_pagamento": "PIX",
                "send": float(valor_recebido),
                "depix_id": txid,
                "status": "pending",
                # "user_id": chatid,  # Remover user_id, usar apenas chatid
            }
            if 'lightning' in rede.lower():
                payload["comprovante"] = "Lightning Invoice"
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://useghost.squareweb.app/rest/deposit.php",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    backend_resp = await resp.json()
                    if not backend_resp.get("success", False):
                        pass
        except Exception as e:
            logger.error(f"Erro ao registrar depósito no backend: {e}")
        # --- FIM REGISTRO BACKEND ---
        try:
            register_pix_payment(txid, chatid, valor_brl)
            logger.info(f"✅ PIX {txid} registrado no Smart Monitor")
        except Exception as e:
            logger.error(f"Erro ao registrar no Smart Monitor: {e}")
        await update.message.reply_photo(
            photo=qr_code,
            caption='📱 *QR Code para pagamento*\n\nAponte a câmera do seu app de pagamento para escanear o QR Code acima.',
            parse_mode='Markdown'
        )
        if 'lightning' in rede.lower():
            mensagem_confirmacao = (
                '⚡ *PAGAMENTO PIX → LIGHTNING* ⚡\n'
                '━━━━━━━━━━━━━━━━━━━━\n'
                f'• *Valor PIX:* {valor_formatado}\n'
                f'• *Receberá:* {int(valor_recebido * 100000000)} sats\n'
                f'• *ID:* `{txid}`\n\n'
                '📱 *Código Copia e Cola:*\n\n'
                f'`{copia_e_cola}`\n\n'
                '⚡ *IMPORTANTE - LEIA COM ATENÇÃO:*\n'
                '1️⃣ Pague o PIX usando o código acima\n'
                '2️⃣ *AGUARDE a confirmação do pagamento PIX*\n'
                '3️⃣ *SOMENTE APÓS* a confirmação, o bot solicitará seu invoice Lightning\n'
                '4️⃣ Você receberá os sats automaticamente em sua carteira\n\n'
                '⚠️ *NÃO ENVIE SEU INVOICE AGORA!*\n'
                '🤖 O bot pedirá automaticamente quando o PIX for confirmado\n'
                '⏱️ Tempo estimado: 5-10 minutos após o pagamento PIX\n\n'
                '📋 *Prepare sua carteira Lightning:*\n'
                '• Baixe uma carteira Lightning (recomendamos Phoenix ou Wallet of Satoshi)\n'
                '• O bot pedirá um invoice quando o PIX for confirmado\n'
                '• Aguarde a notificação automática\n\n'
                '✅ Primeiro: Pague o PIX e aguarde a confirmação!'
            )
        else:
            mensagem_confirmacao = (
                '✅ *SOLICITAÇÃO DE COMPRA RECEBIDA!*\n'
                '━━━━━━━━━━━━━━━━━━━━\n'
                f'• *Valor:* {valor_formatado}\n'
                f'• *Criptomoeda:* {moeda.upper()}\n'
                f'• *Rede:* {rede}\n'
                f'• *Endereço:* `{endereco}`\n'
                f'• *ID da transação:* `{txid}`\n\n'
                '📱 *Código Copia e Cola:*\n\n'
                f'`{copia_e_cola}`\n\n'
                '⏰ Após o pagamento, aguarde alguns instantes para a confirmação.\n'
                '✅ Obrigado pela preferência!'
            )
        await update.message.reply_text(
            mensagem_confirmacao,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
        )
        if 'lightning' in rede.lower():
            logger.info(f"Lightning PIX criado - depix_id: {txid}, chat_id: {chatid}")
            logger.info("Aguardando confirmação PIX para disparar invoice Lightning")
            try:
                from trigger.sistema_gatilhos import trigger_system, TriggerEvent
                trigger_system.trigger_event(
                    TriggerEvent.PIX_PAYMENT_DETECTED,
                    chatid,
                    {'depix_id': txid}
                )
            except Exception as e:
                pass
        return ConversationHandler.END
    except Exception as e:
        # 🎯 CAPTURA: Erro no processamento PIX
        capture_error(chatid, f"Erro no processamento PIX: {str(e)}", "processar_pix")
        logger.error(f"Erro no processamento PIX: {e}")
        await update.message.reply_text(
            "❌ *Erro ao processar pagamento PIX*\n\n"
            "Tente novamente ou escolha outro método de pagamento.",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(menu_metodos_pagamento(), resize_keyboard=True)
        )
        return ESCOLHER_PAGAMENTO

async def cancelar_compra(update: Update, context) -> int:
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

def validar_cpf(cpf: str) -> bool:
    """Valida o CPF (formato e dígitos)."""
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i+1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

async def solicitar_cpf(update: Update, context) -> int:
    """Solicita o CPF do usuário."""
    try:
        await update.message.reply_text(
            "📝 *Precisamos do seu CPF para continuar*\n\n"\
            "Informe seu CPF (apenas números):",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([["🔙 Voltar"]], resize_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Erro ao solicitar CPF: {e}")
        await update.message.reply_text(
            "❌ Erro ao solicitar CPF. Tente novamente.",
            parse_mode='Markdown'
        )
    return SOLICITAR_CPF

async def processar_cpf(update: Update, context) -> int:
    """Processa o CPF informado, valida e envia ao backend."""
    if update.message.text == "🔙 Voltar":
        return await cancelar_compra(update, context)
    cpf = ''.join(filter(str.isdigit, update.message.text))
    if not validar_cpf(cpf):
        await update.message.reply_text(
            "❌ CPF inválido. Por favor, digite novamente (apenas números).",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([["🔙 Voltar"]], resize_keyboard=True)
        )
        return SOLICITAR_CPF
    context.user_data['cpf'] = cpf
    # Envia dados do usuário para o backend PHP e consulta limite
    try:
        user = update.effective_user
        payload = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "cpf": cpf
        }
        url = "https://useghost.squareweb.app/api/user_api.php"
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        limite_msg = ""
        if resp.status_code == 200:
            try:
                data = resp.json()
                limite = data.get("limite")
                if limite is not None:
                    limite_msg = f"\n\n💳 *Seu limite diário:* R$ {float(limite):,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
            except Exception as e:
                logger.warning(f"Não foi possível obter limite do backend: {e}")
        await update.message.reply_text(
            f"✅ CPF cadastrado com sucesso!{limite_msg}\n\nAgora vamos continuar sua compra.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.warning(f"Não foi possível enviar dados do usuário ao backend: {e}")
        await update.message.reply_text(
            "⚠️ Não foi possível validar seu CPF no momento, mas você pode continuar.",
            parse_mode='Markdown'
        )
    # Após cadastrar o CPF, segue para o resumo da compra
    return await resumo_compra(update, context)

def get_compra_conversation():
    """Retorna o ConversationHandler para o fluxo de compra."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🛒 Comprar$'), iniciar_compra)],  # Corrigido para iniciar pelo menu de moedas
        states={
            SOLICITAR_CPF: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_cpf)
            ],
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
            RESUMO_COMPRA: [
                MessageHandler(filters.Regex('^✅ Confirmar Compra$'), confirmar_compra),
                MessageHandler(filters.Regex('^✏️ Alterar Valor$'), confirmar_compra),
                MessageHandler(filters.Regex('^🔙 Mudar Moeda$'), confirmar_compra),
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_compra)
            ],
            SOLICITAR_ENDERECO: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), confirmar_compra),
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_endereco)
            ],
            ESCOLHER_PAGAMENTO: [
                MessageHandler(filters.Regex('^🔙 Voltar$'), lambda u, c: solicitar_endereco(u, c) if 'endereco_recebimento' not in c.user_data else confirmar_compra(u, c)),
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_metodo_pagamento)
            ],
            # AGUARDAR_TED_COMPROVANTE: [
            #     MessageHandler(filters.Regex('^🔙 Voltar$'), mostrar_metodos_pagamento),
            #     MessageHandler(filters.PHOTO | filters.Document.ALL, processar_comprovante_ted),
            #     MessageHandler(filters.TEXT & ~filters.COMMAND, processar_comprovante_ted)
            # ]
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

# 🎯 FUNÇÕES DE CAPTURA PARA MENU COMPRA
def capture_step(user_id: str, step_name: str, data: Dict[str, Any] = None, success: bool = True):
    """Captura um passo do fluxo de compra"""
    if CAPTURE_ENABLED and capture_system:
        try:
            capture_system.capture_step(
                str(user_id),
                step_name,
                data or {},
                success
            )
        except Exception as e:
            logging.warning(f"Erro ao capturar passo {step_name}: {e}")

def capture_user_session(user_id: str, username: str = None):
    """Inicia uma sessão de captura para o usuário"""
    if CAPTURE_ENABLED and capture_system:
        try:
            capture_system.start_session(str(user_id), username)
        except Exception as e:
            logging.warning(f"Erro ao iniciar sessão de captura: {e}")

def capture_error(user_id: str, error: str, context: str = ""):
    """Captura um erro no fluxo"""
    if CAPTURE_ENABLED and capture_system:
        try:
            capture_system.capture_error(str(user_id), error, context)
        except Exception as e:
            logging.warning(f"Erro ao capturar erro: {e}")
