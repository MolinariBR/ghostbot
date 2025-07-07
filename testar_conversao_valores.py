#!/usr/bin/env python3
"""
Testar conversão de valores com as correções feitas
"""

def testar_conversoes():
    print("🧮 TESTANDO CONVERSÕES DE VALORES")
    print("=" * 50)
    
    # Dados dos depósitos criados
    depositos = [
        {"depix_id": "ln_real_1751930501_8534e4", "amount_in_cents": 300, "valor_reais": 3.00},
        {"depix_id": "ln_real_1751930503_9ea40e", "amount_in_cents": 400, "valor_reais": 4.00},
        {"depix_id": "ln_real_1751930506_057444", "amount_in_cents": 500, "valor_reais": 5.00},
    ]
    
    print("📊 Cotação assumida: BTC = R$ 600.000 (1 real = ~166,67 sats)")
    print()
    
    for dep in depositos:
        amount_cents = dep["amount_in_cents"]
        valor_reais = dep["valor_reais"]
        
        # Conversão ANTIGA (incorreta)
        amount_sats_antigo = int(amount_cents * 5)  # 500 sats por real
        valor_reais_antigo = amount_sats_antigo / 500
        
        # Conversão NOVA (correta)
        amount_sats_novo = int((amount_cents / 100) * 166.67)
        valor_reais_novo = amount_sats_novo / 166.67
        
        print(f"💰 Depósito: {dep['depix_id'][-6:]}")
        print(f"   📋 Real: R$ {valor_reais:.2f} ({amount_cents} centavos)")
        print(f"   ❌ ANTIGO: {amount_sats_antigo} sats (R$ {valor_reais_antigo:.2f}) - INCORRETO!")
        print(f"   ✅ NOVO: {amount_sats_novo} sats (R$ {valor_reais_novo:.2f}) - CORRETO!")
        print(f"   📉 Diferença: {amount_sats_antigo - amount_sats_novo} sats a menos (economizou)")
        print()
    
    print("🎯 RESULTADO:")
    print("✅ Com a correção, os valores agora estão compatíveis com o saldo de 2975 sats")
    print("✅ Antes: até 2500 sats por depósito (inviável)")
    print("✅ Agora: 500-833 sats por depósito (viável)")

if __name__ == "__main__":
    testar_conversoes()
