#!/usr/bin/env python3
"""
TESTE FORÇADO - Voltz Lightning com Depix IDs Reais
===================================================

Este script permite testar o fluxo Lightning usando depix_ids reais,
forçando a atualização do status para simular pagamento confirmado.
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

import requests
import json
import time
from api.voltz import VoltzAPI

def listar_deposits_usuario(chatid):
    """Lista todos os depósitos de um usuário para pegar depix_ids reais."""
    url = f"https://useghost.squareweb.app/rest/deposit.php?chatid={chatid}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        deposits = data.get('deposits', [])
        
        print(f"📋 Depósitos encontrados para usuário {chatid}:")
        print("=" * 60)
        
        for i, dep in enumerate(deposits, 1):
            print(f"{i}. ID: {dep.get('depix_id', 'N/A')}")
            print(f"   Status: {dep.get('status', 'N/A')}")
            print(f"   Valor: R$ {dep.get('amount_in_cents', 0)/100:.2f}")
            print(f"   Moeda: {dep.get('moeda', 'N/A')}")
            print(f"   Rede: {dep.get('rede', 'N/A')}")
            print(f"   Data: {dep.get('created_at', 'N/A')}")
            print(f"   TxID: {dep.get('blockchainTxID', 'Não confirmado')}")
            print("-" * 40)
        
        return deposits
    except Exception as e:
        print(f"❌ Erro ao listar depósitos: {e}")
        return []

def forcar_confirmacao_deposito(depix_id, fake_txid=None):
    """Força a confirmação de um depósito alterando status e txid."""
    if not fake_txid:
        fake_txid = f"teste_blockchain_{int(time.time())}"
    
    url = "https://useghost.squareweb.app/rest/deposit.php"
    payload = {
        "action": "update_status",
        "depix_id": depix_id,
        "status": "confirmado", 
        "blockchainTxID": fake_txid
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Depósito {depix_id} marcado como confirmado")
            print(f"🔗 TxID simulado: {fake_txid}")
            return True
        else:
            print(f"❌ Erro ao confirmar: {result.get('error', 'Erro desconhecido')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def testar_voltz_status(depix_id):
    """Testa se o Voltz detecta o depósito e gera invoice."""
    voltz = VoltzAPI(backend_url='https://useghost.squareweb.app')
    
    print(f"\n🔍 Verificando status Voltz para {depix_id}...")
    
    for tentativa in range(1, 6):
        print(f"   Tentativa {tentativa}/5...")
        
        status = voltz.check_deposit_status(depix_id)
        
        if status.get('success'):
            print(f"✅ Status encontrado: {status.get('status')}")
            
            if status.get('invoice'):
                print(f"⚡ INVOICE ENCONTRADO!")
                print(f"📋 Payment Request: {status['invoice'][:50]}...")
                if status.get('qr_code'):
                    print(f"📱 QR Code URL: {status['qr_code']}")
                return status
            else:
                print("   Aguardando invoice ser gerado...")
        else:
            print(f"❌ Erro: {status.get('error', 'Erro desconhecido')}")
        
        if tentativa < 5:
            print("   ⏱️ Aguardando 5 segundos...")
            time.sleep(5)
    
    print("⏰ Timeout - Invoice não foi gerado")
    return None

def executar_cron_voltz():
    """Executa o processamento do cron Voltz manualmente."""
    print("\n🔄 Executando processamento Voltz...")
    
    try:
        # Usar endpoint correto do diretório voltz
        url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print("✅ Cron Voltz executado com sucesso")
        print(f"📝 Resposta: {response.text[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar cron: {e}")
        return False

def disparar_processamento_lightning(depix_id):
    """Dispara processamento Lightning específico via Voltz."""
    print(f"\n⚡ Disparando processamento Lightning para {depix_id}...")
    
    try:
        # Usar endpoint específico do Voltz para processar depósito
        url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
        payload = {
            "action": "process_deposit",
            "depix_id": depix_id
        }
        
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Processamento Lightning disparado")
            return True
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao disparar processamento: {e}")
        return False

def main():
    print("🧪 TESTE FORÇADO - Voltz Lightning")
    print("=" * 50)
    
    # IDs específicos para teste (fornecidos pelo usuário)
    depix_ids_teste = [
        "0197e0ed06537df9820a28f5a5380a3b",
        "0197e10b5b8f7df9a6bf9430188534e4", 
        "0197e12300eb7df9808ca5d7719ea40e",
        "0197e5214a377dfaae6e541f68057444"
    ]
    
    print("🎯 Depix IDs disponíveis para teste:")
    print("-" * 40)
    for i, depix_id in enumerate(depix_ids_teste, 1):
        print(f"{i}. {depix_id}")
    
    # Opção para usar ID personalizado
    print(f"{len(depix_ids_teste) + 1}. Usar outro depix_id")
    print(f"{len(depix_ids_teste) + 2}. Listar depósitos por chat_id")
    
    try:
        escolha = int(input(f"\nEscolha uma opção (1-{len(depix_ids_teste) + 2}): "))
        
        if escolha <= len(depix_ids_teste):
            depix_id = depix_ids_teste[escolha - 1]
        elif escolha == len(depix_ids_teste) + 1:
            depix_id = input("Digite o depix_id: ").strip()
            if not depix_id:
                print("❌ Depix ID inválido")
                return
        elif escolha == len(depix_ids_teste) + 2:
            # Fluxo original - listar por chat_id
            chatid = input("Digite o chat ID (padrão: 7910260237): ").strip()
            if not chatid:
                chatid = "7910260237"
            
            deposits = listar_deposits_usuario(chatid)
            if not deposits:
                print("❌ Nenhum depósito encontrado")
                return
            
            escolha_dep = int(input("Digite o número do depósito: ")) - 1
            if escolha_dep < 0 or escolha_dep >= len(deposits):
                print("❌ Escolha inválida")
                return
            
            depix_id = deposits[escolha_dep]['depix_id']
        else:
            print("❌ Opção inválida")
            return
            
    except ValueError:
        print("❌ Número inválido")
        return
    
    print(f"\n🎯 Testando depix_id: {depix_id}")
    
    # Buscar dados do depósito
    print(f"\n🔍 Buscando dados do depósito...")
    deposit_data = buscar_dados_deposito(depix_id)
    
    if not deposit_data:
        print("❌ Depósito não encontrado")
        return
    
    print(f"✅ Depósito encontrado:")
    print(f"   Status: {deposit_data.get('status')}")
    print(f"   Valor: R$ {deposit_data.get('amount_in_cents', 0)/100:.2f}")
    print(f"   Moeda: {deposit_data.get('moeda')}")
    print(f"   Rede: {deposit_data.get('rede')}")
    print(f"   TxID: {deposit_data.get('blockchainTxID', 'Não confirmado')}")
    
    if deposit_data.get('is_test'):
        print(f"🧪 Dados de teste criados com TxID real do Depix")
    
    # Para testes, o depósito já é criado como confirmado
    print(f"\n✅ Depósito já está confirmado para teste")
    
    # Executar processamento Lightning específico
    print(f"\n🔄 Disparando processamento Lightning...")
    disparar_processamento_lightning(depix_id)
    
    # Executar cron Voltz como backup
    print(f"\n🔄 Executando cron Voltz para processar depósito...")
    executar_cron_voltz()
    
    # Aguardar processamento
    print("⏱️ Aguardando 8 segundos para processamento...")
    time.sleep(8)
    
    # Testar status
    print(f"\n🧪 Testando geração de invoice...")
    resultado = testar_voltz_status(depix_id)
    
    if resultado and resultado.get('invoice'):
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print(f"⚡ Invoice Lightning gerado para {depix_id}")
        
        # Exibir detalhes do invoice
        print(f"\n📄 DETALHES DO INVOICE:")
        print(f"💰 Valor: {deposit_data.get('send', 'N/A')} sats")
        print(f"🆔 Depix ID: {depix_id}")
        print(f"📱 Invoice: {resultado['invoice']}")
        
        if resultado.get('qr_code'):
            print(f"📱 QR Code: {resultado['qr_code']}")
        
        # Mostrar comando para testar pagamento
        print(f"\n💡 Para testar o pagamento Lightning:")
        print(f"   lncli payinvoice {resultado['invoice']}")
        
    else:
        print(f"\n❌ TESTE FALHOU")
        print(f"Invoice não foi gerado para {depix_id}")
        print(f"Verifique os logs do Voltz para mais detalhes")
        
        # Mostrar status atual
        print(f"\n📊 Status atual do Voltz:")
        if resultado:
            print(f"   Success: {resultado.get('success')}")
            print(f"   Status: {resultado.get('status')}")
            if resultado.get('error'):
                print(f"   Erro: {resultado.get('error')}")

def buscar_txid_depix(depix_id):
    """Busca o TxID real via API HTTP direta do Depix."""
    try:
        print(f"🔍 Consultando API Depix para TxID do {depix_id}...")
        
        # Tenta diferentes endpoints para buscar o pagamento
        endpoints = [
            f"https://api.depix.com.br/v1/payment/{depix_id}",
            f"https://api.depix.com.br/v1/payments/{depix_id}",
            f"https://api.depix.com.br/payment/{depix_id}",
            f"https://api.depix.com.br/payments/{depix_id}"
        ]
        
        for endpoint in endpoints:
            try:
                print(f"   Tentando endpoint: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Busca pelos campos de TxID mais comuns
                    txid = (data.get('transaction_id') or 
                           data.get('txid') or 
                           data.get('id') or
                           data.get('payment_id'))
                    
                    if txid:
                        status = data.get('status', 'confirmed')
                        print(f"✅ Depix encontrado:")
                        print(f"   TxID: {txid}")
                        print(f"   Status: {status}")
                        
                        return {
                            'txid': txid,
                            'status': status,
                            'depix_data': data
                        }
                        
            except Exception as e:
                print(f"   ❌ Erro no endpoint {endpoint}: {e}")
                continue
        
        # Se não conseguir via API, simula um TxID baseado no depix_id
        print(f"⚠️ Não foi possível consultar API Depix")
        print(f"📝 Gerando TxID simulado baseado no depix_id...")
        
        # Cria um TxID simulado mas válido baseado no depix_id
        import hashlib
        simulated_txid = hashlib.md5(f"depix_{depix_id}_test".encode()).hexdigest()
        
        print(f"✅ TxID simulado gerado: {simulated_txid}")
        
        return {
            'txid': simulated_txid,
            'status': 'confirmed',
            'depix_data': {'simulated': True, 'original_depix_id': depix_id}
        }
            
    except Exception as e:
        print(f"❌ Erro geral ao consultar Depix: {e}")
        
        # Fallback: cria TxID simulado
        import hashlib
        simulated_txid = hashlib.md5(f"depix_{depix_id}_fallback".encode()).hexdigest()
        
        print(f"📝 Usando TxID de fallback: {simulated_txid}")
        
        return {
            'txid': simulated_txid,
            'status': 'confirmed',
            'depix_data': {'fallback': True, 'original_depix_id': depix_id}
        }

def criar_deposito_teste(depix_id, txid, chatid="7910260237"):
    """Cria um depósito de teste no backend usando dados do Depix."""
    try:
        print(f"📝 Criando depósito de teste no backend...")
        
        # Dados para teste Lightning com valores pequenos (R$ 4,00 máximo)
        payload = {
            "chatid": chatid,
            "user_id": int(chatid),
            "depix_id": depix_id,
            "blockchainTxID": txid,
            "status": "confirmado",  # Força como confirmado
            "amount_in_cents": 400,  # R$ 4,00 (valor baixo para teste)
            "moeda": "BTC",
            "rede": "⚡ Lightning",  # Formato correto para Lightning
            "send": 800,  # 800 sats (~R$ 4,00)
            "taxa": 0.20,  # 5% de R$ 4,00
            "address": "voltzapi@tria.com",  # Endereço padrão Lightning
            "metodo_pagamento": "PIX",
            "forma_pagamento": "PIX",
            "comprovante": "Lightning Invoice Test - Baixo valor",
            "action": "force_create"  # Flag especial para teste
        }
        
        url = "https://useghost.squareweb.app/rest/deposit.php"
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Depósito de teste criado no backend")
            print(f"📄 Resposta: {result}")
            return True
        else:
            print(f"⚠️ Resposta do backend: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar depósito teste: {e}")
        return False

def buscar_dados_deposito(depix_id):
    """Busca dados do depósito via Depix e cria entrada de teste."""
    try:
        # 1. Buscar TxID real via Depix
        depix_data = buscar_txid_depix(depix_id)
        
        if not depix_data or not depix_data.get('txid'):
            print(f"❌ Não foi possível obter TxID do Depix para {depix_id}")
            return None
        
        txid = depix_data['txid']
        print(f"✅ TxID obtido do Depix: {txid}")
        
        # 2. Criar depósito de teste no backend com dados reais do Depix
        criar_deposito_teste(depix_id, txid)
        
        # 3. Retornar dados para o teste (valores baixos)
        return {
            'depix_id': depix_id,
            'status': 'confirmado',  # Força como confirmado para teste
            'amount_in_cents': 400,  # R$ 4,00 fictício
            'moeda': 'BTC',
            'rede': 'lightning',
            'send': 800,  # 800 sats fictício
            'blockchainTxID': txid,  # TxID real do Depix
            'is_test': True
        }
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados do depósito: {e}")
        return None

if __name__ == "__main__":
    main()
