#!/usr/bin/env python3
"""
Teste do novo sistema inteligente de monitoramento PIX
"""
import sys
import asyncio
sys.path.append('/home/mau/bot/ghost')

async def test_smart_monitoring():
    """Testa o novo sistema inteligente"""
    try:
        print("🧠 Testando Sistema Inteligente de Monitoramento PIX...")
        
        # Dados do PIX atual
        depix_id = '0197f7083e627dfe8532dfb32d576171'
        chat_id = '7910260237'
        amount_brl = 10.0
        
        # Importar o monitor
        from trigger.smart_pix_monitor import smart_monitor
        
        print(f"📝 Registrando PIX no sistema inteligente...")
        print(f"   Depix ID: {depix_id}")
        print(f"   Chat ID: {chat_id}")
        print(f"   Valor: R$ {amount_brl}")
        
        # Registrar o PIX (vai iniciar verificação inteligente automaticamente)
        smart_monitor.register_pix_payment(depix_id, chat_id, amount_brl)
        
        print("✅ PIX registrado! Sistema inteligente iniciado.")
        print("⏱️ Aguardando verificação inteligente...")
        
        # Aguardar um pouco para ver o resultado
        await asyncio.sleep(60)  # 1 minuto para primeira verificação
        
        # Verificar status
        stats = smart_monitor.get_stats()
        active = smart_monitor.get_active_payments()
        
        print(f"📊 Estatísticas: {stats}")
        print(f"🔄 Pagamentos ativos: {len(active)}")
        
        for pid, data in active.items():
            print(f"   - {pid}: {data.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Iniciando teste do sistema inteligente...")
    result = asyncio.run(test_smart_monitoring())
    print(f"✅ Resultado: {'Sucesso' if result else 'Falha'}")
    return result

if __name__ == "__main__":
    main()
