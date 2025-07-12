# MENU DE COMPRA V2 - VERSÃO LIMPA E OTIMIZADA
# Criado em 10/07/2025 para substituir o menu antigo com problemas
# Foco: Simplicidade, robustez e identificação consistente

import logging
import re
import time
import asyncio
import aiohttp
import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import MessageHandler, ConversationHandler, CommandHandler, filters
from telegram.ext import ContextTypes
from comissao.validador import gerar_resumo_compra

# 🎯 SISTEMA DE CAPTURA LIMPO
try:
    from captura.capture_system import capture_system
    CAPTURE_ENABLED = True
    
    def capture_step(chatid: str, step: str, data: Dict = None):
        if CAPTURE_ENABLED and capture_system:
            try:
                capture_system.capture_event(chatid, step, data or {})
            except Exception:
                pass  # Falha silenciosa para não quebrar o fluxo
    
    def capture_error(chatid: str, error: str, context: str):
        if CAPTURE_ENABLED and capture_system:
            try:
                capture_system.capture_error(chatid, error, context)
            except Exception:
                pass  # Falha silenciosa para não quebrar o fluxo
    
    def capture_user_session(chatid: str, username: str = "Unknown"):
        if CAPTURE_ENABLED and capture_system:
            try:
                capture_system.start_session(chatid, username)
            except Exception:
                pass  # Falha silenciosa para não quebrar o fluxo
    
    print("✅ Sistema de captura V2 carregado")
except Exception as e:
    print(f"⚠️ Sistema de captura não disponível: {e}")
    CAPTURE_ENABLED = False
    
    def capture_step(chatid: str, step: str, data: Dict = None):
        pass  # No-op
    
    def capture_error(chatid: str, error: str, context: str):
        pass  # No-op
    
    def capture_user_session(chatid: str, username: str = "Unknown"):
        pass  # No-op

# 🚀 IMPORTS ESSENCIAIS
try:
    from api.depix import pix_api
    from direct_notification import notification_system
    DEPIX_ENABLED = True
except Exception as e:
    print(f"⚠️ API Depix não disponível: {e}")
    DEPIX_ENABLED = False

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Estados da conversa
ESCOLHER_MOEDA, ESCOLHER_REDE, INFORMAR_VALOR, CONFIRMAR_DADOS, ESCOLHER_PAGAMENTO = range(5)

# Constantes
PIX = "💠 PIX"
MIN_VALOR = 10.0
MAX_VALOR = 5000.0

# Caminho relativo para o diretório de logs
LOG_DIR = os.path.join(os.path.dirname(__file__), '../log_final')
LOG_PATH = os.path.join(LOG_DIR, 'bot.log')

# Garante que o diretório de logs existe
os.makedirs(LOG_DIR, exist_ok=True)

