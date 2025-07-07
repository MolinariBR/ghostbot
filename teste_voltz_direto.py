#!/usr/bin/env python3
"""
TESTE DIRETO VOLTZ - Apenas endpoints que funcionam
===================================================

Script simplificado que usa apenas os endpoints do diretório /voltz/
que estão funcionando corretamente.
"""

import requests
import json
import time
import sys
import os

# Adiciona path do ghost
sys.path.append('/home/mau/bot/ghost')

def criar_deposito_voltz_direto(depix_id, chat_id="123456789"):
    """
    Cria depósito diretamente via REST API (que funciona).
    """
    print(f"🆕 Criando depósito Lightning via REST API...")
    
    # TxID simulado mas válido
    import hashlib
    txid = hashlib.md5(f"voltz_test_{depix_id}_{int(time.time())}".encode()).hexdigest()
    
    payload = {
        "chatid": str(chat_id),
        "user_id": int(chat_id),
        "depix_id": depix_id,
        "blockchainTxID": txid,
        "status": "confirmado",
        "amount_in_cents": 400,  # R$ 4,00 (valor baixo para teste)
        "moeda": "BTC",
        "rede": "⚡ Lightning",
        "send": 800,  # 800 sats (~R$ 4,00)
        "taxa": 0.20,  # 5% de R$ 4,00  
        "address": "voltzapi@tria.com",
        "metodo_pagamento": "PIX",
        "forma_pagamento": "PIX",
        "comprovante": "Lightning Invoice Test - Baixo valor"
    }
    
    try:
        url = "https://useghost.squareweb.app/rest/deposit.php"
        response = requests.post(url, json=payload, timeout=15)
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Depósito criado!")
                print(f"🆔 Depix ID: {depix_id}")
                print(f"🔗 TxID: {txid}")
                return True
                
        print(f"⚠️ Problema na criação")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def processar_via_voltz_rest(depix_id):
    """
    Processa depósito via voltz_rest.php (endpoint que funciona).
    """
    print(f"\n🔄 Processando via Voltz REST...")
    
    try:
        # Teste 1: GET simples (cron)
        url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
        response = requests.get(url, timeout=30)
        
        print(f"GET Status: {response.status_code}")
        print(f"GET Resposta: {response.text[:200]}...")
        
        time.sleep(2)
        
        # Teste 2: POST com depix_id específico
        payload = {
            "action": "process_deposit",
            "depix_id": depix_id
        }
        
        response = requests.post(url, json=payload, timeout=30)
        print(f"POST Status: {response.status_code}")
        print(f"POST Resposta: {response.text[:200]}...")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False

def verificar_invoice_voltz(depix_id):
    """
    Verifica invoice via voltz_status.php (endpoint que funciona).
    """
    print(f"\n⚡ Verificando invoice via Voltz Status...")
    
    try:
        # Teste direto via HTTP
        url = "https://useghost.squareweb.app/voltz/voltz_status.php"
        
        # Teste 1: POST com depix_id
        payload = {"depix_id": depix_id}
        response = requests.post(url, json=payload, timeout=15)
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('invoice'):
                    print(f"\n🎉 INVOICE ENCONTRADO!")
                    print(f"Invoice: {data['invoice']}")
                    return data
                else:
                    print(f"⏳ Invoice ainda não gerado")
                    return None
            except json.JSONDecodeError:
                print(f"📝 Resposta não é JSON válido")
                return None
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return None

def teste_completo_voltz(depix_id):
    """
    Executa teste completo usando apenas endpoints Voltz que funcionam.
    """
    print(f"🧪 TESTE COMPLETO VOLTZ - {depix_id}")
    print("=" * 50)
    
    # Fase 1: Criar depósito
    print(f"\n🚀 FASE 1: Criando depósito")
    if not criar_deposito_voltz_direto(depix_id):
        print("❌ Falha na criação, mas continuando...")
    
    time.sleep(3)
    
    # Fase 2: Processar
    print(f"\n🚀 FASE 2: Processando via Voltz")
    if not processar_via_voltz_rest(depix_id):
        print("❌ Falha no processamento, mas continuando...")
    
    time.sleep(5)
    
    # Fase 3: Verificar invoice (múltiplas tentativas)
    print(f"\n🚀 FASE 3: Verificando invoice")
    for tentativa in range(1, 6):
        print(f"\n   Tentativa {tentativa}/5...")
        
        resultado = verificar_invoice_voltz(depix_id)
        
        if resultado and resultado.get('invoice'):
            print(f"\n🎉 SUCESSO! Invoice gerado:")
            print(f"🆔 Depix ID: {depix_id}")
            print(f"⚡ Invoice: {resultado['invoice']}")
            
            if resultado.get('qr_code'):
                print(f"📱 QR Code: {resultado['qr_code']}")
            
            print(f"\n💡 Para testar pagamento:")
            print(f"lncli payinvoice {resultado['invoice']}")
            
            return True
        
        if tentativa < 5:
            print(f"   ⏱️ Aguardando 5 segundos...")
            time.sleep(5)
    
    print(f"\n❌ Invoice não foi gerado após 5 tentativas")
    return False

def main():
    print("🧪 TESTE DIRETO VOLTZ")
    print("=" * 30)
    
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
    
    # Executar teste completo
    sucesso = teste_completo_voltz(depix_id)
    
    if sucesso:
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print(f"\n❌ TESTE FALHOU")
        print(f"Possíveis causas:")
        print(f"• Lightning Node offline")
        print(f"• Voltz não está processando Lightning")
        print(f"• Configuração incorreta")

if __name__ == "__main__":
    main()
