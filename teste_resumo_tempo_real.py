#!/usr/bin/env python3
"""
Teste específico para verificar o resumo da compra em tempo real
com o bot rodando.
"""

import sys
import os
import asyncio
import logging

# Adicionar o diretório atual ao path
sys.path.insert(0, os.getcwd())

# Configurar logging
logging.basicConfig(level=logging.INFO)

async def testar_resumo_compra():
    """Simula exatamente o que acontece no resumo da compra."""
    print("🧪 TESTE: Simulação do Resumo da Compra")
    print("=" * 50)
    
    # Simula context.user_data
    context_data = {
        'moeda': '₿ Bitcoin (BTC)',
        'rede': '⚡ Lightning',
        'valor_brl': 250.0,
        'cpf': '12345678901'
    }
    
    print(f"📋 Dados simulados:")
    print(f"   • Moeda: {context_data['moeda']}")
    print(f"   • Rede: {context_data['rede']}")
    print(f"   • Valor: R$ {context_data['valor_brl']}")
    
    # Importa e testa a cotação
    try:
        from api.cotacao import get_btc_price_brl
        cotacao = float(get_btc_price_brl())
        print(f"   • Cotação BTC: R$ {cotacao:,.2f}")
    except Exception as e:
        print(f"   ⚠️ Erro na cotação, usando fallback: {e}")
        cotacao = 350000.0
    
    # Testa o sistema de comissões
    print(f"\n🧮 TESTE: Sistema de Comissões")
    print("-" * 30)
    
    try:
        from limites.comissao import calcular_comissao
        
        moeda_upper = context_data['moeda'].upper()
        if 'BTC' in moeda_upper:
            moeda_calc = 'BTC'
        elif 'USDT' in moeda_upper:
            moeda_calc = 'USDT'
        elif 'DEPIX' in moeda_upper:
            moeda_calc = 'DEPIX'
        else:
            moeda_calc = 'BTC'
        
        print(f"   🔍 Calculando para: {moeda_calc}")
        resultado_comissao = calcular_comissao(context_data['valor_brl'], moeda_calc)
        
        if resultado_comissao:
            print("   ✅ Sistema de comissões funcionou:")
            comissao_info = resultado_comissao['comissao']
            percentual = comissao_info['percentual']
            taxa_fixa = comissao_info['fixo']
            comissao_total = comissao_info['total']
            valor_liquido = resultado_comissao['valor_liquido']
            
            print(f"      • Percentual: {percentual}%")
            print(f"      • Taxa fixa: R$ {taxa_fixa}")
            print(f"      • Comissão total: R$ {comissao_total}")
            print(f"      • Valor líquido: R$ {valor_liquido}")
            
            # Simula o que aparece no resumo
            valor_recebido = valor_liquido / cotacao
            
            # Formata igual ao menu_compra.py
            def formatar_brl(valor: float) -> str:
                return f"R$ {valor:,.2f}".replace(".", "v").replace(",", ".").replace("v", ",")
            
            def formatar_cripto(valor: float, moeda: str) -> str:
                if "BTC" in moeda.upper():
                    return f"{valor:.8f} {moeda.split()[0].strip()}"
                elif "USDT" in moeda.upper():
                    return f"{valor:,.2f} {moeda.split()[0].strip()}"
                else:
                    return f"{valor:,.2f} {moeda.split()[0].strip()}"
            
            valor_brl_formatado = formatar_brl(context_data['valor_brl'])
            valor_recebido_formatado = formatar_cripto(valor_recebido, context_data['moeda'])
            comissao_formatada = formatar_brl(comissao_total)
            cotacao_formatada = formatar_brl(cotacao)
            
            # Taxa do parceiro (simulando PIX)
            taxa_parceiro_info = "R$ 1,00"
            
            print(f"\n📋 RESUMO COMO APARECE NO BOT:")
            print("=" * 50)
            
            mensagem = (
                f"📋 *RESUMO DA COMPRA*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"• *Moeda:* {context_data['moeda']}\n"
                f"• *Rede:* {context_data['rede']}\n"
                f"• *Valor Investido:* {valor_brl_formatado}\n"
                f"• *Parceiro:* {taxa_parceiro_info}\n"
                f"• *Comissão:* {percentual:.1f}% + R$ {taxa_fixa:.2f} = {comissao_formatada}\n"
                f"• *Cotação:* {cotacao_formatada}\n"
                f"• *Você receberá:* {valor_recebido_formatado}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
            )
            
            print(mensagem)
            
        else:
            print("   ❌ FALLBACK SERIA USADO!")
            print("   📊 Resumo exibiria: 1.0% + R$ 0.00")
            
            # Simula o fallback
            taxa = 0.01  # 1% de taxa de exemplo
            comissao_total = context_data['valor_brl'] * taxa
            valor_liquido = context_data['valor_brl'] - comissao_total
            valor_recebido = valor_liquido / cotacao
            percentual = 1.0  # 1.0% (já em formato de exibição)
            taxa_fixa = 0.0
            
            print(f"\n❌ FALLBACK - RESUMO COMO APARECERIA:")
            print("=" * 50)
            
            mensagem_fallback = (
                f"📋 *RESUMO DA COMPRA*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"• *Moeda:* {context_data['moeda']}\n"
                f"• *Rede:* {context_data['rede']}\n"
                f"• *Valor Investido:* R$ {context_data['valor_brl']:,.2f}\n"
                f"• *Parceiro:* R$ 1,00\n"
                f"• *Comissão:* {percentual:.1f}% + R$ {taxa_fixa:.2f} = R$ {comissao_total:.2f}\n"
                f"• *Cotação:* R$ {cotacao:,.2f}\n"
                f"• *Você receberá:* {valor_recebido:.8f} BTC\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
            )
            
            print(mensagem_fallback)
            
    except Exception as e:
        print(f"   ❌ Erro no sistema de comissões: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(testar_resumo_compra())
