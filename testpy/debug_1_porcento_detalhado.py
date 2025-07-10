#!/usr/bin/env python3
"""
Debug específico para o problema do 1.0% no resumo da compra.
Simula exatamente o fluxo do menu_compra.py linha por linha.
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.getcwd())

print("🔍 DEBUG: Problema 1.0% no Resumo da Compra")
print("=" * 60)

def simular_fluxo_completo():
    """Simula exatamente o que acontece na função resumo_compra."""
    
    # Simula os dados que vêm do context.user_data
    moeda_original = "₿ Bitcoin (BTC)"  # Como aparece no teclado
    rede = "⚡ Lightning"
    valor_brl = 250.0
    
    print(f"📋 Dados de entrada (simulação):")
    print(f"   • moeda original: '{moeda_original}'")
    print(f"   • rede: '{rede}'")
    print(f"   • valor_brl: {valor_brl}")
    
    # Testa o cálculo de comissão linha por linha como no código
    print(f"\n🧮 TESTE: Executando calcular_comissao")
    print("-" * 40)
    
    try:
        from limites.comissao import calcular_comissao
        
        print(f"   🔍 Chamando: calcular_comissao({valor_brl}, '{moeda_original}')")
        resultado_comissao = calcular_comissao(valor_brl, moeda_original)
        
        print(f"   📊 Resultado: {resultado_comissao}")
        
        if resultado_comissao:
            print("   ✅ Sistema de comissões FUNCIONOU!")
            
            # Extrai os valores exatamente como no código
            comissao_total = resultado_comissao['comissao']['total']
            valor_liquido = resultado_comissao['valor_liquido']
            
            # Informações da comissão
            comissao_info = resultado_comissao['comissao']
            percentual = comissao_info['percentual']
            taxa_fixa = comissao_info['fixo']
            
            print(f"      • comissao_total: {comissao_total}")
            print(f"      • valor_liquido: {valor_liquido}")
            print(f"      • percentual: {percentual}")
            print(f"      • taxa_fixa: {taxa_fixa}")
            
            print(f"\n📋 Como apareceria no resumo:")
            print(f"   Comissão: {percentual:.1f}% + R$ {taxa_fixa:.2f} = R$ {comissao_total:.2f}")
            
        else:
            print("   ❌ Sistema de comissões FALHOU!")
            print("   🚨 FALLBACK SERIA USADO:")
            
            # Simula o fallback
            taxa = 0.01  # 1% de taxa de exemplo
            comissao_total = valor_brl * taxa
            valor_liquido = valor_brl - comissao_total
            percentual = 1.0  # 1.0% (já em formato de exibição)
            taxa_fixa = 0.0
            
            print(f"      • taxa: {taxa} (1%)")
            print(f"      • comissao_total: {comissao_total}")
            print(f"      • valor_liquido: {valor_liquido}")
            print(f"      • percentual: {percentual}")
            print(f"      • taxa_fixa: {taxa_fixa}")
            
            print(f"\n📋 Como apareceria no resumo (FALLBACK):")
            print(f"   Comissão: {percentual:.1f}% + R$ {taxa_fixa:.2f} = R$ {comissao_total:.2f}")
            
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

def testar_diferentes_formatos():
    """Testa diferentes formatos de moeda para encontrar o problema."""
    print(f"\n🧪 TESTE: Diferentes formatos de moeda")
    print("-" * 40)
    
    formatos_moeda = [
        "₿ Bitcoin (BTC)",      # Como vem do teclado
        "Bitcoin (BTC)",        # Sem emoji
        "BTC",                  # Só a sigla
        "bitcoin",              # Minúsculo
        "BITCOIN",              # Maiúsculo
    ]
    
    try:
        from limites.comissao import calcular_comissao
        
        for formato in formatos_moeda:
            print(f"\n   🔍 Testando: '{formato}'")
            resultado = calcular_comissao(250.0, formato)
            
            if resultado:
                percentual = resultado['comissao']['percentual']
                print(f"      ✅ Funcionou: {percentual}%")
            else:
                print(f"      ❌ Falhou: None")
                
    except Exception as e:
        print(f"   ❌ ERRO: {e}")

def verificar_regras_comissao():
    """Verifica as regras de comissão diretamente."""
    print(f"\n🔍 TESTE: Verificando regras de comissão")
    print("-" * 40)
    
    try:
        from limites.comissao import ComissaoCalculator
        
        regras = ComissaoCalculator.REGRAS_COMISSAO
        print(f"   📊 Moedas disponíveis: {list(regras.keys())}")
        
        for moeda, regra_list in regras.items():
            print(f"\n   💰 {moeda}:")
            for i, regra in enumerate(regra_list):
                print(f"      Faixa {i+1}: R$ {regra['min']} - {regra['max'] or 'sem limite'}")
                print(f"      Percentual: {regra['percentual'] * 100}%")
                print(f"      Fixo: R$ {regra['fixo']}")
                
    except Exception as e:
        print(f"   ❌ ERRO: {e}")

def simular_deteccao_moeda():
    """Simula como a moeda é detectada no código."""
    print(f"\n🔧 TESTE: Simulando detecção de moeda")
    print("-" * 40)
    
    moeda_input = "₿ Bitcoin (BTC)"
    
    # Como o código pode estar processando
    moeda_upper = moeda_input.upper()
    print(f"   📝 moeda_input: '{moeda_input}'")
    print(f"   📝 moeda_upper: '{moeda_upper}'")
    
    # Testa diferentes condições
    if "BTC" in moeda_upper:
        print(f"   ✅ 'BTC' encontrado em '{moeda_upper}'")
        moeda_detectada = "BTC"
    elif "USDT" in moeda_upper:
        print(f"   ✅ 'USDT' encontrado em '{moeda_upper}'")
        moeda_detectada = "USDT"
    elif "DEPIX" in moeda_upper:
        print(f"   ✅ 'DEPIX' encontrado em '{moeda_upper}'")
        moeda_detectada = "DEPIX"
    else:
        print(f"   ❌ Nenhuma moeda detectada em '{moeda_upper}'")
        moeda_detectada = None
    
    print(f"   🎯 Moeda detectada: '{moeda_detectada}'")
    
    return moeda_detectada

if __name__ == "__main__":
    simular_fluxo_completo()
    testar_diferentes_formatos()
    verificar_regras_comissao()
    simular_deteccao_moeda()
    
    print(f"\n🎯 CONCLUSÃO:")
    print("=" * 60)
    print("Se ainda aparece 1.0%, o problema pode ser:")
    print("1. 🔄 Bot não recarregou o código novo")
    print("2. 💾 Cache do sistema ou Telegram")
    print("3. 🚨 Alguma condição específica não testada")
    print("4. 📱 Interface não atualizada")
