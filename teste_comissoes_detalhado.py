#!/usr/bin/env python3
"""
Teste Específico do Sistema de Comissões
Verifica limites exatos das faixas e casos especiais
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

from limites.comissao import calcular_comissao, obter_faixas_moeda, validar_valor_minimo, obter_valor_minimo

def teste_faixas_btc():
    """Testa as faixas específicas do BTC."""
    print("🪙 TESTE BTC - Faixas Específicas")
    print("-" * 40)
    
    # Testa os limites exatos das faixas
    valores_teste = [
        (9.99, "Abaixo do mínimo"),
        (10.00, "Limite inferior faixa 1"),
        (500.00, "Limite superior faixa 1"),
        (500.01, "Limite inferior faixa 2"),
        (1000.00, "Limite superior faixa 2"),
        (1000.01, "Limite inferior faixa 3"),
        (4999.99, "Limite superior faixa 3"),
        (5000.00, "Acima do máximo"),
    ]
    
    for valor, descricao in valores_teste:
        resultado = calcular_comissao(valor, 'BTC')
        if resultado:
            comissao = resultado['comissao']
            print(f"R$ {valor:8.2f} ({descricao:22}): {comissao['percentual']:4.1f}% + R${comissao['fixo']:5.2f} = R${comissao['total']:6.2f}")
        else:
            print(f"R$ {valor:8.2f} ({descricao:22}): ❌ Fora das faixas")
    
    print()

def teste_faixas_stablecoins():
    """Testa as faixas das stablecoins (DEPIX e USDT)."""
    print("💳 TESTE STABLECOINS - Faixas Específicas")
    print("-" * 40)
    
    for moeda in ['DEPIX', 'USDT']:
        print(f"\n🔸 {moeda}:")
        valores_teste = [
            (99.99, "Abaixo do mínimo"),
            (100.00, "Valor mínimo"),
            (500.00, "Valor médio"),
            (10000.00, "Valor alto"),
        ]
        
        for valor, descricao in valores_teste:
            resultado = calcular_comissao(valor, moeda)
            if resultado:
                comissao = resultado['comissao']
                print(f"  R$ {valor:8.2f} ({descricao:15}): {comissao['percentual']:4.1f}% + R${comissao['fixo']:5.2f} = R${comissao['total']:6.2f}")
            else:
                print(f"  R$ {valor:8.2f} ({descricao:15}): ❌ Fora das faixas")

def teste_valores_minimos():
    """Testa os valores mínimos por moeda."""
    print("\n💰 TESTE VALORES MÍNIMOS")
    print("-" * 40)
    
    for moeda in ['BTC', 'DEPIX', 'USDT']:
        minimo = obter_valor_minimo(moeda)
        print(f"{moeda:5}: R$ {minimo:8.2f}")
        
        # Testa validação
        valido_abaixo = validar_valor_minimo(minimo - 0.01, moeda)
        valido_exato = validar_valor_minimo(minimo, moeda)
        
        print(f"      Validação R$ {minimo-0.01:6.2f}: {'✅' if valido_abaixo else '❌'}")
        print(f"      Validação R$ {minimo:6.2f}: {'✅' if valido_exato else '❌'}")

def teste_informacoes_faixas():
    """Mostra informações detalhadas das faixas."""
    print("\n📊 INFORMAÇÕES DAS FAIXAS")
    print("-" * 40)
    
    for moeda in ['BTC', 'DEPIX', 'USDT']:
        print(f"\n🔸 {moeda}:")
        faixas = obter_faixas_moeda(moeda)
        
        for i, faixa in enumerate(faixas, 1):
            min_val = faixa['min']
            max_val = faixa['max']
            percentual = faixa['percentual']
            fixo = faixa['fixo']
            
            if max_val:
                range_str = f"R$ {min_val:8.2f} a R$ {max_val:8.2f}"
            else:
                range_str = f"R$ {min_val:8.2f} ou mais"
            
            print(f"  Faixa {i}: {range_str} - {percentual:4.1f}% + R$ {fixo:5.2f}")

if __name__ == "__main__":
    print("🧪 TESTE DETALHADO DO SISTEMA DE COMISSÕES")
    print("=" * 50)
    
    teste_faixas_btc()
    teste_faixas_stablecoins()
    teste_valores_minimos()
    teste_informacoes_faixas()
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes concluídos!")
