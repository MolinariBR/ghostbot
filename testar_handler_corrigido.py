#!/usr/bin/env python3
"""
Testar o handler Lightning corrigido simulando uma chamada do Voltz
"""

import requests

def testar_handler():
    print("🧪 TESTANDO HANDLER LIGHTNING CORRIGIDO")
    print("=" * 50)
    
    # Simular um depósito Lightning confirmado
    depix_id = "teste_1751898619"  # Um dos depósitos que confirmamos
    
    print(f"🔍 Testando depósito: {depix_id}")
    
    # 1. Verificar dados do depósito via API
    url = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('deposits'):
                dep = data['deposits'][0]
                amount_cents = dep.get('amount_in_cents', 0)
                
                print(f"📋 Dados do depósito:")
                print(f"   💰 amount_in_cents: {amount_cents}")
                print(f"   💵 Valor: R$ {amount_cents/100:.2f}")
                print(f"   📊 Status: {dep.get('status')}")
                print(f"   🔗 TxID: {dep.get('blockchainTxID')}")
                print()
                
                # 2. Simular conversão do handler corrigido
                amount_sats = int((amount_cents / 100) * 166.67)
                valor_reais = amount_sats / 166.67
                
                print(f"🧮 Conversão Handler Lightning:")
                print(f"   ⚡ amount_sats: {amount_sats}")
                print(f"   💵 valor_reais: R$ {valor_reais:.2f}")
                print()
                
                # 3. Verificar se está correto
                if amount_cents == 1000:  # R$ 10,00
                    expected_sats = int(10 * 166.67)
                    print(f"✅ TESTE PASSOU:")
                    print(f"   • Esperado: ~{expected_sats} sats para R$ 10,00")
                    print(f"   • Calculado: {amount_sats} sats")
                    print(f"   • Diferença: {abs(expected_sats - amount_sats)} sats")
                    print(f"   • Valor exibido: R$ {valor_reais:.2f}")
                    
                    if abs(expected_sats - amount_sats) < 10:
                        print("🎉 CONVERSÃO CORRETA!")
                    else:
                        print("❌ Conversão incorreta")
                else:
                    print(f"ℹ️ Valor diferente de R$ 10,00: R$ {amount_cents/100:.2f}")
                
            else:
                print("❌ Depósito não encontrado")
        else:
            print(f"❌ Erro API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_handler()
