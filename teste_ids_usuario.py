#!/usr/bin/env python3
"""
TESTE ESPECÍFICO - IDs Fornecidos pelo Usuário
==============================================

Este script testa especificamente os depix_ids fornecidos pelo usuário
para verificar se conseguimos forçar a geração de invoices Lightning.
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

import requests
import json
import time
from api.voltz import VoltzAPI

# IDs fornecidos pelo usuário
DEPIX_IDS_TESTE = [
    "0197e0ed06537df9820a28f5a5380a3b",
    "0197e10b5b8f7df9a6bf9430188534e4",
    "0197e12300eb7df9808ca5d7719ea40e", 
    "0197e5214a377dfaae6e541f68057444"
]

def buscar_dados_deposito(depix_id):
    """Busca dados completos de um depósito pelo depix_id."""
    url = f"https://useghost.squareweb.app/rest/deposit.php"
    
    try:
        # Primeiro, tentar buscar por depix_id
        response = requests.get(f"{url}?depix_id={depix_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') and data.get('deposit'):
            return data['deposit']
        
        print(f"⚠️ Depósito {depix_id} não encontrado pela busca direta")
        return None
        
    except Exception as e:
        print(f"❌ Erro ao buscar depósito {depix_id}: {e}")
        return None

def forcar_confirmacao_deposito(depix_id, fake_txid=None):
    """Força a confirmação de um depósito alterando status e txid."""
    if not fake_txid:
        fake_txid = f"teste_blockchain_{int(time.time())}"
    
    url = "https://useghost.squareweb.app/api/update_transaction.php"
    
    data = {
        'depix_id': depix_id,
        'status': 'confirmado',
        'blockchainTxID': fake_txid
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Status forçado para 'confirmado' com TxID: {fake_txid}")
            return True
        else:
            print(f"❌ Erro ao forçar confirmação: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao forçar confirmação: {e}")
        return False

def verificar_invoice_gerado(depix_id, max_tentativas=5):
    """Verifica se o invoice foi gerado após confirmação."""
    voltz = VoltzAPI()
    
    print(f"\n🔍 Verificando se invoice foi gerado para {depix_id}...")
    
    for tentativa in range(1, max_tentativas + 1):
        print(f"   Tentativa {tentativa}/{max_tentativas}...")
        
        status = voltz.check_deposit_status(depix_id)
        
        if status.get('success'):
            print(f"✅ Status Voltz: {status.get('status')}")
            
            if status.get('invoice'):
                print(f"⚡ INVOICE GERADO COM SUCESSO!")
                print(f"📋 Payment Request: {status['invoice'][:50]}...")
                if status.get('qr_code'):
                    print(f"📱 QR Code: {status['qr_code']}")
                return status
            else:
                print("   Aguardando invoice ser gerado...")
        else:
            print(f"❌ Erro Voltz: {status.get('error', 'Erro desconhecido')}")
        
        if tentativa < max_tentativas:
            print("   ⏱️ Aguardando 3 segundos...")
            time.sleep(3)
    
    print("⏰ Invoice não foi gerado no tempo esperado")
    return None

def executar_cron_voltz():
    """Executa o processamento do cron Voltz."""
    print("\n🔄 Executando cron Voltz...")
    
    try:
        url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print("✅ Cron Voltz executado")
        print(f"📝 Resposta: {response.text[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar cron: {e}")
        return False

def testar_depix_id(depix_id):
    """Testa um depix_id específico."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTANDO DEPIX_ID: {depix_id}")
    print(f"{'='*60}")
    
    # 1. Buscar dados do depósito
    print("1️⃣ Buscando dados do depósito...")
    deposit_data = buscar_dados_deposito(depix_id)
    
    if not deposit_data:
        print(f"❌ Depósito {depix_id} não foi encontrado na base de dados")
        print("   Pode ter sido removido ou nunca existido")
        return False
    
    print(f"✅ Depósito encontrado:")
    print(f"   Status atual: {deposit_data.get('status')}")
    print(f"   Valor: R$ {deposit_data.get('amount_in_cents', 0)/100:.2f}")
    print(f"   Moeda: {deposit_data.get('moeda')}")
    print(f"   Rede: {deposit_data.get('rede')}")
    print(f"   TxID: {deposit_data.get('blockchainTxID', 'Nenhum')}")
    
    # 2. Verificar se já tem invoice
    print("\n2️⃣ Verificando se já existe invoice...")
    voltz = VoltzAPI()
    status_inicial = voltz.check_deposit_status(depix_id)
    
    if status_inicial.get('success') and status_inicial.get('invoice'):
        print(f"⚡ INVOICE JÁ EXISTE!")
        print(f"📋 Payment Request: {status_inicial['invoice'][:50]}...")
        return True
    
    # 3. Forçar confirmação se necessário
    if deposit_data.get('status') != 'confirmado':
        print(f"\n3️⃣ Forçando confirmação do depósito...")
        if not forcar_confirmacao_deposito(depix_id):
            print("❌ Falha ao forçar confirmação")
            return False
    else:
        print(f"\n3️⃣ Depósito já está confirmado")
    
    # 4. Executar cron Voltz
    print(f"\n4️⃣ Executando processamento Voltz...")
    if not executar_cron_voltz():
        print("❌ Falha ao executar cron")
        return False
    
    # 5. Verificar se invoice foi gerado
    print(f"\n5️⃣ Verificando geração do invoice...")
    invoice_result = verificar_invoice_gerado(depix_id)
    
    if invoice_result:
        print(f"\n🎉 SUCESSO! Invoice gerado para {depix_id}")
        return True
    else:
        print(f"\n❌ FALHA! Invoice não foi gerado para {depix_id}")
        return False

