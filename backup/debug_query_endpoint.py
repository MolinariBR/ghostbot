#!/usr/bin/env python3
"""
Debug do handler Lightning - verificar por que está mostrando R$ 0,00
"""

import requests
import json

def debug_deposito(depix_id):
    """Debug de um depósito específico"""
    print(f"🔍 DEBUGANDO DEPÓSITO: {depix_id}")
    print("=" * 60)
    
    # 1. Verificar dados do depósito na API
    url = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('deposits'):
                dep = data['deposits'][0]
                print("📋 DADOS DO DEPÓSITO:")
                print(f"   💰 amount_in_cents: {dep.get('amount_in_cents')}")
                print(f"   💵 Valor real: R$ {dep.get('amount_in_cents', 0) / 100:.2f}")
                print(f"   📊 Status: {dep.get('status')}")
                print(f"   🔗 BlockchainTxID: {dep.get('blockchainTxID')}")
                print(f"   ⚡ Rede: {dep.get('rede')}")
                print()
                
                # 2. Simular conversão do handler
                amount_cents = dep.get('amount_in_cents', 0)
                
                # Conversão NOVA (correta)
                amount_sats_novo = int((amount_cents / 100) * 166.67)
                valor_reais_novo = amount_sats_novo / 166.67
                
                print("🧮 CONVERSÕES:")
                print(f"   ✅ Método novo: {amount_sats_novo} sats → R$ {valor_reais_novo:.2f}")
                print()
                
                return dep
            else:
                print("❌ Depósito não encontrado na API")
        else:
            print(f"❌ Erro API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao buscar depósito: {e}")
    
    return None

def main():
    # Depósitos recém-criados
    depositos = [
        "ln_real_1751930501_8534e4",  # R$ 3,00
        "ln_real_1751930503_9ea40e",  # R$ 4,00  
        "ln_real_1751930506_057444",  # R$ 5,00
    ]
    
    for depix_id in depositos:
        debug_deposito(depix_id)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
        cursor.execute("SELECT id, blockchainTxID, status, rede, chatid, depix_id FROM deposit WHERE rede LIKE '%lightning%' ORDER BY id DESC LIMIT 5")
        debug_deps = cursor.fetchall()
        
        for dep in debug_deps:
            print(f"ID: {dep[0]}")
            print(f"  TxID: '{dep[1]}' (NULL: {dep[1] is None}, Empty: {dep[1] == ''})")
            print(f"  Status: '{dep[2]}'")
            print(f"  Rede: '{dep[3]}'")
            print(f"  ChatID: '{dep[4]}' (NULL: {dep[4] is None})")
            print(f"  DepixID: '{dep[5]}' (NULL: {dep[5] is None})")
            print()
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