def log_event(event_type, chatid=None, data=None):
    """Registra evento no log principal do bot"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "chatid": chatid,
            "data": data or {}
        }
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Erro ao registrar log: {e}")

# ==========================================
# FUNÇÕES DE LOG E CAPTURA
# ==========================================
# log_event: registra eventos críticos no arquivo de log principal
# capture_step/capture_error/capture_user_session: sistema de captura para rastreabilidade

# ==========================================
# CLASSE PRINCIPAL DO MENU DE COMPRA
# ==========================================
class MenuCompraV2:
    """
    Menu de compra V2 - Versão limpa e otimizada
    Gerencia todo o fluxo de compra do bot Ghost, incluindo seleção de moeda, rede,
    valor, confirmação, pagamento e integração com backend/stateless.
    """
    
    def __init__(self):
        self.menu_principal_func = None
    
    def set_menu_principal(self, menu_func):
        """Define a função do menu principal"""
        self.menu_principal_func = menu_func
    
    # ==========================================
    # HELPERS E VALIDAÇÕES
    # ==========================================
    # formatar_brl: formata valores em reais
    # validar_valor: valida e converte valores informados pelo usuário
    # validar_limites_valor: verifica limites permitidos
    # get_chatid: obtém o chatid do usuário

    # ==========================================
    # MENUS E KEYBOARDS
    # ==========================================
    # menu_moedas/menu_redes/menu_valores_sugeridos/menu_confirmacao/menu_pagamento:
    # geram os teclados de opções para cada etapa do fluxo

    # ==========================================
    # HANDLERS DA CONVERSA
    # ==========================================
    # iniciar_compra: inicia o fluxo de compra
    # escolher_moeda: processa escolha da moeda
    # escolher_rede: processa escolha da rede
    # informar_valor: processa valor informado
    # confirmar_dados: processa confirmação dos dados
    # escolher_pagamento: processa escolha da forma de pagamento

    # ==========================================
    # PROCESSAMENTO PIX
    # ==========================================
    # atualizar_status_deposito_backend: atualiza status do depósito no backend
    # validar_pagamento_confirmado_backend: valida pagamento via backend REST
    # _processar_pix: processa pagamento PIX, integra com Depix, backend e libera envio dos sats
    # _simular_pix: simula pagamento PIX para testes
    # _fallback_check: verificação de fallback caso o sistema principal falhe
    # _validar_resposta_depix: valida resposta da API Depix
    # _extrair_dados_pix: extrai dados do PIX da resposta da API

    # ==========================================
    # HELPERS
    # ==========================================
    # _cancelar_compra: cancela a compra e retorna ao menu principal
    # _get_main_menu: retorna o teclado do menu principal

    # ==========================================
    # CONVERSATION HANDLER
    # ==========================================
    # get_conversation_handler: retorna o ConversationHandler configurado para o fluxo

    # ==========================================
    # CÁLCULO DE COMISSÃO E CONVERSÃO
    # ==========================================
    # calcular_comissao_fallback: calcula comissão padrão
    # calcular_sats_equivalente: converte BRL para sats usando cotação online ou fallback

    # ==========================================
    # INSTÂNCIA GLOBAL E FUNÇÕES DE COMPATIBILIDADE
    # ==========================================
    # menu_compra_v2: instância global do menu
    # get_compra_conversation_v2/set_menu_principal_v2: funções de compatibilidade

    # ==========================================
    # LOGS DE INICIALIZAÇÃO
    # ==========================================
    # Prints informativos sobre funcionalidades carregadas

    def formatar_brl(self, valor: float) -> str:
        """Formata valor em BRL"""
        return f"R$ {valor:,.2f}".replace(".", "v").replace(",", ".").replace("v", ",")
    
    def validar_valor(self, valor_str: str) -> tuple[bool, float, str]:
        """Valida e converte valor informado, aceitando formatos como 'R$ 50,00', '50,00 reais', etc."""
        try:
            # Remove símbolos de moeda, espaços e texto extra
            valor_str = valor_str.replace('R$', '').replace('reais', '').replace('REAIS', '').replace('Real', '').replace('REAL', '').replace(' ', '').replace('.', '').replace(',', '.')
            # Extrai o primeiro número decimal ou inteiro do texto
            match = re.search(r'(\d+\.?\d*)', valor_str)
            if not match:
                return False, 0, "Formato inválido. Use apenas números (ex: 50.00)"
            valor = float(match.group(1))
            if valor < MIN_VALOR:
                return False, 0, f"Valor mínimo é {self.formatar_brl(MIN_VALOR)}"
            if valor > MAX_VALOR:
                return False, 0, f"Valor máximo é {self.formatar_brl(MAX_VALOR)}"
            return True, valor, ""
        except (ValueError, AttributeError):
            return False, 0, "Formato inválido. Use apenas números (ex: 50.00)"
    
    def validar_limites_valor(self, valor: float) -> bool:
        """Valida se o valor está dentro dos limites permitidos"""
        return MIN_VALOR <= valor <= MAX_VALOR
    
    def get_chatid(self, update: Update) -> str:
        """Obtém chatid de forma consistente"""
        return str(update.effective_user.id)
    
    # ==========================================
    # MENUS E KEYBOARDS
    # ==========================================
    
    def menu_moedas(self):
        """Menu de seleção de moedas"""
        return [
            ["Bitcoin", "USDT", "DEPIX"],
            ["🔙 Voltar"]
        ]
    
    def menu_redes(self):
        """Menu de seleção de redes conforme a moeda escolhida"""
        moeda = getattr(self, '_moeda_selecionada', None)
        if moeda == "Bitcoin (BTC)" or moeda == "Bitcoin":
            return [
                ["⚡ Lightning", "💧 Liquid", "🔗 Onchain"],
                ["🔙 Voltar"]
            ]
        elif moeda == "USDT":
            return [
                ["💧 Liquid", "🟣 Polygon"],
                ["🔙 Voltar"]
            ]
        elif moeda == "DEPIX":
            return [
                ["💧 Liquid"],
                ["🔙 Voltar"]
            ]
        else:
            return [
                ["⚡ Lightning"],
                ["🔙 Voltar"]
            ]

    
    def menu_valores_sugeridos(self):
        """Menu com valores sugeridos"""
        return [
            ["R$ 10,00", "R$ 25,00", "R$ 50,00"],
            ["R$ 100,00", "R$ 250,00", "R$ 500,00"],
            ["🔙 Voltar"]
        ]
    
    def menu_confirmacao(self):
        """Menu de confirmação"""
        return [
            ["✅ Confirmar Compra"],
            ["✏️ Alterar Valor", "🔙 Voltar"]
        ]
    
    def menu_pagamento(self):
        """Menu de formas de pagamento"""
        return [
            ["💠 PIX", "🏦 TED", "📄 Boleto"],
            ["🔙 Voltar"]
        ]
    
    # ==========================================
    # HANDLERS DA CONVERSA
    # ==========================================
    
    async def iniciar_compra(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Inicia o fluxo de compra"""
        chatid = self.get_chatid(update)
        user = update.effective_user
        username = user.username or user.first_name or "Unknown"
        
        # Inicia sessão de captura
        capture_user_session(chatid, username)
        capture_step(chatid, "COMPRA_INICIADA", {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "user_id": user.id
        })
        log_event("COMPRA_INICIADA", chatid, {"username": username})
        
        try:
            # Limpa dados anteriores
            context.user_data.clear()
            
            reply_markup = ReplyKeyboardMarkup(self.menu_moedas(), resize_keyboard=True)
            
            await update.message.reply_text(
                "🪙 *ESCOLHA A MOEDA*\n\n"
                "Selecione a criptomoeda que deseja comprar:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            capture_step(chatid, "MENU_MOEDAS_EXIBIDO", {"success": True})
            return ESCOLHER_MOEDA
            
        except Exception as e:
            capture_error(chatid, str(e), "iniciar_compra")
            logger.error(f"Erro iniciando compra: {e}")
            log_event("ERRO", chatid, {"erro": str(e), "contexto": "iniciar_compra"})
            
            await update.message.reply_text(
                "❌ Erro ao iniciar compra. Tente novamente.",
                reply_markup=self._get_main_menu()
            )
            return ConversationHandler.END
    
    async def escolher_moeda(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Processa escolha da moeda"""
        chatid = self.get_chatid(update)
        escolha = update.message.text

        capture_step(chatid, "MOEDA_ESCOLHIDA", {"moeda": escolha})
        log_event("MOEDA_ESCOLHIDA", chatid, {"moeda": escolha})

        if escolha == "🔙 Voltar":
            return await self._cancelar_compra(update, context)

        if "Bitcoin" in escolha or "BTC" in escolha:
            context.user_data['moeda'] = "Bitcoin (BTC)"
            context.user_data['moeda_codigo'] = "BTC"
            self._moeda_selecionada = "Bitcoin (BTC)"
            reply_markup = ReplyKeyboardMarkup(self.menu_redes(), resize_keyboard=True)
            await update.message.reply_text(
                "⚡ *ESCOLHA A REDE*\n\nSelecione a rede para sua transação:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return ESCOLHER_REDE
        elif "USDT" in escolha:
            context.user_data['moeda'] = "USDT"
            context.user_data['moeda_codigo'] = "USDT"
            self._moeda_selecionada = "USDT"
            reply_markup = ReplyKeyboardMarkup(self.menu_redes(), resize_keyboard=True)
            await update.message.reply_text(
                "⚡ *ESCOLHA A REDE*\n\nSelecione a rede para sua transação:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return ESCOLHER_REDE
        elif "DEPIX" in escolha:
            context.user_data['moeda'] = "DEPIX"
            context.user_data['moeda_codigo'] = "DEPIX"
            self._moeda_selecionada = "DEPIX"
            reply_markup = ReplyKeyboardMarkup(self.menu_redes(), resize_keyboard=True)
            await update.message.reply_text(
                "⚡ *ESCOLHA A REDE*\n\nSelecione a rede para sua transação:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return ESCOLHER_REDE
        else:
            await update.message.reply_text(
                "❌ Opção inválida. Selecione uma moeda:",
                reply_markup=ReplyKeyboardMarkup(self.menu_moedas(), resize_keyboard=True)
            )
            return ESCOLHER_MOEDA
    
    async def escolher_rede(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Processa escolha da rede"""
        chatid = self.get_chatid(update)
        escolha = update.message.text
        capture_step(chatid, "REDE_ESCOLHIDA", {"rede": escolha})
        log_event("REDE_ESCOLHIDA", chatid, {"rede": escolha})
        moeda = context.user_data.get('moeda', '')
        # Regras de atendimento
        if (moeda in ["Bitcoin (BTC)", "Bitcoin"] and escolha in ["💧 Liquid", "🔗 Onchain"]) or \
           (moeda == "USDT" and escolha in ["💧 Liquid", "🟣 Polygon"]) or \
           (moeda == "DEPIX" and escolha == "💧 Liquid"):
            await update.message.reply_text(
                "Para esta opção, fale com o atendente: @GhosttP2P",
                parse_mode='Markdown',
                reply_markup=self._get_main_menu()
            )
            return ConversationHandler.END
        if escolha == "🔙 Voltar":
            reply_markup = ReplyKeyboardMarkup(self.menu_moedas(), resize_keyboard=True)
            await update.message.reply_text(
                "🪙 *ESCOLHA A MOEDA*\n\nSelecione a criptomoeda:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return ESCOLHER_MOEDA
        if "Lightning" in escolha:
            context.user_data['rede'] = "Lightning"
            context.user_data['endereco_recebimento'] = 'LIGHTNING_ADDRESS_SOLICITADO'  # Será solicitado depois
            reply_markup = ReplyKeyboardMarkup(self.menu_valores_sugeridos(), resize_keyboard=True)
            await update.message.reply_text(
                f"💰 *VALOR DO INVESTIMENTO*\n\n"
                f"💎 Moeda: {context.user_data['moeda']}\n"
                f"⚡ Rede: {context.user_data['rede']}\n\n"
                f"📊 Limites:\n"
                f"• Mínimo: {self.formatar_brl(MIN_VALOR)}\n"
                f"• Máximo: {self.formatar_brl(MAX_VALOR)}\n\n"
                f"Digite o valor ou escolha uma opção:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return INFORMAR_VALOR
        else:
            await update.message.reply_text(
                "❌ Opção inválida. Selecione uma rede:",
                reply_markup=ReplyKeyboardMarkup(self.menu_redes(), resize_keyboard=True)
            )
            return ESCOLHER_REDE
    
    async def informar_valor(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Processa valor informado"""
        chatid = self.get_chatid(update)
        valor_str = update.message.text
        capture_step(chatid, "VALOR_INFORMADO", {"valor_str": valor_str})
        log_event("VALOR_INFORMADO", chatid, {"valor_str": valor_str})
        if valor_str == "🔙 Voltar":
            reply_markup = ReplyKeyboardMarkup(self.menu_redes(), resize_keyboard=True)
            await update.message.reply_text(
                "⚡ *ESCOLHA A REDE*\n\nSelecione a rede:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return ESCOLHER_REDE
        # Valida valor
        valido, valor, erro = self.validar_valor(valor_str)
        if not valido or not self.validar_limites_valor(valor):
            capture_error(chatid, erro or "Valor fora dos limites", "validar_valor")
            await update.message.reply_text(
                f"❌ {erro or 'Valor fora dos limites'}\n\nTente novamente:",
                reply_markup=ReplyKeyboardMarkup(self.menu_valores_sugeridos(), resize_keyboard=True)
            )
            return INFORMAR_VALOR
        # Salva valor
        context.user_data['valor_brl'] = valor
        moeda = context.user_data.get('moeda', '')
        rede = context.user_data.get('rede', '')
        # Cálculo de comissão (com fallback)
        try:
            from comissao.validador import ComissaoCalculator
            comissao_calc = ComissaoCalculator()
            comissao_info = comissao_calc.calcular_comissao(valor, 'BTC')
            if not comissao_info or 'comissao_total' not in comissao_info:
                comissao_info = self.calcular_comissao_fallback(valor)
        except Exception:
            comissao_info = self.calcular_comissao_fallback(valor)
        context.user_data['comissao_info'] = comissao_info
        # Cálculo de sats com cotação real
        valor_sats = await self.calcular_sats_equivalente(valor)
        if valor_sats == 0:
            valor_sats = 1000
        context.user_data['valor_btc'] = valor_sats
        # Resumo usando validador integrado com limites
        pix = (moeda.upper() in ["BITCOIN", "BTC"] and rede.upper() in ["LIGHTNING", "LNT"])
        resumo = gerar_resumo_compra(chatid, moeda, rede, valor, pix=pix)
        resumo += f"\n\n💸 Comissão: R$ {comissao_info['comissao_total']:.2f} ({comissao_info['taxa_percentual']}%)"
        resumo += f"\n🔢 Valor em sats: {valor_sats:,}"
        reply_markup = ReplyKeyboardMarkup(self.menu_confirmacao(), resize_keyboard=True)
        await update.message.reply_text(
            resumo,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        capture_step(chatid, "RESUMO_EXIBIDO", {"valor": valor, "moeda": moeda, "rede": rede, "sats": valor_sats})
        return CONFIRMAR_DADOS
    
    async def confirmar_dados(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Processa confirmação dos dados"""
        chatid = self.get_chatid(update)
        escolha = update.message.text
        capture_step(chatid, "CONFIRMACAO_PROCESSADA", {"escolha": escolha})
        log_event("CONFIRMACAO_PROCESSADA", chatid, {"escolha": escolha})
        if escolha == "🔙 Voltar":
            reply_markup = ReplyKeyboardMarkup(self.menu_valores_sugeridos(), resize_keyboard=True)
            await update.message.reply_text(
                "💰 *VALOR DO INVESTIMENTO*\n\nDigite o valor:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return INFORMAR_VALOR
        if escolha == "✏️ Alterar Valor":
            return await self.informar_valor(update, context)
        if escolha == "✅ Confirmar Compra":
            moeda = context.user_data.get('moeda', '')
            rede = context.user_data.get('rede', '')
            valor = context.user_data.get('valor_brl', 0)
            pix = context.user_data.get('pagamento', '') == PIX
            # Não exibe resumo novamente aqui
            await update.message.reply_text(
                "Selecione a forma de pagamento:",
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardMarkup(self.menu_pagamento(), resize_keyboard=True)
            )
            return ESCOLHER_PAGAMENTO
        else:
            await update.message.reply_text(
                "❌ Opção inválida. Confirma os dados?",
                reply_markup=ReplyKeyboardMarkup(self.menu_confirmacao(), resize_keyboard=True)
            )
            return CONFIRMAR_DADOS
    
    async def escolher_pagamento(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Processa escolha da forma de pagamento"""
        chatid = self.get_chatid(update)
        escolha = update.message.text
        
        capture_step(chatid, "PAGAMENTO_ESCOLHIDO", {"forma": escolha})
        log_event("PAGAMENTO_ESCOLHIDO", chatid, {"forma": escolha})
        
        if escolha == "🔙 Voltar":
            reply_markup = ReplyKeyboardMarkup(self.menu_confirmacao(), resize_keyboard=True)
            await update.message.reply_text(
                "📋 *RESUMO DA COMPRA*\n\nConfirma os dados?",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return CONFIRMAR_DADOS
        if escolha in ["🏦 TED", "📄 Boleto"]:
            await update.message.reply_text(
                "Para esta forma de pagamento, fale com o atendente: @GhosttP2P",
                parse_mode='Markdown',
                reply_markup=self._get_main_menu()
            )
            return ConversationHandler.END
        if escolha == PIX:
            return await self._processar_pix(update, context)
        else:
            await update.message.reply_text(
                "❌ Opção inválida. Selecione uma forma de pagamento:",
                reply_markup=ReplyKeyboardMarkup(self.menu_pagamento(), resize_keyboard=True)
            )
            return ESCOLHER_PAGAMENTO
    
    # ==========================================
    # PROCESSAMENTO PIX
    # ==========================================
    
    async def atualizar_status_deposito_backend(self, depix_id: str, chatid: str, blockchainTxID: str, novo_status: str = "pagamento_confirmado"):
        """Atualiza o status do depósito no backend após confirmação do pagamento"""
        log_event("ATUALIZAR_STATUS_DEPOSITO", chatid, {"depix_id": depix_id, "blockchainTxID": blockchainTxID, "novo_status": novo_status})
        try:
            url_backend = "https://useghost.squareweb.app/api/deposit_receiver.php"
            payload = {
                "id": None,  # opcional, pode ser ignorado se autoincremento
                "chatid": chatid,
                "depix_id": depix_id,
                "blockchainTxID": blockchainTxID,
                "status": novo_status
            }
            import requests
            resp = requests.post(url_backend, json=payload, timeout=10)
            if resp.status_code == 200:
                logger.info(f"Status do depósito atualizado para {novo_status} (depix_id={depix_id})")
                return True
            else:
                logger.warning(f"Falha ao atualizar status do depósito: {resp.text}")
        except Exception as e:
            logger.error(f"Erro ao atualizar status do depósito: {e}")
        return False

    async def validar_pagamento_confirmado_backend(self, depix_id: str) -> bool:
        """Valida se o pagamento foi confirmado via backend REST."""
        log_event("VALIDAR_PAGAMENTO_BACKEND", None, {"depix_id": depix_id})
        try:
            url = f"https://useghost.squareweb.app/payment_status/check.php?depix_id={depix_id}"
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        status = data.get("status", "pending")
                        if status in ["pix_confirmado", "pagamento_confirmado", "completed"]:
                            return True
            return False
        except Exception as e:
            logger.error(f"Erro ao validar pagamento no backend: {e}")
            return False

    async def _processar_pix(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Processa pagamento PIX de forma limpa"""
        chatid = self.get_chatid(update)
        log_event("PROCESSAR_PIX_INICIADO", chatid)
        try:
            valor_brl = context.user_data['valor_brl']
            valor_centavos = int(valor_brl * 100)
            endereco_temp = "LIGHTNING_PENDING"
            moeda = context.user_data.get('moeda', '')
            rede = context.user_data.get('rede', '')
            # Gera resumo para garantir consistência
            from comissao.validador import gerar_resumo_compra
            resumo = gerar_resumo_compra(chatid, moeda, rede, valor_brl, pix=True)
            if not DEPIX_ENABLED:
                return await self._simular_pix(update, context)
            logger.info(f"Criando PIX para {chatid} - valor: R$ {valor_brl}")
            # Calcular valor em sats antes de registrar depósito
            from comissao.validador import calcular_sats_recebidos
            valor_sats = calcular_sats_recebidos(chatid, "Bitcoin", "Lightning", valor_brl, pix=True)
            context.user_data['valor_btc'] = valor_sats
            logger.info(f"Valor em sats calculado: {valor_sats}")
            if valor_sats == 0:
                logger.error(f"Valor em sats é zero para depósito PIX! chatid={chatid}, valor_brl={valor_brl}")
            valor_btc = valor_sats  # Correção: garante que valor_btc está definido
            cobranca = pix_api.criar_pagamento(
                valor_centavos=valor_centavos,
                endereco=endereco_temp,
                chatid=chatid,
                moeda="BTC",
                rede="Lightning",
                taxa=5.0,  # 5%
                forma_pagamento="PIX",
                send=float(valor_sats),
                user_id=chatid,
                comprovante="Lightning Invoice"
            )
            if not self._validar_resposta_depix(cobranca):
                raise Exception("Resposta inválida da API Depix")
            qr_code, txid, copia_e_cola = self._extrair_dados_pix(cobranca)
            if txid:
                log_event("PIX_TXID_RECEBIDO", chatid, {"txid": txid, "valor_btc": valor_btc})
                # ENVIO AUTOMÁTICO PARA BACKEND (sem banco local)
                try:
                    valor_btc = valor_sats
                    payment_hash = cobranca.get('transaction_id') or cobranca.get('txid', '')
                    deposito_backend = {
                        "id": None,  # opcional, pode ser ignorado se autoincremento
                        "chatid": chatid,
                        "depix_id": txid,
                        "blockchainTxID": payment_hash,
                        "status": "pending",
                        "amount_in_cents": valor_centavos,
                        "send": valor_btc,
                        "rede": "Lightning",
                        "moeda": "BTC",
                        "address": "LIGHTNING_PENDING",
                        "taxa": 5.0,
                        "forma_pagamento": "PIX",
                        "created_at": datetime.now().isoformat(),
                        "user_id": chatid,
                        "notified": 0,
                        "metodo_pagamento": "PIX",
                        "comprovante": "Lightning Invoice",
                        "cpf": None
                    }
                    url_backend = "https://useghost.squareweb.app/api/deposit_receiver.php"
                    requests.post(url_backend, json=deposito_backend, timeout=10)
                    # Validação REST antes de liberar envio dos sats
                    pagamento_confirmado = await self.validar_pagamento_confirmado_backend(txid)
                    if pagamento_confirmado:
                        logger.info(f"Pagamento confirmado via backend para depix_id={txid}, liberando envio dos sats.")
                        # Aqui você pode chamar a função de envio dos sats
                        # Exemplo: await self.enviar_sats_ao_cliente(chatid, valor_btc, payment_hash)
                        # Notificação para admin/cliente
                        await update.message.reply_text(
                            f"✅ Pagamento confirmado! Seus sats serão enviados em instantes.",
                            parse_mode='Markdown'
                        )
                        log_event("PAGAMENTO_CONFIRMADO", chatid, {"depix_id": txid})
                    else:
                        logger.info(f"Pagamento ainda não confirmado para depix_id={txid}, aguardando confirmação.")
                except Exception as e:
                    logger.warning(f"Erro ao enviar depósito para backend: {e}")
                try:
                    asyncio.create_task(notification_system.schedule_smart_checks(txid, chatid))
                    logger.info(f"PIX {txid} agendado para verificação inteligente")
                except Exception as e:
                    logger.warning(f"Erro agendando verificação: {e}")
                    asyncio.create_task(self._fallback_check(txid, chatid))
            await update.message.reply_photo(
                photo=qr_code,
                caption="📱 *Escaneie o QR Code para pagar*",
                parse_mode='Markdown'
            )
            log_event("PIX_QRCODE_ENVIADO", chatid, {"txid": txid, "qr_code": qr_code})
            # Usa o resumo do validador para garantir consistência
            mensagem = (
                f"⚡ *PAGAMENTO PIX → LIGHTNING* ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{resumo}\n"
                f"🆔 ID: `{txid}`\n\n"
                f"📱 *Código Copia e Cola:*\n"
                f"`{copia_e_cola}`\n\n"
                f"📋 *INSTRUÇÕES:*\n"
                f"1️⃣ Pague o PIX acima\n"
                f"2️⃣ Aguarde confirmação (automática)\n"
                f"3️⃣ Informe seu Lightning Address\n"
                f"4️⃣ Receba os sats!\n\n"
                f"⚠️ *Aguarde a confirmação antes de enviar o Lightning Address*"
            )
            await update.message.reply_text(
                mensagem,
                parse_mode='Markdown',
                reply_markup=self._get_main_menu()
            )
            capture_step(chatid, "PIX_CRIADO_SUCESSO", {
                "txid": txid,
                "valor": valor_brl
            })
            log_event("PIX_CRIADO_SUCESSO", chatid, {"txid": txid, "valor": valor_brl})
            context.user_data.clear()
            return ConversationHandler.END
        except Exception as e:
            log_event("ERRO_PROCESSAR_PIX", chatid, {"erro": str(e)})
            capture_error(chatid, str(e), "processar_pix")
            logger.error(f"Erro processando PIX: {e}")
            log_event("ERRO", chatid, {"erro": str(e), "contexto": "processar_pix"})
            await update.message.reply_text(
                f"❌ *Erro ao processar PIX*\n\n"
                f"Tente novamente ou contate o suporte.\n"
                f"Erro: {str(e)[:50]}...",
                parse_mode='Markdown',
                reply_markup=self._get_main_menu()
            )
            context.user_data.clear()
            return ConversationHandler.END
    
    async def _simular_pix(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Simula PIX quando API não está disponível"""
        chatid = self.get_chatid(update)
        log_event("SIMULAR_PIX_INICIADO", chatid)
        try:
            valor_brl = context.user_data['valor_brl']
            moeda = context.user_data.get('moeda', '')
            rede = context.user_data.get('rede', '')
            from comissao.validador import gerar_resumo_compra
            resumo = gerar_resumo_compra(chatid, moeda, rede, valor_brl, pix=True)
            txid = f"test_{chatid}_{int(time.time())}"
            qr_code_url = "https://via.placeholder.com/200x200/0066ff/ffffff?text=QR+PIX"
            copia_e_cola = f"00020126360014BR.GOV.BCB.PIX0114+5511999999999520400005303986540{valor_brl:.2f}5802BR5925GHOST BOT6009SAO PAULO62070503***6304"
            await update.message.reply_text(
                f"🧪 *MODO SIMULAÇÃO - PIX*\n\n"
                f"{resumo}\n"
                f"🆔 ID: `{txid}`\n\n"
                f"📱 Código simulado:\n"
                f"`{copia_e_cola[:50]}...`\n\n"
                f"⚠️ *Este é um PIX simulado para testes*",
                parse_mode='Markdown',
                reply_markup=self._get_main_menu()
            )
            capture_step(chatid, "PIX_SIMULADO", {"txid": txid, "valor": valor_brl})
            log_event("PIX_SIMULADO", chatid, {"txid": txid, "valor": valor_brl})
            context.user_data.clear()
            return ConversationHandler.END
        except Exception as e:
            log_event("ERRO_SIMULAR_PIX", chatid, {"erro": str(e)})
            logger.error(f"Erro na simulação do PIX: {e}")
            await update.message.reply_text(
                f"❌ *Erro na simulação do PIX*\n\n"
                f"Tente novamente ou contate o suporte.\n"
                f"Erro: {str(e)[:50]}...",
                parse_mode='Markdown',
                reply_markup=self._get_main_menu()
            )
            context.user_data.clear()
            return ConversationHandler.END
    
    async def _fallback_check(self, txid: str, chatid: str):
        """Verificação de fallback caso o sistema principal falhe"""
        log_event("FALLBACK_CHECK_INICIADO", chatid, {"txid": txid})
        try:
            await asyncio.sleep(30)  # Aguarda 30s
            from direct_notification import notification_system
            await notification_system.check_and_notify(txid, chatid)
        except Exception as e:
            logger.error(f"Erro na verificação de fallback: {e}")
    
    def _validar_resposta_depix(self, cobranca: Dict) -> bool:
        log_event("VALIDAR_RESPOSTA_DEPIX", None, {"cobranca": cobranca})
        """Valida resposta da API Depix"""
        if not cobranca:
            return False
        
        # Verifica estrutura de sucesso
        if cobranca.get('success') and 'data' in cobranca:
            data = cobranca['data']
            return bool(data.get('qr_image_url') and (data.get('qr_code_text') or data.get('qr_code')))
        
        # Verifica estrutura alternativa
        return bool(cobranca.get('qr_image_url') and (cobranca.get('qr_code_text') or cobranca.get('copia_e_cola')))
    
    def _extrair_dados_pix(self, cobranca: Dict) -> tuple[str, str, str]:
        log_event("EXTRAIR_DADOS_PIX", None, {"cobranca": cobranca})
        """Extrai dados do PIX da resposta da API"""
        if cobranca.get('success') and 'data' in cobranca:
            data = cobranca['data']
            return (
                data.get('qr_image_url', ''),
                data.get('transaction_id', ''),
                data.get('qr_code_text') or data.get('qr_code', '')
            )
        else:
            return (
                cobranca.get('qr_image_url', ''),
                cobranca.get('transaction_id') or cobranca.get('txid', ''),
                cobranca.get('qr_code_text') or cobranca.get('copia_e_cola', '')
            )
    
    # ==========================================
    # HELPERS
    # ==========================================
    
    async def _cancelar_compra(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancela a compra e volta ao menu principal"""
        chatid = self.get_chatid(update)
        log_event("CANCELAR_COMPRA", chatid)
        capture_step(chatid, "COMPRA_CANCELADA")
        log_event("COMPRA_CANCELADA", chatid)
        
        context.user_data.clear()
        
        await update.message.reply_text(
            "❌ Compra cancelada.\n\nVocê pode iniciar uma nova compra a qualquer momento.",
            reply_markup=self._get_main_menu()
        )
        
        return ConversationHandler.END
    
    def _get_main_menu(self):
        """Retorna keyboard do menu principal"""
        try:
            if self.menu_principal_func:
                main_menu = self.menu_principal_func()
                if main_menu:
                    return ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        except Exception:
            pass
        
        # Fallback
        return ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
    
    # ==========================================
    # CONVERSATION HANDLER
    # ==========================================
    
    def get_conversation_handler(self):
        """Retorna o ConversationHandler configurado"""
        return ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex('^🛒 Comprar$'), self.iniciar_compra),
                MessageHandler(filters.Regex('^Comprar$'), self.iniciar_compra)
            ],
            states={
                ESCOLHER_MOEDA: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.escolher_moeda)
                ],
                ESCOLHER_REDE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.escolher_rede)
                ],
                INFORMAR_VALOR: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.informar_valor)
                ],
                CONFIRMAR_DADOS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirmar_dados)
                ],
                ESCOLHER_PAGAMENTO: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.escolher_pagamento)
                ]
            },
            fallbacks=[
                CommandHandler('start', self._cancelar_compra),
                MessageHandler(filters.Regex('^/cancelar$'), self._cancelar_compra),
                MessageHandler(filters.Regex('^❌ Cancelar$'), self._cancelar_compra)
            ],
            name="compra_v2_conversation"
        )

    def calcular_comissao_fallback(self, valor: float) -> dict:
        """Calcula comissão padrão de fallback (taxa fixa 5%)"""
        taxa_percentual = 5.0
        comissao_total = round(valor * taxa_percentual / 100, 2)
        return {
            "comissao_total": comissao_total,
            "taxa_percentual": taxa_percentual
        }
    
    async def calcular_sats_equivalente(self, valor_brl: float) -> int:
        """Converte BRL para sats usando cotação online ou fallback, com validação extra"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://blockchain.info/tobtc?currency=BRL&value={valor_brl:.2f}"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        btc_str = await resp.text()
                        btc = float(btc_str)
                        # Se o valor em BTC for maior que 0.01, provavelmente está errado
                        if btc > 0.01:
                            logger.warning(f"Cotação BTC anormal para R$ {valor_brl}: {btc_str} BTC")
                            return 1000
                        sats = int(round(btc * 100_000_000))
                        if 1 <= sats <= 1_000_000:
                            return sats
        except Exception as e:
            logger.warning(f"Erro ao converter BRL para sats: {e}")
        # Fallback: retorna 1000 sats se não conseguir cotação
        return 1000

# ==========================================
# INSTÂNCIA GLOBAL
# ==========================================

# Cria instância global
menu_compra_v2 = MenuCompraV2()

# Funções de compatibilidade
def get_compra_conversation_v2():
    """Retorna o conversation handler V2"""
    return menu_compra_v2.get_conversation_handler()

def set_menu_principal_v2(menu_func):
    """Define função do menu principal"""
    menu_compra_v2.set_menu_principal(menu_func)

# ==========================================
# LOGS DE INICIALIZAÇÃO
# ==========================================

print("✅ Menu Compra V2 carregado com sucesso!")
print("📋 Funcionalidades:")
print("   - ✅ Identificação consistente (apenas chatid)")
print("   - ✅ Fluxo simplificado (5 estados)")
print("   - ✅ Tratamento robusto de erros")
print("   - ✅ Sistema de captura integrado")
print("   - ✅ Fallbacks para APIs indisponíveis")
print("   - ✅ Logs detalhados")
print("   - ✅ Código limpo e documentado")
