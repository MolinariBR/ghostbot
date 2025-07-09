#!/usr/bin/env python3
"""
Debug específico da comissão BTC
"""

import sys
sys.path.append('/home/mau/bot/ghost')

def debug_comissao_btc():
    """Debug da comissão BTC"""
    
    print("🔍 DEBUG COMISSÃO BTC")
    print("=" * 40)
    
    try:
        from limites.comissao import ComissaoCalculator, calcular_comissao
        
        # Teste direto com a classe
        print("\n📊 TESTE DIRETO COM CLASSE:")
        print("-" * 30)
        
        calc = ComissaoCalculator()
        regras = calc.REGRAS_COMISSAO['BTC']
        
        print("Regras BTC configuradas:")
        for i, regra in enumerate(regras, 1):
            print(f"  Faixa {i}:")
            print(f"    Min: R$ {regra['min']}")
            print(f"    Max: R$ {regra['max']}")
            print(f"    Percentual: {regra['percentual']} ({float(regra['percentual'] * 100)}%)")
            print(f"    Fixo: R$ {regra['fixo']}")
        
        # Teste com valor específico
        print(f"\n🧪 TESTE COM R$ 250,00:")
        print("-" * 30)
        
        resultado = calcular_comissao(250.00, 'BTC')
        
        if resultado:
            print(f"✅ Resultado encontrado:")
            print(f"  Valor original: R$ {resultado['valor_original']:.2f}")
            print(f"  Moeda: {resultado['moeda']}")
            print(f"  Faixa aplicada:")
            print(f"    Min: R$ {resultado['faixa']['min']:.2f}")
            print(f"    Max: R$ {resultado['faixa']['max']:.2f}")
            print(f"  Comissão:")
            print(f"    Percentual configurado: {resultado['comissao']['percentual']:.1f}%")
            print(f"    Valor percentual: R$ {resultado['comissao']['percentual_valor']:.2f}")
            print(f"    Valor fixo: R$ {resultado['comissao']['fixo']:.2f}")
            print(f"    Total: R$ {resultado['comissao']['total']:.2f}")
            print(f"  Valor líquido: R$ {resultado['valor_liquido']:.2f}")
            print(f"  Taxa efetiva: {resultado['percentual_efetivo']:.2f}%")
            
            # Verificação manual
            print(f"\n🔢 VERIFICAÇÃO MANUAL:")
            print("-" * 30)
            from decimal import Decimal
            valor = Decimal('250.00')
            percentual = Decimal('0.10')  # 10%
            fixo = Decimal('1.00')
            
            comissao_calc = valor * percentual
            total_calc = comissao_calc + fixo
            
            print(f"  R$ 250,00 × 10% = R$ {float(comissao_calc):.2f}")
            print(f"  R$ {float(comissao_calc):.2f} + R$ 1,00 = R$ {float(total_calc):.2f}")
            
            if float(total_calc) == resultado['comissao']['total']:
                print("  ✅ Cálculo está correto!")
            else:
                print("  ❌ Diferença encontrada!")
                
        else:
            print("❌ Nenhum resultado encontrado")
            
        # Teste com outros valores BTC
        print(f"\n🧪 TESTE COM OUTROS VALORES BTC:")
        print("-" * 40)
        
        valores_teste = [50, 100, 500, 600, 1200]
        
        for valor in valores_teste:
            resultado = calcular_comissao(valor, 'BTC')
            if resultado:
                print(f"  R$ {valor:>6.2f} → {resultado['comissao']['percentual']:>4.1f}% + R$ {resultado['comissao']['fixo']:>4.2f} = R$ {resultado['comissao']['total']:>6.2f}")
            else:
                print(f"  R$ {valor:>6.2f} → Fora das faixas")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_comissao_btc()
