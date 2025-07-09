#!/usr/bin/env python3
"""
Teste de simulação completa da interação do usuário para verificar o fluxo corrigido.
"""
import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockUpdate:
    """Simula o objeto Update do Telegram."""
    def __init__(self, message_text):
        self.message = MagicMock()
        self.message.text = message_text
        self.message.reply_text = AsyncMock()

class MockContext:
    """Simula o objeto Context do Telegram."""
    def __init__(self):
        self.user_data = {}

async def simular_fluxo_completo_usuario():
    """Simula o fluxo completo de um usuário fazendo uma compra."""
    print("\n🎭 SIMULAÇÃO COMPLETA DO FLUXO DO USUÁRIO")
    print("=" * 60)
    
    # 1. Usuário seleciona moeda
    print("\n1️⃣ SELEÇÃO DA MOEDA")
    context = MockContext()
    context.user_data['moeda'] = '₿ Bitcoin (BTC)'  # Como vem do teclado
    print(f"   👤 Usuário selecionou: '{context.user_data['moeda']}'")
    
    # 2. Usuário seleciona rede
    print("\n2️⃣ SELEÇÃO DA REDE")
    context.user_data['rede'] = 'Lightning Network'
    print(f"   🌐 Rede selecionada: '{context.user_data['rede']}'")
    
    # 3. Usuário informa valor
    print("\n3️⃣ VALOR INFORMADO")
    context.user_data['valor_brl'] = 250.0
    print(f"   💰 Valor: R$ {context.user_data['valor_brl']}")
    
    # 4. Usuário informa CPF
    print("\n4️⃣ CPF INFORMADO")
    context.user_data['cpf'] = '12345678900'
    print(f"   📄 CPF: {context.user_data['cpf']}")
    
    # 5. Sistema gera resumo da compra
    print("\n5️⃣ GERAÇÃO DO RESUMO DA COMPRA")
    print("   🔄 Chamando função resumo_compra...")
    
    # Importa a função real do menu
    import sys
    sys.path.append('/home/mau/bot/ghost')
    
    # Simula a função obter_cotacao
    async def obter_cotacao_mock(moeda):
        print(f"   💱 Obtendo cotação para: '{moeda}'")
        return 350000.0  # Cotação BTC simulada
    
    # Substitui a função original temporariamente
    import menus.menu_compra
    original_obter_cotacao = menus.menu_compra.obter_cotacao
    menus.menu_compra.obter_cotacao = obter_cotacao_mock
    
    try:
        # Cria mocks para Update
        update = MockUpdate("")
        
        # Chama a função real de resumo da compra
        print("   📞 Executando resumo_compra() real...")
        resultado = await menus.menu_compra.resumo_compra(update, context)
        
        # Verifica se a mensagem foi enviada
        if update.message.reply_text.called:
            mensagem_enviada = update.message.reply_text.call_args[0][0]
            print("\n📨 MENSAGEM ENVIADA AO USUÁRIO:")
            print("=" * 50)
            print(mensagem_enviada)
            print("=" * 50)
            
            # Verifica se o percentual está correto
            if "10.0%" in mensagem_enviada:
                print("\n✅ SUCESSO! Percentual 10.0% encontrado na mensagem!")
                return True
            elif "1.0%" in mensagem_enviada:
                print("\n❌ ERRO! Ainda mostra percentual 1.0% (fallback)!")
                return False
            else:
                print("\n⚠️  WARNING! Não foi possível identificar o percentual na mensagem.")
                return False
        else:
            print("\n❌ ERRO! Nenhuma mensagem foi enviada.")
            return False
            
    except Exception as e:
        print(f"\n💥 ERRO DURANTE EXECUÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restaura a função original
        menus.menu_compra.obter_cotacao = original_obter_cotacao

async def verificar_logs_em_tempo_real():
    """Verifica se há mensagens de erro sendo geradas."""
    print("\n📊 VERIFICAÇÃO DE LOGS")
    print("=" * 40)
    
    # Intercepta logs do sistema de comissão
    import logging
    
    log_messages = []
    
    class LogCapture(logging.Handler):
        def emit(self, record):
            log_messages.append(self.format(record))
    
    # Adiciona handler personalizado
    log_capture = LogCapture()
    logging.getLogger('limites.comissao').addHandler(log_capture)
    
    try:
        # Executa teste que pode gerar logs
        from limites.comissao import calcular_comissao
        
        print("   🧪 Testando com string completa (deveria gerar warning)...")
        resultado1 = calcular_comissao(250.0, "₿ Bitcoin (BTC)")
        
        print("   🧪 Testando com sigla extraída (deveria funcionar)...")
        resultado2 = calcular_comissao(250.0, "BTC")
        
        print(f"\n📝 LOGS CAPTURADOS:")
        for i, msg in enumerate(log_messages, 1):
            print(f"   {i}. {msg}")
        
        if resultado1 is None and resultado2 is not None:
            print(f"\n✅ COMPORTAMENTO CORRETO:")
            print(f"   - String completa: None (gera warning)")
            print(f"   - Sigla extraída: Sucesso (percentual {resultado2['comissao']['percentual']:.1f}%)")
            return True
        else:
            print(f"\n❌ COMPORTAMENTO INESPERADO:")
            print(f"   - String completa: {resultado1}")
            print(f"   - Sigla extraída: {resultado2}")
            return False
            
    finally:
        # Remove handler
        logging.getLogger('limites.comissao').removeHandler(log_capture)

async def main():
    """Executa a simulação completa."""
    print("🚀 SIMULAÇÃO COMPLETA DO FLUXO CORRIGIDO")
    print("=" * 70)
    
    # Verifica logs primeiro
    logs_ok = await verificar_logs_em_tempo_real()
    
    # Simula fluxo do usuário
    fluxo_ok = await simular_fluxo_completo_usuario()
    
    print("\n" + "=" * 70)
    print("📋 RESUMO FINAL:")
    print(f"   🗂️  Logs: {'✅ OK' if logs_ok else '❌ PROBLEMA'}")
    print(f"   👤 Fluxo do usuário: {'✅ OK' if fluxo_ok else '❌ PROBLEMA'}")
    
    if logs_ok and fluxo_ok:
        print("\n🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
        print("   O bug do 1% foi corrigido com sucesso.")
        print("   O usuário agora vê o percentual correto (10.0% para BTC).")
    else:
        print("\n⚠️  AINDA HÁ PROBLEMAS A INVESTIGAR!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
