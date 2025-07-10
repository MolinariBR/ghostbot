#!/usr/bin/env python3
"""
Módulo de Redirecionamentos Automáticos
Gerencia redirecionamentos para @GhosttP2P conforme as regras de negócio.
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class RedirecionamentoManager:
    """
    Gerencia redirecionamentos automáticos para @GhosttP2P.
    """
    
    CONTATO_SUPORTE = "@GhosttP2P"
    
    @staticmethod
    async def redirecionar_venda(update: Update, context) -> None:
        """
        Redireciona usuário para venda via @GhosttP2P.
        
        Args:
            update: Update do Telegram
            context: Context do bot
        """
        try:
            mensagem = (
                "💱 *VENDA DE CRIPTOMOEDAS*\n\n"
                "🔄 Para vender suas criptomoedas, entre em contato com nosso suporte:\n\n"
                f"👤 {RedirecionamentoManager.CONTATO_SUPORTE}\n\n"
                "🎯 *Nossa equipe irá ajudá-lo com:*\n"
                "• Cotação em tempo real\n"
                "• Processo de venda seguro\n"
                "• Suporte personalizado\n\n"
                "⚡ *Resposta rápida garantida!*"
            )
            
            await update.message.reply_text(
                mensagem,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Redirecionamento de venda para usuário {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao redirecionar venda: {e}")
            await update.message.reply_text(
                "❌ Erro interno. Contate o suporte: @GhosttP2P"
            )
    
    @staticmethod
    async def redirecionar_ted_boleto(update: Update, context) -> None:
        """
        Redireciona usuário para TED/Boleto via @GhosttP2P.
        
        Args:
            update: Update do Telegram
            context: Context do bot
        """
        try:
            mensagem = (
                "🏦 *PAGAMENTO VIA TED/BOLETO*\n\n"
                "🔄 Para pagamentos via TED ou Boleto, entre em contato com nosso suporte:\n\n"
                f"👤 {RedirecionamentoManager.CONTATO_SUPORTE}\n\n"
                "🎯 *Nossa equipe irá ajudá-lo com:*\n"
                "• Geração de boleto bancário\n"
                "• Dados para transferência TED\n"
                "• Acompanhamento do pagamento\n"
                "• Suporte especializado\n\n"
                "⚡ *Atendimento personalizado!*"
            )
            
            await update.message.reply_text(
                mensagem,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Redirecionamento TED/Boleto para usuário {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao redirecionar TED/Boleto: {e}")
            await update.message.reply_text(
                "❌ Erro interno. Contate o suporte: @GhosttP2P"
            )
    
    @staticmethod
    async def redirecionar_suporte_geral(update: Update, context, motivo: str = "suporte") -> None:
        """
        Redireciona usuário para suporte geral.
        
        Args:
            update: Update do Telegram
            context: Context do bot
            motivo: Motivo do redirecionamento
        """
        try:
            mensagem = (
                "🛠️ *SUPORTE ESPECIALIZADO*\n\n"
                f"📞 Para {motivo}, entre em contato com nosso suporte:\n\n"
                f"👤 {RedirecionamentoManager.CONTATO_SUPORTE}\n\n"
                "🎯 *Nossa equipe está pronta para ajudar!*\n"
                "• Suporte técnico\n"
                "• Dúvidas sobre transações\n"
                "• Problemas e soluções\n"
                "• Atendimento personalizado\n\n"
                "⚡ *Resposta rápida garantida!*"
            )
            
            await update.message.reply_text(
                mensagem,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Redirecionamento {motivo} para usuário {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao redirecionar {motivo}: {e}")
            await update.message.reply_text(
                "❌ Erro interno. Contate o suporte: @GhosttP2P"
            )

# Funções de conveniência
async def redirecionar_para_venda(update: Update, context):
    """Função de conveniência para redirecionamento de venda."""
    await RedirecionamentoManager.redirecionar_venda(update, context)

async def redirecionar_para_ted_boleto(update: Update, context):
    """Função de conveniência para redirecionamento de TED/Boleto."""
    await RedirecionamentoManager.redirecionar_ted_boleto(update, context)

async def redirecionar_para_suporte(update: Update, context, motivo: str = "suporte"):
    """Função de conveniência para redirecionamento de suporte."""
    await RedirecionamentoManager.redirecionar_suporte_geral(update, context, motivo)
