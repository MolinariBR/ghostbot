#!/usr/bin/env python3
"""
TESTE LIGHTNING COM INVOICE REAL - Ghost P2P
============================================

Script para testar pagamentos Lightning com invoices reais.
"""

import requests
import json
import time
import sys

def gerar_invoice_teste():
    """Instrui como gerar um invoice real para teste."""
    print("📋 COMO GERAR INVOICE REAL PARA TESTE")
    print("=" * 50)
    print("💡 OPÇÕES PARA GERAR INVOICE:")
    print()
    print("1️⃣ WALLET OF SATOSHI (Mobile):")
    print("   • Abrir app Wallet of Satoshi")
    print("   • Clicar em 'Receive'")
    print("   • Digitar valor: 1000 sats")
    print("   • Copiar invoice gerado")
    print()
    print("2️⃣ PHOENIX WALLET (Mobile):")
    print("   • Abrir Phoenix Wallet")
    print("   • Clicar em 'Receive'")
    print("   • Digitar: 1000 sats")
    print("   • Copiar payment request")
    print()
    print("3️⃣ BLUE WALLET (Mobile):")
    print("   • Criar Lightning Wallet")
    print("   • Clicar 'Receive'")
    print("   • Valor: 1000 sats")
    print("   • Copiar invoice")
    print()
    print("4️⃣ LINHA DE COMANDO (LND/CLN):")
    print("   lncli addinvoice --amt 1000 --memo 'Teste Ghost P2P'")
    print("   lightning-cli invoice 1000000 'teste' 'Ghost P2P'")
    print()
    print("⚠️ IMPORTANTE:")
    print("   • Invoice deve começar com 'lnbc' (mainnet) ou 'lntb' (testnet)")
    print("   • Valor: 1000 sats (~R$ 2,00)")
    print("   • Invoice expira em ~1 hora")

def validar_invoice(invoice):
    """Valida formato básico do invoice Lightning."""
    if not invoice:
        return False, "Invoice vazio"
    
    invoice = invoice.strip()
    
    if not (invoice.startswith('lnbc') or invoice.startswith('lntb')):
        return False, "Invoice deve começar com 'lnbc' (mainnet) ou 'lntb' (testnet)"
    
    if len(invoice) < 50:
        return False, "Invoice muito curto (mínimo 50 caracteres)"
    
    if len(invoice) > 1000:
        return False, "Invoice muito longo (máximo 1000 caracteres)"
    
    return True, "Invoice válido"

