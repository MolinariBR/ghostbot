#!/usr/bin/env python3
"""
TESTE DIRETO - Voltz com IDs específicos
========================================
Teste simples usando seus depix_ids reais.
"""

import requests
import time

def testar_depix_id(depix_id):
    """Testa um depix_id específico no Voltz."""
    print(f"\n🧪 TESTANDO: {depix_id}")
    print("=" * 50)
    
    # 1. Executar cron Voltz
    print("🔄 Executando cron Voltz...")
    try:
        cron_url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
        cron_resp = requests.get(cron_url, timeout=30)
        print(f"✅ Cron executado: {cron_resp.status_code}")
    except Exception as e:
        print(f"❌ Erro no cron: {e}")
    
    # 2. Aguardar processamento
    print("⏱️ Aguardando 3 segundos...")
    time.sleep(3)
    
    # 3. Verificar status
    print("🔍 Verificando status no Voltz...")
    try:
        status_url = "https://useghost.squareweb.app/voltz/voltz_status.php"
        payload = {"depix_id": depix_id}
        
        response = requests.post(status_url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        print(f"📊 Resposta do Voltz:")
        print(f"   Success: {result.get('success')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Depix ID: {result.get('depix_id')}")
        
        if result.get('invoice'):
            print(f"⚡ INVOICE ENCONTRADO!")
            print(f"📋 Payment Request: {result['invoice']}")
            if result.get('qr_code'):
                print(f"📱 QR Code: {result['qr_code']}")
            return True
        else:
            print(f"❌ Nenhum invoice encontrado")
            if result.get('deposit'):
                dep = result['deposit']
                print(f"📋 Dados do depósito:")
                print(f"   Status: {dep.get('status')}")
                print(f"   Valor: R$ {dep.get('amount_in_cents', 0)/100:.2f}")
                print(f"   Moeda: {dep.get('moeda')}")
                print(f"   TxID: {dep.get('blockchainTxID', 'Não confirmado')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")
        return False

def main():
    print("🚀 TESTE DIRETO - Seus Depix IDs")
    print("=" * 40)
    
    # Seus IDs específicos
    depix_ids = [
        "0197e0ed06537df9820a28f5a5380a3b",
        "0197e10b5b8f7df9a6bf9430188534e4", 
        "0197e12300eb7df9808ca5d7719ea40e",
        "0197e5214a377dfaae6e541f68057444"
    ]
    
    sucessos = 0
    
    for i, depix_id in enumerate(depix_ids, 1):
        print(f"\n🎯 TESTE {i}/{len(depix_ids)}")
        sucesso = testar_depix_id(depix_id)
        if sucesso:
            sucessos += 1
        
        if i < len(depix_ids):
            print("⏸️ Pausando 5 segundos entre testes...")
            time.sleep(5)
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"✅ Sucessos: {sucessos}/{len(depix_ids)}")
    print(f"❌ Falhas: {len(depix_ids) - sucessos}/{len(depix_ids)}")
    
    if sucessos > 0:
        print(f"🎉 TESTE CONCLUÍDO - {sucessos} invoice(s) gerado(s)!")
    else:
        print(f"⚠️ Nenhum invoice foi gerado")
        print(f"💡 Possíveis motivos:")
        print(f"   - Depósitos não estão com status 'confirmado'")
        print(f"   - Voltz não encontra os dados necessários")
        print(f"   - Problema na configuração do Lightning")

if __name__ == "__main__":
    main()
