#!/usr/bin/env python3
"""
Debug do Resumo da Compra - Verificar problema do 1.0%
"""

import sys
sys.path.append('/home/mau/bot/ghost')

def debug_resumo_compra():
    """Debuga o problema do resumo da compra mostrando 1.0% em vez de 10%"""
    
    print("🔍 DEBUG: Problema 1.0% vs 10% no Resumo da Compra")
    print("=" * 60)
    
    # Simula os dados do usuário
    valor_brl = 250.00
    moeda = 'BTC'
    
    print(f"📋 Dados de entrada:")
    print(f"   • Valor: R$ {valor_brl:.2f}")
    print(f"   • Moeda: {moeda}")
    
    # Teste 1: Sistema de comissões diretamente
    print(f"\n🧪 TESTE 1: Sistema de Comissões Direto")
    print("-" * 40)
    
    try:
        from limites.comissao import calcular_comissao
        resultado_comissao = calcular_comissao(valor_brl, moeda)
        
        if resultado_comissao:
            print("✅ Sistema de comissões funcionando!")
            comissao_info = resultado_comissao['comissao']
            percentual = comissao_info['percentual']
            taxa_fixa = comissao_info['fixo']
            comissao_total = comissao_info['total']
            
            print(f"   • Percentual: {percentual:.1f}%")
            print(f"   • Taxa fixa: R$ {taxa_fixa:.2f}")
            print(f"   • Total: R$ {comissao_total:.2f}")
            
            # Simula linha do resumo
            print(f"\n📋 Como aparece no resumo:")
            print(f"   • Comissão: {percentual:.1f}% + R$ {taxa_fixa:.2f} = R$ {comissao_total:.2f}")
            
        else:
            print("❌ Sistema de comissões falhou!")
            print("🔧 Usando fallback:")
            taxa = 0.01  # 1%
            comissao_total = valor_brl * taxa
            percentual = 1.0  # 1.0%
            taxa_fixa = 0.0
            
            print(f"   • Percentual: {percentual:.1f}%")
            print(f"   • Taxa fixa: R$ {taxa_fixa:.2f}")
            print(f"   • Total: R$ {comissao_total:.2f}")
            
            print(f"\n📋 Como aparece no resumo (FALLBACK):")
            print(f"   • Comissão: {percentual:.1f}% + R$ {taxa_fixa:.2f} = R$ {comissao_total:.2f}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    # Teste 2: Verificar se o import está funcionando no contexto do menu
    print(f"\n🧪 TESTE 2: Import no Contexto do Menu")
    print("-" * 40)
    
    try:
        # Simula exatamente como está no menu_compra.py
        from limites.comissao import calcular_comissao
        
        resultado_comissao = calcular_comissao(valor_brl, moeda)
        
        if resultado_comissao:
            comissao_total = resultado_comissao['comissao']['total']
            comissao_info = resultado_comissao['comissao']
            percentual = comissao_info['percentual']
            taxa_fixa = comissao_info['fixo']
            print(f"✅ Import funcionando - Percentual: {percentual:.1f}%")
        else:
            print("❌ Import falhou - usando fallback")
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
    except Exception as e:
        print(f"❌ Outro erro: {e}")
    
    # Teste 3: Verificar valores das regras
    print(f"\n🧪 TESTE 3: Verificar Regras de Comissão")
    print("-" * 40)
    
    try:
        from limites.comissao import ComissaoCalculator
        
        regras_btc = ComissaoCalculator.REGRAS_COMISSAO['BTC']
        primeira_regra = regras_btc[0]
        
        print(f"✅ Primeira regra BTC:")
        print(f"   • Min: R$ {primeira_regra['min']}")
        print(f"   • Max: R$ {primeira_regra['max']}")
        print(f"   • Percentual: {primeira_regra['percentual']} ({float(primeira_regra['percentual'] * 100):.1f}%)")
        print(f"   • Fixo: R$ {primeira_regra['fixo']}")
        
        # Verificar se R$ 250 está na faixa
        from decimal import Decimal
        valor_decimal = Decimal(str(valor_brl))
        min_val = primeira_regra['min']
        max_val = primeira_regra['max']
        
        if valor_decimal >= min_val and valor_decimal <= max_val:
            print(f"✅ R$ {valor_brl} está na primeira faixa (10%)")
        else:
            print(f"❌ R$ {valor_brl} NÃO está na primeira faixa")
            
    except Exception as e:
        print(f"❌ Erro ao verificar regras: {e}")
    
    print(f"\n🎯 CONCLUSÃO:")
    print("=" * 60)
    print("Se você está vendo 1.0% no bot, pode ser:")
    print("1. 🔄 Bot não recarregou o código (reinicie)")
    print("2. 💾 Cache do Telegram/app")
    print("3. 🚨 Sistema de comissão falhando (usando fallback)")
    print("4. 📱 Instância antiga do bot rodando")

if __name__ == "__main__":
    debug_resumo_compra()