def criar_deposito_real():
    """Cria um depósito real para teste Lightning."""
    print("\n🆕 CRIANDO DEPÓSITO REAL PARA TESTE")
    print("=" * 50)
    
    url = "https://useghost.squareweb.app/rest/deposit.php"
    depix_id = f"real_test_{int(time.time())}"
    
    payload = {
        "chatid": "7910260237",
        "user_id": 7910260237,
        "depix_id": depix_id,
        "status": "confirmado",  # PIX já foi pago
        "amount_in_cents": 200,  # R$ 2,00
        "moeda": "BTC", 
        "rede": "⚡ Lightning",
        "send": 1000,  # 1000 sats
        "taxa": 0.10,  # R$ 0,10
        "address": "voltzapi@tria.com",
        "metodo_pagamento": "PIX",
        "forma_pagamento": "PIX",
        "comprovante": "PIX confirmado - Teste real Lightning",
        "action": "create"
    }
    
    print(f"📝 Depix ID: {depix_id}")
    print(f"💰 Valor PIX: R$ 2,00")
    print(f"⚡ BTC para enviar: 1000 sats")
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Depósito criado: {result}")
            return depix_id
        else:
            print(f"   ❌ Erro: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def processar_pagamento_real(depix_id, client_invoice):
    """Processa pagamento Lightning real."""
    print(f"\n⚡ PROCESSAMENTO PAGAMENTO REAL")
    print("=" * 50)
    print(f"🎯 Depix ID: {depix_id}")
    print(f"📋 Invoice: {client_invoice[:50]}...")
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    payload = {
        "action": "pay_invoice",
        "depix_id": depix_id,
        "client_invoice": client_invoice
    }
    
    print("⚠️ ATENÇÃO: Este pagamento será REAL!")
    print("💰 1000 sats serão enviados para a carteira fornecida")
    
    confirmacao = input("\n🤔 Confirmar pagamento real? (sim/NAO): ").strip().lower()
    
    if confirmacao not in ['sim', 's', 'yes', 'y']:
        print("❌ Pagamento cancelado pelo usuário")
        return None
    
    print("\n🚀 Enviando pagamento Lightning...")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📄 JSON: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print(f"\n🎉 PAGAMENTO REALIZADO COM SUCESSO!")
                print(f"   📄 Payment Hash: {data.get('payment_hash')}")
                if data.get('preimage'):
                    print(f"   🔑 Preimage: {data.get('preimage')}")
                print(f"   💰 Taxa: {data.get('fee_msat', 0)} msat")
                print(f"   📱 Invoice pago: {client_invoice}")
                return data
            else:
                print(f"\n❌ PAGAMENTO FALHOU!")
                print(f"   Erro: {data.get('error')}")
                return None
        else:
            print(f"\n❌ Erro HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"\n❌ Erro de conexão: {e}")
        return None

def verificar_saldo_antes_depois():
    """Verifica saldo do nó antes e depois do pagamento."""
    print(f"\n💰 VERIFICAÇÃO DE SALDO")
    print("=" * 50)
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    payload = {"action": "check_balance"}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                balance = data.get('balance', {})
                sats = balance.get('balance', 0)
                print(f"   💰 Saldo atual: {sats:,} sats (~R$ {sats/50000:.2f})")
                return sats
            else:
                print(f"   ❌ Erro: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    return None

def main():
    print("🧪 TESTE LIGHTNING COM INVOICE REAL")
    print("=" * 60)
    print("⚠️ ESTE TESTE ENVOLVE PAGAMENTO REAL DE 1000 SATS!")
    print("=" * 60)
    
    # 1. Verificar saldo inicial
    print("1️⃣ Verificando saldo inicial...")
    saldo_inicial = verificar_saldo_antes_depois()
    
    if not saldo_inicial or saldo_inicial < 2000:
        print("❌ Saldo insuficiente para teste (mínimo: 2000 sats)")
        return
    
    # 2. Instruções para gerar invoice
    gerar_invoice_teste()
    
    # 3. Solicitar invoice do usuário
    print("\n📋 FORNECER INVOICE LIGHTNING")
    print("=" * 50)
    client_invoice = input("🔮 Cole seu invoice Lightning aqui: ").strip()
    
    # 4. Validar invoice
    valido, mensagem = validar_invoice(client_invoice)
    
    if not valido:
        print(f"❌ Invoice inválido: {mensagem}")
        return
    
    print(f"✅ Invoice válido: {mensagem}")
    
    # 5. Criar depósito
    depix_id = criar_deposito_real()
    
    if not depix_id:
        print("❌ Falha na criação do depósito")
        return
    
    # 6. Aguardar
    print("\n⏱️ Aguardando 3 segundos...")
    time.sleep(3)
    
    # 7. Processar pagamento
    resultado = processar_pagamento_real(depix_id, client_invoice)
    
    # 8. Verificar saldo final
    print("\n2️⃣ Verificando saldo final...")
    saldo_final = verificar_saldo_antes_depois()
    
    if saldo_inicial and saldo_final:
        diferenca = saldo_inicial - saldo_final
        print(f"📊 Diferença: -{diferenca} sats")
    
    # 9. Resumo
    print(f"\n📋 RESUMO DO TESTE:")
    if resultado and resultado.get('success'):
        print(f"✅ Pagamento Lightning realizado com sucesso!")
        print(f"✅ Sistema Ghost P2P + Voltz funcionando!")
        print(f"✅ Cliente recebeu 1000 sats via Lightning!")
    else:
        print(f"❌ Teste falhou - verificar logs e configuração")
    
    print(f"\n🎯 PRÓXIMO PASSO: Integrar no bot Telegram!")

if __name__ == "__main__":
    main()
