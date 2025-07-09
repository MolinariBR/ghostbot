#!/usr/bin/env python3
"""
Script para detectar quando o fallback de comissão está sendo usado
e investigar se há algum problema no sistema de comissões.
"""

import sys
import os
import logging

# Configurar logging para capturar warnings
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s:%(name)s:%(message)s'
)

# Adicionar o diretório atual ao path
sys.path.insert(0, os.getcwd())

print("🔍 DEBUG: Detectando uso do fallback de comissão")
print("=" * 60)

def testar_sistema_comissao():
    """Testa o sistema de comissão para detectar falhas."""
    print("\n📋 TESTE 1: Importação do sistema de comissões")
    print("-" * 40)
    
    try:
        from limites.comissao import calcular_comissao
        print("✅ Import bem-sucedido")
    except Exception as e:
        print(f"❌ Erro no import: {e}")
        return False
    
    # Testa diferentes cenários
    cenarios = [
        {"valor": 100, "moeda": "BTC", "esperado": "10%"},
        {"valor": 250, "moeda": "BTC", "esperado": "10%"},
        {"valor": 600, "moeda": "BTC", "esperado": "6%"},
        {"valor": 100, "moeda": "DEPIX", "esperado": "1.9%"},
        {"valor": 100, "moeda": "USDT", "esperado": "1.9%"},
    ]
    
    print("\n📋 TESTE 2: Cenários de comissão")
    print("-" * 40)
    
    for i, cenario in enumerate(cenarios, 1):
        valor = cenario["valor"]
        moeda = cenario["moeda"]
        esperado = cenario["esperado"]
        
        print(f"\n🧪 Cenário {i}: R$ {valor} em {moeda}")
        
        resultado = calcular_comissao(valor, moeda)
        
        if resultado:
            percentual = resultado['comissao']['percentual']
            print(f"   ✅ Resultado: {percentual}% (esperado: {esperado})")
        else:
            print(f"   ❌ Falhou! Retornou None (fallback seria usado)")
    
    return True

def simular_resumo_compra():
    """Simula o fluxo do resumo da compra para detectar uso do fallback."""
    print("\n📋 TESTE 3: Simulação do resumo da compra")
    print("-" * 40)
    
    # Simula o que acontece na função resumo_compra
    valor_brl = 250
    moeda = "BTC"
    
    print(f"   💰 Valor: R$ {valor_brl}")
    print(f"   🪙 Moeda: {moeda}")
    
    try:
        from limites.comissao import calcular_comissao
        
        # Captura warnings para detectar fallback
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            resultado_comissao = calcular_comissao(valor_brl, moeda)
            
            if resultado_comissao:
                # Usa os valores calculados pelo sistema de comissões
                comissao_info = resultado_comissao['comissao']
                percentual = comissao_info['percentual']
                taxa_fixa = comissao_info['fixo']
                
                print(f"   ✅ Sistema funcionou:")
                print(f"      • Percentual: {percentual}%")
                print(f"      • Taxa fixa: R$ {taxa_fixa}")
                print(f"   📊 Resumo exibiria: {percentual:.1f}% + R$ {taxa_fixa:.2f}")
                
                if len(w) > 0:
                    print(f"   ⚠️ Warnings capturados: {len(w)}")
                    for warning in w:
                        print(f"      - {warning.message}")
                        
            else:
                # Fallback seria usado
                print("   ❌ FALLBACK SERIA USADO!")
                print("   📊 Resumo exibiria: 1.0% + R$ 0.00")
                
    except Exception as e:
        print(f"   ❌ Erro na simulação: {e}")

def verificar_logs_warning():
    """Verifica se há logs de warning do fallback."""
    print("\n📋 TESTE 4: Verificando logs de warning")
    print("-" * 40)
    
    # Captura logs em tempo real
    import logging
    from io import StringIO
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.WARNING)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    
    # Simula o cálculo novamente
    try:
        from limites.comissao import calcular_comissao
        resultado = calcular_comissao(250, "BTC")
        
        # Verifica os logs capturados
        log_output = log_capture.getvalue()
        
        if log_output:
            print(f"   ⚠️ Logs de warning encontrados:")
            print(f"   {log_output}")
        else:
            print("   ✅ Nenhum warning encontrado")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    finally:
        logger.removeHandler(handler)

if __name__ == "__main__":
    testar_sistema_comissao()
    simular_resumo_compra() 
    verificar_logs_warning()
    
    print("\n🎯 RESUMO:")
    print("=" * 60)
    print("Se você ainda vê 1.0% no bot:")
    print("1. 🔄 O bot precisa ser reiniciado")
    print("2. 💾 Cache do Telegram/cliente")
    print("3. 🚨 Algum erro não detectado neste teste")
    print("4. 📱 Instância diferente do bot rodando")
