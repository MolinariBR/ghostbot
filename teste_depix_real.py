#!/usr/bin/env python3
"""
FORÇAR TESTE COM DEPIX_IDS REAIS
=================================

Cria entradas de teste no banco usando os depix_ids reais fornecidos,
depois simula o webhook para disparar o fluxo Lightning.
"""

import requests
import json
import time

def criar_deposito_forcado(depix_id, chat_id="123456789"):
    """
    Força a criação de um depósito no banco com o depix_id fornecido.
    """
    print(f"🆕 Criando depósito forçado para {depix_id}...")
    
    # Cria via endpoint REST
    url = "https://useghost.squareweb.app/rest/deposit.php"
    payload = {
        "chatid": str(chat_id),
        "moeda": "BTC",
        "rede": "⚡ Lightning",
        "amount_in_cents": 10000,  # R$ 100,00
        "taxa": 5.0,  # 5%
        "address": "voltzapi@tria.com",
        "metodo_pagamento": "PIX",
        "send": 271428,  # sats (aproximadamente)
        "depix_id": depix_id,
        "status": "pending",
        "user_id": int(chat_id),
        "comprovante": "Lightning Invoice"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Depósito criado com sucesso!")
                return True
            else:
                print(f"❌ Erro na criação: {result}")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def simular_webhook_simplificado(depix_id):
    """
    Simula webhook sem token (para teste local).
    """
    print(f"\n🔗 Simulando webhook para {depix_id}...")
    
    # Tenta primeiro via endpoint direto do Lightning
    lightning_url = "https://useghost.squareweb.app/api/lightning_trigger.php"
    payload = {"depix_id": depix_id}
    
    try:
        response = requests.post(lightning_url, json=payload, timeout=15)
        print(f"Lightning trigger - Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro Lightning trigger: {e}")
        return False

def verificar_invoice(depix_id):
    """
    Verifica se foi gerado invoice via Voltz.
    """
    print(f"\n⚡ Verificando invoice para {depix_id}...")
    
    import sys
    sys.path.append('/home/mau/bot/ghost')
    
    try:
        from api.voltz import VoltzAPI
        voltz = VoltzAPI(backend_url='https://useghost.squareweb.app')
        
        for i in range(1, 6):
            print(f"   Tentativa {i}/5...")
            
            status = voltz.check_deposit_status(depix_id)
            print(f"   Resposta: {status}")
            
            if status.get('invoice'):
                print(f"\n🎉 INVOICE ENCONTRADO!")
                print(f"Invoice: {status['invoice']}")
                return status
            
            if i < 5:
                time.sleep(3)
        
        print(f"⏰ Timeout - Invoice não gerado")
        return None
        
    except Exception as e:
        print(f"Erro na verificação: {e}")
        return None

def main():
    print("🧪 TESTE FORÇADO COM DEPIX_IDS REAIS")
    print("=" * 50)
    
    # Seus depix_ids
    depix_ids = [
        "0197e0ed06537df9820a28f5a5380a3b",
        "0197e10b5b8f7df9a6bf9430188534e4",
        "0197e12300eb7df9808ca5d7719ea40e",
        "0197e5214a377dfaae6e541f68057444"
    ]
    
    print("🎯 Depix IDs disponíveis:")
    for i, depix_id in enumerate(depix_ids, 1):
        print(f"{i}. {depix_id}")
    
    try:
        escolha = int(input(f"\nEscolha (1-{len(depix_ids)}): ")) - 1
        if escolha < 0 or escolha >= len(depix_ids):
            print("❌ Escolha inválida")
            return
        
        depix_id = depix_ids[escolha]
        
    except ValueError:
        print("❌ Número inválido")
        return
    
    print(f"\n🎯 Testando: {depix_id}")
    
    # 1. Criar depósito forçado
    print(f"\n🚀 FASE 1: Criando depósito")
    if not criar_deposito_forcado(depix_id):
        print("❌ Falha na criação, mas continuando...")
    
    time.sleep(2)
    
    # 2. Simular webhook/trigger
    print(f"\n🚀 FASE 2: Disparando processamento")
    if not simular_webhook_simplificado(depix_id):
        print("❌ Falha no trigger, mas continuando...")
    
    time.sleep(3)
    
    # 3. Verificar invoice
    print(f"\n🚀 FASE 3: Verificando invoice")
    resultado = verificar_invoice(depix_id)
    
    if resultado and resultado.get('invoice'):
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print(f"✅ Depix ID: {depix_id}")
        print(f"✅ Invoice: {resultado['invoice'][:50]}...")
        
        print(f"\n💡 Para testar pagamento:")
        print(f"lncli payinvoice {resultado['invoice']}")
        
    else:
        print(f"\n❌ TESTE FALHOU")
        print(f"Verifique:")
        print(f"• Se o depósito foi criado no banco")
        print(f"• Se o Voltz está processando")
        print(f"• Se o Lightning Node está online")

if __name__ == "__main__":
    main()
