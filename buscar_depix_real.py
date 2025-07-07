#!/usr/bin/env python3
"""
BUSCAR DEPIX IDS REAIS
======================
Script para listar seus depósitos reais e testar com eles.
"""

import requests
import json

def buscar_deposits_reais(chatid="7910260237"):
    """Busca depósitos reais de um usuário."""
    print(f"🔍 Buscando depósitos para chat_id: {chatid}")
    
    try:
        url = f"https://useghost.squareweb.app/rest/deposit.php?chatid={chatid}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        deposits = data.get('deposits', [])
        
        if not deposits:
            print("❌ Nenhum depósito encontrado")
            return []
        
        print(f"✅ Encontrados {len(deposits)} depósitos:")
        print("=" * 60)
        
        lightning_deposits = []
        
        for i, dep in enumerate(deposits, 1):
            depix_id = dep.get('depix_id', 'N/A')
            status = dep.get('status', 'N/A')
            valor = dep.get('amount_in_cents', 0) / 100
            moeda = dep.get('moeda', 'N/A')
            rede = dep.get('rede', 'N/A')
            data_criacao = dep.get('created_at', 'N/A')
            
            print(f"{i:2d}. ID: {depix_id}")
            print(f"    Status: {status}")
            print(f"    Valor: R$ {valor:.2f}")
            print(f"    Moeda: {moeda}")
            print(f"    Rede: {rede}")
            print(f"    Data: {data_criacao}")
            
            # Marcar se é Lightning
            if 'lightning' in rede.lower():
                print(f"    ⚡ LIGHTNING DEPOSIT")
                lightning_deposits.append(dep)
            
            print("-" * 40)
        
        print(f"\n⚡ Lightning deposits encontrados: {len(lightning_deposits)}")
        
        return deposits
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def testar_depix_real(depix_id):
    """Testa um depix_id real."""
    print(f"\n🧪 TESTANDO ID REAL: {depix_id}")
    print("=" * 50)
    
    # 1. Verificar se existe no Voltz
    try:
        url = "https://useghost.squareweb.app/voltz/voltz_status.php"
        payload = {"depix_id": depix_id}
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            print("✅ Depósito encontrado no Voltz!")
            
            deposit = result.get('deposit', {})
            print(f"📋 Dados:")
            print(f"   Status: {deposit.get('status')}")
            print(f"   Valor: R$ {deposit.get('amount_in_cents', 0)/100:.2f}")
            print(f"   Moeda: {deposit.get('moeda')}")
            print(f"   Rede: {deposit.get('rede')}")
            print(f"   TxID: {deposit.get('blockchainTxID', 'N/A')}")
            
            if result.get('invoice'):
                print(f"⚡ INVOICE JÁ EXISTE!")
                print(f"📱 Payment Request: {result['invoice']}")
                return True
            else:
                print(f"⏳ Invoice ainda não gerado")
                
                # Se confirmado, tentar forçar processamento
                if deposit.get('status') == 'confirmado':
                    print("🔄 Executando cron Voltz para processar...")
                    try:
                        cron_url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
                        requests.get(cron_url, timeout=30)
                        print("✅ Cron executado")
                        
                        # Verificar novamente
                        import time
                        time.sleep(5)
                        response2 = requests.post(url, json=payload, timeout=10)
                        result2 = response2.json()
                        
                        if result2.get('invoice'):
                            print(f"⚡ INVOICE GERADO!")
                            print(f"📱 Payment Request: {result2['invoice']}")
                            return True
                        else:
                            print("❌ Invoice ainda não foi gerado")
                    except Exception as e:
                        print(f"❌ Erro no cron: {e}")
                
                return False
        else:
            print(f"❌ Depósito não encontrado: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🔍 BUSCAR E TESTAR DEPIX IDS REAIS")
    print("=" * 40)
    
    # Buscar depósitos reais
    deposits = buscar_deposits_reais()
    
    if not deposits:
        return
    
    # Filtrar apenas Lightning
    lightning_deps = [d for d in deposits if 'lightning' in d.get('rede', '').lower()]
    
    if lightning_deps:
        print(f"\n⚡ TESTANDO DEPÓSITOS LIGHTNING:")
        for i, dep in enumerate(lightning_deps, 1):
            print(f"\n--- TESTE {i}/{len(lightning_deps)} ---")
            testar_depix_real(dep['depix_id'])
    else:
        print(f"\n⚠️ Nenhum depósito Lightning encontrado")
        print(f"💡 Escolha um depósito qualquer para testar:")
        
        try:
            escolha = int(input(f"Digite o número (1-{len(deposits)}): ")) - 1
            if 0 <= escolha < len(deposits):
                testar_depix_real(deposits[escolha]['depix_id'])
            else:
                print("❌ Escolha inválida")
        except ValueError:
            print("❌ Número inválido")

if __name__ == "__main__":
    main()
