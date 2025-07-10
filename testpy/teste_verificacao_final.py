#!/usr/bin/env python3
"""
Teste de verificação final para confirmar se o bug do 1% foi corrigido.
"""
import asyncio
import logging
from unittest.mock import MagicMock

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def testar_fluxo_resumo_completo():
    """Testa o fluxo completo do resumo da compra."""
    print("\n🔍 TESTE DE VERIFICAÇÃO FINAL")
    print("=" * 50)
    
    # Simula o context.user_data como o bot recebe
    context_data = {
        'moeda': '₿ Bitcoin (BTC)',  # Como vem do teclado
        'rede': 'Lightning Network',
        'valor_brl': 250.0,
        'cpf': '12345678900'
    }
    
    print(f"📥 Dados de entrada:")
    print(f"   🪙 Moeda: '{context_data['moeda']}'")
    print(f"   💰 Valor: R$ {context_data['valor_brl']}")
    
    # Simula a função obter_cotacao
    async def obter_cotacao(moeda):
        return 350000.0  # Cotação simulada para BTC
    
    try:
        moeda = context_data.get('moeda', 'a moeda selecionada')
        valor_brl = context_data.get('valor_brl', 0)
        
        # Obtém a cotação
        cotacao = await obter_cotacao(moeda)
        print(f"💱 Cotação obtida: R$ {cotacao:,.2f}")
        
        # 🚀 INTEGRAÇÃO: Sistema de Comissões (EXATAMENTE como no código atual)
        from limites.comissao import calcular_comissao
        
        # Extrai a sigla da moeda do texto do menu
        print(f"\n🔧 PROCESSAMENTO DA MOEDA:")
        print(f"   📝 Moeda original: '{moeda}'")
        
        moeda_calc = moeda
        if "BTC" in moeda.upper():
            moeda_calc = "BTC"
            print(f"   ✅ Detectado BTC - usando: '{moeda_calc}'")
        elif "USDT" in moeda.upper():
            moeda_calc = "USDT"
            print(f"   ✅ Detectado USDT - usando: '{moeda_calc}'")
        elif "DEPIX" in moeda.upper():
            moeda_calc = "DEPIX"
            print(f"   ✅ Detectado DEPIX - usando: '{moeda_calc}'")
        else:
            print(f"   ⚠️  Moeda não reconhecida - usando original: '{moeda_calc}'")
        
        # Calcula a comissão baseada na moeda e valor
        print(f"\n🧮 CALCULANDO COMISSÃO:")
        print(f"   📞 Chamando: calcular_comissao({valor_brl}, '{moeda_calc}')")
        
        resultado_comissao = calcular_comissao(valor_brl, moeda_calc)
        
        if resultado_comissao:
            print(f"   ✅ Sucesso! Resultado obtido")
            # Usa os valores calculados pelo sistema de comissões
            comissao_total = resultado_comissao['comissao']['total']
            valor_liquido = resultado_comissao['valor_liquido']
            valor_recebido = valor_liquido / cotacao
            
            # Informações da comissão
            comissao_info = resultado_comissao['comissao']
            percentual = comissao_info['percentual']
            taxa_fixa = comissao_info['fixo']
            
            print(f"\n📊 RESULTADO DO CÁLCULO:")
            print(f"   💯 Percentual: {percentual:.1f}%")
            print(f"   🏦 Taxa fixa: R$ {taxa_fixa:.2f}")
            print(f"   💸 Comissão total: R$ {comissao_total:.2f}")
            print(f"   💰 Valor líquido: R$ {valor_liquido:.2f}")
            print(f"   🪙 Você receberá: {valor_recebido:.8f} BTC")
            
            # Verifica se o percentual está correto
            if percentual == 10.0:
                print(f"\n✅ SUCESSO! Percentual correto: {percentual:.1f}%")
                return True
            else:
                print(f"\n❌ ERRO! Percentual incorreto: {percentual:.1f}% (esperado: 10.0%)")
                return False
                
        else:
            print(f"   ❌ Falha! Resultado None - acionando fallback")
            # Fallback para o sistema antigo se não conseguir calcular comissão
            logger.warning(f"Não foi possível calcular comissão para {moeda} valor R$ {valor_brl}")
            percentual = 1.0  # 1.0% (fallback)
            print(f"\n⚠️  FALLBACK ACIONADO! Percentual: {percentual:.1f}%")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

async def testar_multiplas_moedas():
    """Testa com diferentes formatos de moeda."""
    print("\n🔄 TESTE COM MÚLTIPLAS MOEDAS")
    print("=" * 50)
    
    moedas_teste = [
        "₿ Bitcoin (BTC)",
        "💰 USDT (Tether)",
        "🔷 DEPIX",
        "ETH"  # Esta deve falhar
    ]
    
    for moeda in moedas_teste:
        print(f"\n🧪 Testando moeda: '{moeda}'")
        
        # Extrai a sigla
        moeda_calc = moeda
        if "BTC" in moeda.upper():
            moeda_calc = "BTC"
        elif "USDT" in moeda.upper():
            moeda_calc = "USDT"
        elif "DEPIX" in moeda.upper():
            moeda_calc = "DEPIX"
        
        print(f"   📝 Sigla extraída: '{moeda_calc}'")
        
        try:
            from limites.comissao import calcular_comissao
            resultado = calcular_comissao(250.0, moeda_calc)
            
            if resultado:
                percentual = resultado['comissao']['percentual']
                print(f"   ✅ Sucesso: {percentual:.1f}%")
            else:
                print(f"   ❌ Falha: None (fallback acionado)")
                
        except Exception as e:
            print(f"   💥 Erro: {e}")

async def main():
    """Executa todos os testes."""
    print("🚀 INICIANDO VERIFICAÇÃO FINAL DO BUG 1%")
    print("=" * 60)
    
    # Teste principal
    sucesso = await testar_fluxo_resumo_completo()
    
    # Teste com múltiplas moedas
    await testar_multiplas_moedas()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ VERIFICAÇÃO FINAL: BUG CORRIGIDO COM SUCESSO!")
        print("   O percentual 10.0% está sendo calculado corretamente para BTC.")
    else:
        print("❌ VERIFICAÇÃO FINAL: BUG AINDA EXISTE!")
        print("   O sistema ainda está retornando percentual incorreto.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
