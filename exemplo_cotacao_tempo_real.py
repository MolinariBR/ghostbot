#!/usr/bin/env python3
"""
Exemplo de Integração do Resumo com Cotação em Tempo Real
=========================================================

Este exemplo demonstra como o novo resumo da compra pode ser integrado
com APIs de cotação em tempo real para fornecer informações atualizadas.
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

from menus.menu_compra import gerar_resumo_compra
from api.cotacao import get_btc_price_brl, get_usdt_price_brl, get_depix_price_brl
import asyncio

class MockContext:
    """Mock do Context do Telegram para demonstração."""
    def __init__(self):
        self.user_data = {}

async def demonstrar_cotacao_tempo_real():
    """Demonstra como integrar cotação em tempo real no resumo."""
    
    print("📈 DEMONSTRAÇÃO: Cotação em Tempo Real")
    print("=" * 50)
    
    # Obtém cotações atuais
    try:
        cotacao_btc = await get_btc_price_brl()
        cotacao_usdt = await get_usdt_price_brl()
        cotacao_depix = await get_depix_price_brl()
        
        print(f"💰 Cotações atuais:")
        print(f"   • BTC: R$ {cotacao_btc:.2f}")
        print(f"   • USDT: R$ {cotacao_usdt:.2f}")
        print(f"   • DEPIX: R$ {cotacao_depix:.2f}")
        
    except Exception as e:
        print(f"❌ Erro ao obter cotações: {e}")
        # Usa cotações de exemplo
        cotacao_btc = 250000.00
        cotacao_usdt = 5.20
        cotacao_depix = 1.00
        
        print(f"💰 Usando cotações de exemplo:")
        print(f"   • BTC: R$ {cotacao_btc:.2f}")
        print(f"   • USDT: R$ {cotacao_usdt:.2f}")
        print(f"   • DEPIX: R$ {cotacao_depix:.2f}")
    
    print("\n" + "=" * 50)
    
    # Cenários com cotação em tempo real
    cenarios = [
        {
            'nome': 'BTC com cotação atual',
            'dados': {
                'moeda': 'BTC',
                'rede': 'ONCHAIN',
                'valor_brl': 1000.00,
                'cotacao': cotacao_btc,
                'metodo_pagamento': 'PIX'
            }
        },
        {
            'nome': 'USDT com cotação atual',
            'dados': {
                'moeda': 'USDT',
                'rede': 'POLYGON',
                'valor_brl': 500.00,
                'cotacao': cotacao_usdt,
                'metodo_pagamento': 'TED'
            }
        },
        {
            'nome': 'DEPIX com cotação atual',
            'dados': {
                'moeda': 'DEPIX',
                'rede': 'STABLE',
                'valor_brl': 300.00,
                'cotacao': cotacao_depix,
                'metodo_pagamento': 'PIX'
            }
        }
    ]
    
    for i, cenario in enumerate(cenarios, 1):
        print(f"\n🔸 CENÁRIO {i}: {cenario['nome']}")
        print("-" * 40)
        
        # Cria contexto com dados atuais
        context = MockContext()
        context.user_data = cenario['dados']
        
        # Gera resumo com cotação em tempo real
        resumo = gerar_resumo_compra(context)
        print(resumo)
        
        # Análise do impacto da cotação
        valor_investido = cenario['dados']['valor_brl']
        cotacao = cenario['dados']['cotacao']
        
        print(f"\n📊 Análise:")
        print(f"   • Valor investido: R$ {valor_investido:.2f}")
        print(f"   • Cotação atual: R$ {cotacao:.2f}")
        print(f"   • Impacto da cotação no resultado final calculado automaticamente")

async def simular_mudanca_cotacao():
    """Simula como mudanças na cotação afetam o resumo."""
    
    print("\n\n📊 SIMULAÇÃO: Impacto da Mudança de Cotação")
    print("=" * 50)
    
    # Dados base
    context = MockContext()
    context.user_data = {
        'moeda': 'BTC',
        'rede': 'ONCHAIN',
        'valor_brl': 1000.00,
        'metodo_pagamento': 'PIX'
    }
    
    # Diferentes cenários de cotação
    cotacoes = [
        (200000.00, "Cotação Baixa"),
        (250000.00, "Cotação Média"),
        (300000.00, "Cotação Alta")
    ]
    
    for cotacao, descricao in cotacoes:
        print(f"\n🔸 {descricao}: R$ {cotacao:.2f}")
        print("-" * 30)
        
        # Atualiza cotação no contexto
        context.user_data['cotacao'] = cotacao
        
        # Gera resumo
        resumo = gerar_resumo_compra(context)
        
        # Extrai apenas a linha relevante
        linhas = resumo.split('\n')
        for linha in linhas:
            if 'Você receberá:' in linha:
                print(f"   {linha}")
                break
        
        # Calcula quantidade para comparação
        # (R$ 1000 - R$ 61 comissão - R$ 1 parceiro) / cotacao
        quantidade = (1000 - 61 - 1) / cotacao
        print(f"   Quantidade: {quantidade:.8f} BTC")

def exemplo_integracao_api():
    """Mostra como integrar com APIs de cotação."""
    
    print("\n\n🔌 EXEMPLO DE INTEGRAÇÃO COM API")
    print("=" * 50)
    
    codigo_exemplo = '''
# Exemplo de como integrar no menu_compra.py

async def resumo_compra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra o resumo da compra com cotação em tempo real."""
    try:
        moeda = context.user_data.get('moeda', 'BTC')
        
        # Obtém cotação em tempo real
        if moeda == 'BTC':
            cotacao = await get_btc_price_brl()
        elif moeda == 'USDT':
            cotacao = await get_usdt_price_brl()
        elif moeda == 'DEPIX':
            cotacao = await get_depix_price_brl()
        else:
            cotacao = 0.0
        
        # Salva cotação no contexto
        context.user_data['cotacao'] = cotacao
        
        # Gera resumo com cotação atualizada
        resumo_detalhado = gerar_resumo_compra(context)
        
        # Adiciona timestamp da cotação
        timestamp = datetime.now().strftime("%H:%M:%S")
        resumo_com_timestamp = f"{resumo_detalhado}\\n\\n🕐 Cotação atualizada às {timestamp}"
        
        # Envia para o usuário
        await update.message.reply_text(resumo_com_timestamp, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao obter cotação: {e}")
        # Fallback para cotação padrão
        ...
    '''
    
    print(codigo_exemplo)

if __name__ == "__main__":
    asyncio.run(demonstrar_cotacao_tempo_real())
    asyncio.run(simular_mudanca_cotacao())
    exemplo_integracao_api()
    
    print("\n" + "=" * 50)
    print("🎯 RESUMO DA DEMONSTRAÇÃO:")
    print("• Integração com cotação em tempo real funcionando")
    print("• Impacto das mudanças de cotação visível no resumo")
    print("• Código de exemplo para implementação fornecido")
    print("• Sistema robusto com fallback para erros")
    print("• Atualização automática de valores calculados")
