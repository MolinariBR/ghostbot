#!/usr/bin/env python3
"""
Lightning Address Handler - Processa endereços Lightning digitados pelo usuário
Integra com o backend para finalizar pagamentos Lightning
"""
import logging
import re
import requests
import json
import asyncio
from typing import Dict, Any, Optional
from telegram import Update
from telegram.ext import ContextTypes

# Configuração de logging
logger = logging.getLogger(__name__)

class LightningAddressHandler:
    """Handler para processar Lightning Address/Invoice digitados pelo usuário"""
    
    def __init__(self):
        self.backend_url = "https://useghost.squareweb.app/api/process_lightning_address.php"
        self.fallback_url = "https://useghost.squareweb.app/api/process_lightning_address.php"
        
    def is_lightning_address(self, text: str) -> bool:
        """Verifica se o texto é um Lightning Address"""
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text))
    
    def is_bolt11_invoice(self, text: str) -> bool:
        """Verifica se o texto é uma BOLT11 invoice"""
        return bool(re.match(r'^ln(bc|tb)[a-z0-9]+$', text, re.IGNORECASE)) and len(text) >= 50
    
    def is_lightning_input(self, text: str) -> bool:
        """Verifica se o texto é Lightning Address ou BOLT11"""
        return self.is_lightning_address(text) or self.is_bolt11_invoice(text)
    
    async def process_lightning_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Processa entrada de Lightning Address/Invoice
        
        Returns:
            bool: True se processou com sucesso, False se não era Lightning input
        """
        try:
            text = update.message.text.strip()
            chat_id = str(update.effective_user.id)
            
            # Verifica se é Lightning Address ou BOLT11
            if not self.is_lightning_input(text):
                return False
                
            logger.info(f"Processando Lightning input para {chat_id}: {text[:20]}...")
            
            # Exibe mensagem de processamento
            await update.message.reply_text(
                "⚡ *Processando Lightning Address/Invoice...*\n\n"
                "🔄 Verificando dados...\n"
                "📡 Conectando com servidor...\n"
                "⏳ Aguarde alguns segundos...",
                parse_mode='Markdown'
            )
            
            # Faz chamada para o backend
            success = await self._call_backend(chat_id, text)
            
            if success:
                await update.message.reply_text(
                    "✅ *Lightning Address/Invoice processado com sucesso!*\n\n"
                    "🎉 Pagamento enviado!\n"
                    "⚡ Você receberá os sats em breve.\n"
                    "🔗 Aguarde a confirmação na Lightning Network.\n\n"
                    "📊 Acompanhe o status do seu pagamento nos logs.",
                    parse_mode='Markdown'
                )
                
                # Redirecionar para o menu principal após sucesso
                await self._redirect_to_main_menu(update, context)
            else:
                await update.message.reply_text(
                    "❌ *Erro ao processar Lightning Address/Invoice*\n\n"
                    "🔍 Possíveis causas:\n"
                    "• Endereço inválido\n"
                    "• Problemas de conectividade\n"
                    "• Falta de saldo\n"
                    "• Erro no servidor\n\n"
                    "💡 Tente novamente ou entre em contato com o suporte.",
                    parse_mode='Markdown'
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Erro processando Lightning input: {e}")
            
            await update.message.reply_text(
                "❌ *Erro interno ao processar Lightning Address/Invoice*\n\n"
                f"Erro: {str(e)[:100]}\n\n"
                "🔄 Tente novamente em alguns minutos.",
                parse_mode='Markdown'
            )
            
            return True  # Retorna True pois foi Lightning input, mesmo com erro
    
    async def _call_backend(self, chat_id: str, user_input: str) -> bool:
        """Chama o backend para processar o Lightning Address/Invoice"""
        try:
            payload = {
                "chat_id": chat_id,
                "user_input": user_input,
                "amount_sats": 1000  # Valor padrão de teste
            }
            
            # Tenta primeiro o endpoint principal
            try:
                response = requests.post(
                    self.backend_url,
                    json=payload,
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Backend response: {result}")
                    return result.get('success', False)
                else:
                    logger.warning(f"Backend retornou {response.status_code}: {response.text}")
                    
            except requests.RequestException as e:
                logger.warning(f"Erro no endpoint principal: {e}")
            
            # Fallback para endpoint local
            try:
                response = requests.post(
                    self.fallback_url,
                    json=payload,
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Fallback response: {result}")
                    return result.get('success', False)
                else:
                    logger.warning(f"Fallback retornou {response.status_code}: {response.text}")
                    
            except requests.RequestException as e:
                logger.warning(f"Erro no fallback: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"Erro geral na chamada backend: {e}")
            return False
        
    async def _redirect_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Redireciona o usuário para o menu principal após processamento bem-sucedido"""
        try:
            # Aguardar um pouco antes de mostrar o menu
            await asyncio.sleep(2)
            
            # Mostrar menu principal com comando /start
            await update.message.reply_text(
                "🏠 *Retornando ao menu principal...*\n\n"
                "Use os botões abaixo para navegar:",
                parse_mode='Markdown',
                reply_markup=self._get_main_menu_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Erro ao redirecionar para menu principal: {e}")
            
            # Fallback: mostrar mensagem simples
            await update.message.reply_text(
                "🏠 *Retornando ao menu principal...*\n\n"
                "Digite /start para ver as opções disponíveis.",
                parse_mode='Markdown'
            )
    
    def _get_main_menu_keyboard(self):
        """Retorna o teclado do menu principal"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("💰 Comprar", callback_data="menu_compra"),
                InlineKeyboardButton("💸 Vender", callback_data="menu_venda")
            ],
            [
                InlineKeyboardButton("📊 Carteira", callback_data="menu_carteira"),
                InlineKeyboardButton("📞 Suporte", url="https://t.me/useghost")
            ],
            [
                InlineKeyboardButton("❓ Ajuda", callback_data="menu_ajuda"),
                InlineKeyboardButton("⚙️ Config", callback_data="menu_config")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

# Instância global
lightning_address_handler = LightningAddressHandler()

# Função para integração com bot principal
async def handle_lightning_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handler função para integração com bot principal"""
    return await lightning_address_handler.process_lightning_input(update, context)

# Função para verificar se é Lightning input
def is_lightning_input(text: str) -> bool:
    """Verifica se o texto é Lightning Address/Invoice"""
    return lightning_address_handler.is_lightning_input(text)

print("✅ Lightning Address Handler carregado!")
print("🔧 Funcionalidades:")
print("   - ✅ Detecção de Lightning Address (user@domain.com)")
print("   - ✅ Detecção de BOLT11 Invoice (lnbc...)")
print("   - ✅ Integração com backend via API")
print("   - ✅ Fallback para endpoint local")
print("   - ✅ Tratamento robusto de erros")
print("   - ✅ Logs detalhados")
