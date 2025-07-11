#!/usr/bin/env python3
# TESTE RÁPIDO MENU V2 - Valida se o novo menu está funcionando

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def teste_menu_v2():
    """Testa se o Menu V2 está funcionando"""
    try:
        print("🧪 TESTANDO MENU COMPRA V2")
        print("=" * 40)
        
        # Teste 1: Import básico
        print("📦 Teste 1: Importando Menu V2...")
        from menus.menu_compra_v2 import MenuCompraV2, get_compra_conversation_v2, set_menu_principal_v2
        print("✅ Import bem-sucedido!")
        
        # Teste 2: Instanciação
        print("\n🏗️ Teste 2: Criando instância...")
        menu = MenuCompraV2()
        print("✅ Instância criada!")
        
        # Teste 3: Conversation Handler
        print("\n🔄 Teste 3: Criando ConversationHandler...")
        handler = get_compra_conversation_v2()
        print(f"✅ Handler criado: {type(handler).__name__}")
        
        # Teste 4: Estados
        print("\n📋 Teste 4: Verificando estados...")
        estados = handler.states
        print(f"✅ Estados definidos: {len(estados)}")
        for estado, handlers in estados.items():
            print(f"   - Estado {estado}: {len(handlers)} handlers")
        
        # Teste 5: Entry points
        print("\n🚪 Teste 5: Verificando entry points...")
        entry_points = handler.entry_points
        print(f"✅ Entry points: {len(entry_points)}")
        
        # Teste 6: Menus
        print("\n📱 Teste 6: Testando menus...")
        moedas = menu.menu_moedas()
        redes = menu.menu_redes()
        valores = menu.menu_valores_sugeridos()
        print(f"✅ Menu moedas: {len(moedas)} opções")
        print(f"✅ Menu redes: {len(redes)} opções")
        print(f"✅ Menu valores: {len(valores)} opções")
        
        # Teste 7: Validação de valor
        print("\n💰 Teste 7: Testando validação de valores...")
        testes_valor = [
            ("10", True),
            ("50.50", True),
            ("5000", True),
            ("5", False),  # Muito baixo
            ("6000", False),  # Muito alto
            ("abc", False),  # Inválido
        ]
        
        for valor_teste, esperado in testes_valor:
            valido, _, _ = menu.validar_valor(valor_teste)
            status = "✅" if valido == esperado else "❌"
            print(f"   {status} Valor '{valor_teste}': {valido} (esperado: {esperado})")
        
        print("\n" + "=" * 40)
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Menu V2 está funcionando corretamente!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = teste_menu_v2()
    
    if sucesso:
        print("\n🚀 PRÓXIMO PASSO: Inicie o bot para testar na prática!")
        print("   Comando: python -m ghost.bot")
    else:
        print("\n⚠️ PROBLEMAS DETECTADOS!")
        print("   Execute o script de reversão se necessário:")
        print("   python scripts/reverter_menu_v2.py")
