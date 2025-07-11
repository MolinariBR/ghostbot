#!/usr/bin/env python3
"""
Debug do problema de Lightning Address no backend
"""
import requests
import json

def debug_lightning_issue():
    """Debug do problema específico"""
    
    print("🔍 DEBUG: Problema Lightning Address Backend")
    print("=" * 60)
    
    backend_url = "https://useghost.squareweb.app"
    chat_id = "7910260237"
    
    # 1. Verificar depósitos pendentes
    print("\n1️⃣ VERIFICANDO DEPÓSITOS PENDENTES:")
    try:
        response = requests.get(
            f"{backend_url}/rest/deposit.php?chatid={chat_id}",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            deposits = data.get('deposits', [])
            
            print(f"   📊 Total de depósitos: {len(deposits)}")
            
            # Procura depósitos Lightning pendentes
            lightning_pending = [
                d for d in deposits 
                if d.get('rede') in ['Lightning', '⚡ Lightning'] 
                and d.get('status') in ['pending', 'confirmado']
                and not d.get('blockchainTxID')
            ]
            
            print(f"   ⚡ Lightning pendentes: {len(lightning_pending)}")
            
            if lightning_pending:
                latest = lightning_pending[-1]  # Mais recente
                print(f"   📋 Mais recente:")
                print(f"      🆔 ID: {latest.get('id')}")
                print(f"      💰 Valor: R$ {latest.get('amount_in_cents', 0)/100}")
                print(f"      🏷️ Address: {latest.get('address', 'N/A')}")
                print(f"      📊 Status: {latest.get('status')}")
                print(f"      🔗 DepixID: {latest.get('depix_id')}")
                return latest.get('depix_id')
            else:
                print("   ⚠️ Nenhum depósito Lightning pendente encontrado")
                return None
        else:
            print(f"   ❌ HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def test_lightning_resolver():
    """Testa o resolvedor Lightning Address diretamente"""
    
    print("\n2️⃣ TESTANDO LIGHTNING ADDRESS RESOLVER:")
    
    lightning_address = "bouncyflight79@walletofsatoshi.com"
    
    try:
        # Testa resolução manual
        username, domain = lightning_address.split('@')
        well_known_url = f"https://{domain}/.well-known/lnurlp/{username}"
        
        print(f"   🌐 URL: {well_known_url}")
        
        response = requests.get(well_known_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Configuração Lightning válida")
            print(f"   📋 Callback: {data.get('callback', 'N/A')}")
            print(f"   💰 Min: {data.get('minSendable', 0)/1000} sats")
            print(f"   💰 Max: {data.get('maxSendable', 0)/1000} sats")
            
            # Testa callback
            callback_url = data.get('callback')
            if callback_url:
                test_amount_msat = 1000 * 1000  # 1000 sats em msat
                callback_test_url = f"{callback_url}?amount={test_amount_msat}"
                
                print(f"   🔄 Testando callback: {callback_test_url}")
                
                callback_response = requests.get(callback_test_url, timeout=10)
                
                if callback_response.status_code == 200:
                    callback_data = callback_response.json()
                    if 'pr' in callback_data:
                        bolt11 = callback_data['pr']
                        print(f"   ✅ BOLT11 obtido: {bolt11[:50]}...")
                        return True
                    else:
                        print(f"   ❌ Callback sem BOLT11: {callback_data}")
                        return False
                else:
                    print(f"   ❌ Callback falhou: HTTP {callback_response.status_code}")
                    return False
            else:
                print(f"   ❌ Callback não encontrado")
                return False
        else:
            print(f"   ❌ Resolução falhou: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_voltz_connectivity():
    """Testa conectividade com Voltz"""
    
    print("\n3️⃣ TESTANDO CONECTIVIDADE VOLTZ:")
    
    voltz_config = {
        'node_url': 'https://lnvoltz.com',
        'admin_key': '8fce34f4b0f8446a990418bd167dc644'
    }
    
    headers = {
        'X-Api-Key': voltz_config['admin_key'],
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{voltz_config['node_url']}/api/v1/wallet",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            print(f"   ✅ Voltz acessível")
            try:
                data = response.json()
                print(f"   📊 Resposta: {data}")
                return True
            except:
                print(f"   ⚠️ Resposta não é JSON: {response.text}")
                return False
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def suggest_solution():
    """Sugere solução baseada nos testes"""
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO E SOLUÇÃO:")
    print("=" * 60)
    
    # Executa os testes
    depix_id = debug_lightning_issue()
    lightning_ok = test_lightning_resolver()
    voltz_ok = test_voltz_connectivity()
    
    print(f"\n📊 RESULTADOS:")
    print(f"   📋 Depósito pendente: {'✅' if depix_id else '❌'}")
    print(f"   ⚡ Lightning resolver: {'✅' if lightning_ok else '❌'}")
    print(f"   🔧 Voltz conectividade: {'✅' if voltz_ok else '❌'}")
    
    if depix_id and lightning_ok and voltz_ok:
        print(f"\n🎉 TUDO FUNCIONANDO!")
        print(f"💡 O problema pode ser temporário ou de configuração do backend")
        print(f"🔄 Tente novamente o Lightning Address")
        
    elif not lightning_ok:
        print(f"\n❌ PROBLEMA: Lightning Address resolver")
        print(f"💡 O endereço pode estar inválido ou o serviço offline")
        print(f"🔄 Tente um Lightning Address diferente:")
        print(f"   • user@walletofsatoshi.com")
        print(f"   • user@strike.army")
        
    elif not voltz_ok:
        print(f"\n❌ PROBLEMA: Conectividade Voltz")
        print(f"💡 O servidor não consegue acessar a API Voltz")
        print(f"🔧 Verifique credenciais e conectividade do servidor")
        
    elif not depix_id:
        print(f"\n❌ PROBLEMA: Nenhum depósito pendente")
        print(f"💡 Faça uma nova compra PIX primeiro")
        
    else:
        print(f"\n⚠️ PROBLEMA MISTO")
        print(f"💡 Múltiplos componentes com problemas")

if __name__ == "__main__":
    suggest_solution()
