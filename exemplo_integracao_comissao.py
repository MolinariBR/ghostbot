#!/usr/bin/env python3
"""
Exemplo de Integração do Sistema de Comissões com o Menu de Compra
================================================================

Este exemplo demonstra como integrar o sistema de comissões ao fluxo de compra,
mostrando ao usuário as taxas aplicadas antes da confirmação da transação.
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

from limites.comissao import calcular_comissao, formatar_resumo_comissao, validar_valor_minimo
import asyncio

class MockUpdate:
    """Mock do Update do Telegram para demonstração."""
    def __init__(self, user_id=12345):
        self.effective_user = MockUser(user_id)
        self.message = MockMessage()

class MockUser:
    """Mock do User do Telegram."""
    def __init__(self, user_id):
        self.id = user_id

class MockMessage:
    """Mock da Message do Telegram."""
    async def reply_text(self, text, parse_mode=None, reply_markup=None):
        print(f"🤖 Bot responde:\n{text}\n")

class MockContext:
    """Mock do Context do Telegram."""
    def __init__(self):
        self.user_data = {}

async def demonstrar_integracao_comissao():
    """Demonstra como integrar o sistema de comissões no fluxo de compra."""
    
    print("🧪 DEMONSTRAÇÃO: Integração Sistema de Comissões")
    print("=" * 60)
    
    # Simula dados de uma compra
    compras_exemplo = [
        {'valor': 150.00, 'moeda': 'BTC', 'nome': 'Bitcoin'},
        {'valor': 750.00, 'moeda': 'BTC', 'nome': 'Bitcoin'},
        {'valor': 2000.00, 'moeda': 'BTC', 'nome': 'Bitcoin'},
        {'valor': 300.00, 'moeda': 'DEPIX', 'nome': 'Depix'},
        {'valor': 500.00, 'moeda': 'USDT', 'nome': 'Tether'},
        {'valor': 50.00, 'moeda': 'BTC', 'nome': 'Bitcoin'},  # Valor baixo
    ]
    
    update = MockUpdate(12345)
    context = MockContext()
    
    for i, compra in enumerate(compras_exemplo, 1):
        print(f"🔸 EXEMPLO {i}: Compra de {compra['nome']}")
        print("-" * 40)
        
        valor = compra['valor']
        moeda = compra['moeda']
        
        # Valida valor mínimo
        if not validar_valor_minimo(valor, moeda):
            mensagem = f"""❌ **VALOR INVÁLIDO**

💰 Valor informado: R$ {valor:.2f}
💎 Moeda: {compra['nome']} ({moeda})

⚠️ **Este valor está abaixo do mínimo permitido para {moeda}.**

Por favor, informe um valor maior e tente novamente."""
            
            await update.message.reply_text(mensagem, parse_mode='Markdown')
            continue
        
        # Calcula comissão
        resultado = calcular_comissao(valor, moeda)
        
        if resultado:
            # Formatação específica para o bot
            comissao = resultado['comissao']
            valor_liquido = resultado['valor_liquido']
            
            mensagem = f"""💰 **RESUMO DA COMPRA**

🪙 **Moeda:** {compra['nome']} ({moeda})
💵 **Valor:** R$ {valor:.2f}

📊 **Comissão:**
▸ Taxa: {comissao['percentual']:.1f}% + R$ {comissao['fixo']:.2f}
▸ **Total:** R$ {comissao['total']:.2f}

💎 **Valor Líquido:** R$ {valor_liquido:.2f}

📈 **Taxa Efetiva:** {resultado['percentual_efetivo']:.2f}%

✅ **Confirmar compra?**"""
            
            await update.message.reply_text(mensagem, parse_mode='Markdown')
            
            # Adiciona informações ao contexto para uso posterior
            context.user_data.update({
                'valor_original': valor,
                'moeda': moeda,
                'comissao_total': comissao['total'],
                'valor_liquido': valor_liquido,
                'resumo_comissao': resultado
            })
            
            print("📋 Dados salvos no contexto:")
            print(f"   • Valor original: R$ {context.user_data['valor_original']:.2f}")
            print(f"   • Comissão: R$ {context.user_data['comissao_total']:.2f}")
            print(f"   • Valor líquido: R$ {context.user_data['valor_liquido']:.2f}")
            
        else:
            mensagem = f"""❌ **ERRO NO CÁLCULO**

Não foi possível calcular a comissão para:
• Valor: R$ {valor:.2f}
• Moeda: {moeda}

Contate o suporte: @GhosttP2P"""
            
            await update.message.reply_text(mensagem, parse_mode='Markdown')
        
        print()

async def demonstrar_casos_especiais():
    """Demonstra casos especiais e tratamento de erros."""
    
    print("🔍 DEMONSTRAÇÃO: Casos Especiais")
    print("=" * 60)
    
    update = MockUpdate(12345)
    
    # Caso 1: Moeda não suportada
    resultado = calcular_comissao(100, 'ETH')
    if not resultado:
        mensagem = """❌ **MOEDA NÃO SUPORTADA**

A moeda ETH não está disponível no momento.

🪙 **Moedas disponíveis:**
• BTC (Bitcoin)
• DEPIX (Depix)
• USDT (Tether)

Escolha uma das moedas disponíveis."""
        
        await update.message.reply_text(mensagem, parse_mode='Markdown')
    
    # Caso 2: Valor muito alto para BTC
    resultado = calcular_comissao(6000, 'BTC')
    if not resultado:
        mensagem = """⚠️ **VALOR ACIMA DO LIMITE**

💰 Valor informado: R$ 6.000,00
💎 Moeda: Bitcoin (BTC)

📊 **Limite máximo para BTC:** R$ 4.999,99

Para valores maiores, entre em contato com nosso suporte:
👤 @GhosttP2P"""
        
        await update.message.reply_text(mensagem, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(demonstrar_integracao_comissao())
    asyncio.run(demonstrar_casos_especiais())
    
    print("=" * 60)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
    print()
    print("📝 PRÓXIMOS PASSOS PARA INTEGRAÇÃO:")
    print("1. Importar o módulo de comissões no menu_compra.py")
    print("2. Adicionar validação de valor mínimo antes do cálculo")
    print("3. Calcular e exibir comissão antes da confirmação")
    print("4. Salvar dados da comissão no contexto do usuário")
    print("5. Usar valor líquido para cálculos finais")