def main():
    print("🧪 TESTE ESPECÍFICO - IDs DO USUÁRIO")
    print("=" * 50)
    
    print("📋 IDs fornecidos para teste:")
    for i, depix_id in enumerate(DEPIX_IDS_TESTE, 1):
        print(f"   {i}. {depix_id}")
    
    print(f"\nOpções:")
    print("1. Testar um ID específico")
    print("2. Testar todos os IDs sequencialmente")
    print("3. Testar apenas IDs que existem na base")
    
    try:
        opcao = int(input("\nEscolha uma opção (1-3): "))
        
        if opcao == 1:
            # Testar um ID específico
            print("\nEscolha o ID para testar:")
            for i, depix_id in enumerate(DEPIX_IDS_TESTE, 1):
                print(f"{i}. {depix_id}")
            
            escolha = int(input("Digite o número: ")) - 1
            if 0 <= escolha < len(DEPIX_IDS_TESTE):
                testar_depix_id(DEPIX_IDS_TESTE[escolha])
            else:
                print("❌ Escolha inválida")
        
        elif opcao == 2:
            # Testar todos sequencialmente
            sucessos = 0
            for depix_id in DEPIX_IDS_TESTE:
                if testar_depix_id(depix_id):
                    sucessos += 1
                print(f"\n{'⏭️ ' * 20}")
            
            print(f"\n📊 RESUMO FINAL:")
            print(f"   Total testados: {len(DEPIX_IDS_TESTE)}")
            print(f"   Sucessos: {sucessos}")
            print(f"   Falhas: {len(DEPIX_IDS_TESTE) - sucessos}")
        
        elif opcao == 3:
            # Testar apenas IDs que existem
            print("\n🔍 Verificando quais IDs existem na base...")
            ids_existentes = []
            
            for depix_id in DEPIX_IDS_TESTE:
                print(f"   Verificando {depix_id}...")
                if buscar_dados_deposito(depix_id):
                    print(f"   ✅ Existe")
                    ids_existentes.append(depix_id)
                else:
                    print(f"   ❌ Não existe")
            
            if not ids_existentes:
                print("\n❌ Nenhum dos IDs existe na base de dados")
                return
            
            print(f"\n📋 IDs existentes encontrados: {len(ids_existentes)}")
            for depix_id in ids_existentes:
                print(f"   • {depix_id}")
            
            if input("\nTestar todos os IDs existentes? (s/n): ").lower() == 's':
                sucessos = 0
                for depix_id in ids_existentes:
                    if testar_depix_id(depix_id):
                        sucessos += 1
                
                print(f"\n📊 RESUMO:")
                print(f"   IDs existentes testados: {len(ids_existentes)}")
                print(f"   Sucessos: {sucessos}")
        
        else:
            print("❌ Opção inválida")
    
    except ValueError:
        print("❌ Número inválido")
    except KeyboardInterrupt:
        print("\n\n🛑 Teste interrompido pelo usuário")

if __name__ == "__main__":
    main()
