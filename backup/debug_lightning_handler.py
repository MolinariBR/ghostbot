#!/usr/bin/env python3
"""
Debug do Handler Lightning - Verificar valores sendo processados
"""

import requests
import json

def debug_voltz_status(depix_id):
    """Debug do status Voltz para um depix_id específico"""
    print(f"🔍 DEBUG VOLTZ STATUS: {depix_id}")
    print("=" * 60)
    
    # 1. Verificar Voltz
    try:
        url = "https://useghost.squareweb.app/voltz/voltz_status.php"
        payload = {"depix_id": depix_id}
        
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"📊 VOLTZ RESPONSE RAW:")
        print(f"Status Code: {response.status_code}")
        print(f"Content: {response.text}")
        
        try:
            # A API Voltz está retornando múltiplos JSONs concatenados
            content = response.text
            
            # Vamos encontrar onde começa o segundo JSON procurando por '}{"success"'
            split_point = content.find('}{"success"')
            if split_point != -1:
                # Pegar o segundo JSON
                second_json = content[split_point + 1:]  # +1 para pular o '}'
                result = json.loads(second_json)
                print(f"\n📊 VOLTZ RESPONSE JSON (segundo):")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                # Se não encontrar, tentar parsear como JSON normal
                result = json.loads(content)
                print(f"\n📊 VOLTZ RESPONSE JSON:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as json_err:
            print(f"❌ Erro ao parsear JSON: {json_err}")
            print(f"Content que tentou parsear: {content}")
            return
        
        # Extrair dados como o handler faz
        if result.get('success'):
            data = result
            status = data.get('status', 'unknown')
            message_text = data.get('message', '')
            amount_sats = data.get('amount_sats', 0)
            
            print(f"\n🎯 DADOS EXTRAÍDOS:")
            print(f"   Status: {status}")
            print(f"   Message: {message_text}")
            print(f"   Amount Sats: {amount_sats}")
            
            # Se amount_sats for 0, tentar buscar do depósito
            if amount_sats == 0:
                print(f"\n💡 Amount_sats é 0, buscando do depósito...")
                
                dep_response = requests.get(f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}", timeout=10)
                if dep_response.status_code == 200:
                    dep_data = dep_response.json()
                    print(f"📋 DEPOSIT DATA:")
                    print(json.dumps(dep_data, indent=2, ensure_ascii=False))
                    
                    if dep_data.get('deposits'):
                        dep = dep_data['deposits'][0]
                        amount_cents = dep.get('amount_in_cents', 0)
                        amount_sats_calc = int((amount_cents / 100) * 166.67)
                        
                        print(f"\n🧮 CÁLCULO:")
                        print(f"   Amount in cents: {amount_cents}")
                        print(f"   Amount em reais: R$ {amount_cents/100:.2f}")
                        print(f"   Amount sats calculado: {amount_sats_calc}")
                        print(f"   Valor final exibido: R$ {amount_sats_calc/166.67:.2f}")
                else:
                    print(f"❌ Erro ao buscar depósito: {dep_response.status_code}")
        else:
            print(f"❌ Voltz não retornou sucesso")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    print("🚀 DEBUG LIGHTNING HANDLER")
    print("=" * 40)
    
    # IDs dos depósitos que acabamos de confirmar
    test_ids = [
        "ln_teste_1751929229_0_380a3b",
        "ln_teste_1751929187_0_380a3b"
    ]
    
    for i, depix_id in enumerate(test_ids, 1):
        print(f"\n--- DEBUG {i}/{len(test_ids)} ---")
        debug_voltz_status(depix_id)
        print()

if __name__ == "__main__":
    main()
