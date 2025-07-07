#!/usr/bin/env python3
"""
VERIFICAR SALDO VOLTZ - Diagnóstico Lightning
==============================================

Script para verificar o saldo da carteira Lightning Voltz
e diagnosticar problemas de geração de invoices.
"""

import requests
import json
import sys
import os

# Adiciona path do ghost
sys.path.append('/home/mau/bot/ghost')

def verificar_saldo_voltz():
    """
    Verifica o saldo da carteira Voltz via API.
    """
    print("💰 VERIFICANDO SALDO VOLTZ")
    print("=" * 40)
    
    # Configurações Voltz (do arquivo de configuração)
    try:
        # Importa configurações do backend
        voltz_config = {
            'node_url': 'https://lnvoltz.com',
            'wallet_id': 'f3c366b7fb6f43fa9467c4dccedaf824',
            'admin_key': '8fce34f4b0f8446a990418bd167dc644',
            'invoice_key': 'b2f68df91c8848f6a1db26f2e403321f'
        }
        
        print(f"🔗 Node URL: {voltz_config['node_url']}")
        print(f"🆔 Wallet ID: {voltz_config['wallet_id'][:16]}...")
        
        # Verificar saldo da carteira
        wallet_url = f"{voltz_config['node_url']}/api/v1/wallet"
        headers = {
            'X-Api-Key': voltz_config['admin_key'],
            'Content-Type': 'application/json'
        }
        
        print(f"\n💳 Consultando saldo da carteira...")
        response = requests.get(wallet_url, headers=headers, timeout=15)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta da carteira:")
            print(json.dumps(data, indent=2))
            
            # Extrair informações de saldo
            balance = data.get('balance', 0)
            balance_sats = balance / 1000 if balance else 0  # msat para sats
            
            print(f"\n💰 SALDO ATUAL:")
            print(f"   • Saldo: {balance_sats:,.0f} sats")
            print(f"   • Valor: {balance} msat")
            
            if balance_sats < 1000:  # Menos de 1000 sats
                print(f"⚠️ SALDO MUITO BAIXO!")
                print(f"   • Saldo atual: {balance_sats:,.0f} sats")
                print(f"   • Mínimo recomendado: 1,000 sats")
                print(f"   • Para gerar invoices é necessário saldo suficiente")
                return False
            else:
                print(f"✅ Saldo suficiente para gerar invoices")
                return True
                
        else:
            print(f"❌ Erro ao consultar carteira: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def verificar_status_node():
    """
    Verifica se o Lightning Node está online e funcionando.
    """
    print(f"\n⚡ VERIFICANDO STATUS DO NODE")
    print("=" * 40)
    
    try:
        voltz_config = {
            'node_url': 'https://lnvoltz.com',
            'admin_key': '8fce34f4b0f8446a990418bd167dc644'
        }
        
        # Verificar status geral do node
        status_url = f"{voltz_config['node_url']}/api/v1/node"
        headers = {
            'X-Api-Key': voltz_config['admin_key'],
            'Content-Type': 'application/json'
        }
        
        response = requests.get(status_url, headers=headers, timeout=15)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Node Status:")
            print(json.dumps(data, indent=2))
            
            # Verificar se node está sincronizado
            synced = data.get('synced_to_chain', False)
            if synced:
                print(f"✅ Node sincronizado com a blockchain")
            else:
                print(f"⚠️ Node não está sincronizado")
            
            return synced
        else:
            print(f"❌ Erro ao verificar node: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação do node: {e}")
        return False

def testar_geracao_invoice():
    """
    Testa a geração de um invoice pequeno para diagnóstico.
    """
    print(f"\n🧪 TESTANDO GERAÇÃO DE INVOICE")
    print("=" * 40)
    
    try:
        voltz_config = {
            'node_url': 'https://lnvoltz.com',
            'wallet_id': 'f3c366b7fb6f43fa9467c4dccedaf824',
            'invoice_key': 'b2f68df91c8848f6a1db26f2e403321f'
        }
        
        # Criar invoice de teste (1000 sats)
        invoice_url = f"{voltz_config['node_url']}/api/v1/payments"
        headers = {
            'X-Api-Key': voltz_config['invoice_key'],
            'Content-Type': 'application/json'
        }
        
        payload = {
            'out': False,  # Invoice (recebimento)
            'amount': 1000,  # 1000 sats
            'memo': 'Teste Ghost Lightning'
        }
        
        print(f"📋 Criando invoice de teste (1000 sats)...")
        response = requests.post(invoice_url, json=payload, headers=headers, timeout=15)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Invoice criado com sucesso!")
            
            payment_request = data.get('payment_request')
            if payment_request:
                print(f"⚡ Invoice: {payment_request[:50]}...")
                print(f"✅ Sistema Lightning está funcionando!")
                return True
            else:
                print(f"⚠️ Invoice criado mas sem payment_request")
                print(f"Resposta: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"❌ Erro ao criar invoice: {response.status_code}")
            print(f"Resposta: {response.text}")
            
            if "insufficient" in response.text.lower():
                print(f"💡 CAUSA IDENTIFICADA: Saldo insuficiente!")
                return False
            elif "balance" in response.text.lower():
                print(f"💡 CAUSA IDENTIFICADA: Problema de saldo!")
                return False
            else:
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste de invoice: {e}")
        return False

def main():
    print("🔍 DIAGNÓSTICO COMPLETO VOLTZ LIGHTNING")
    print("=" * 50)
    
    resultados = {
        'saldo': False,
        'node': False,
        'invoice': False
    }
    
    # 1. Verificar saldo
    print(f"\n🚀 FASE 1: Verificando saldo da carteira")
    resultados['saldo'] = verificar_saldo_voltz()
    
    # 2. Verificar status do node
    print(f"\n🚀 FASE 2: Verificando status do Lightning Node")
    resultados['node'] = verificar_status_node()
    
    # 3. Testar geração de invoice
    print(f"\n🚀 FASE 3: Testando geração de invoice")
    resultados['invoice'] = testar_geracao_invoice()
    
    # Resultado final
    print(f"\n📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 50)
    
    for teste, sucesso in resultados.items():
        status = "✅" if sucesso else "❌"
        print(f"{status} {teste.capitalize()}: {'OK' if sucesso else 'FALHOU'}")
    
    if not resultados['saldo']:
        print(f"\n🎯 PROBLEMA IDENTIFICADO: SALDO INSUFICIENTE")
        print(f"   • A carteira Voltz não tem saldo Lightning suficiente")
        print(f"   • É necessário fazer deposit na carteira Lightning")
        print(f"   • Sem saldo, não é possível gerar invoices")
        
        print(f"\n💡 SOLUÇÕES:")
        print(f"   1. Fazer deposit Bitcoin na carteira Voltz")
        print(f"   2. Abrir canais Lightning com saldo suficiente")
        print(f"   3. Receber pagamentos Lightning para aumentar saldo")
        
    elif not resultados['node']:
        print(f"\n🎯 PROBLEMA IDENTIFICADO: LIGHTNING NODE")
        print(f"   • O Lightning Node não está funcionando corretamente")
        print(f"   • Pode estar offline ou não sincronizado")
        
    elif not resultados['invoice']:
        print(f"\n🎯 PROBLEMA IDENTIFICADO: GERAÇÃO DE INVOICE")
        print(f"   • Não consegue gerar invoices mesmo com saldo")
        print(f"   • Pode ser problema de configuração ou API")
        
    else:
        print(f"\n🎉 TUDO FUNCIONANDO!")
        print(f"   • O problema pode estar na integração Ghost ↔ Voltz")
        print(f"   • Verificar logs do processamento")

if __name__ == "__main__":
    main()
