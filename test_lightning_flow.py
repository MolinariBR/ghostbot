#!/usr/bin/env python3
"""
Teste do fluxo completo de Lightning Address
Simula o processo completo: PIX → confirmação → Lightning Address → pagamento
"""
import asyncio
import requests
import json
from lightning_address_handler import is_lightning_input, LightningAddressHandler

def test_lightning_detection():
    """Testa detecção de Lightning Address/Invoice"""
    print("🧪 TESTE: Detecção de Lightning Address/Invoice")
    
    # Testes de Lightning Address
    lightning_addresses = [
        "user@wallet.com",
        "test@phoenixwallet.me",
        "satoshi@strike.me",
        "test123@walletofsatoshi.com"
    ]
    
    # Testes de BOLT11
    bolt11_invoices = [
        "lnbc1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "lntb1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "lnbc15u1p0xxxx"  # Muito curto - deve falhar
    ]
    
    # Testes negativos
    invalid_inputs = [
        "usuario@",
        "@domain.com",
        "user@domain",
        "lnbc123",  # Muito curto
        "not_lightning",
        "12345",
        "bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    ]
    
    print("\n✅ Testando Lightning Addresses válidos:")
    for addr in lightning_addresses:
        result = is_lightning_input(addr)
        print(f"   {addr}: {'✅' if result else '❌'}")
    
    print("\n✅ Testando BOLT11 Invoices:")
    for invoice in bolt11_invoices:
        result = is_lightning_input(invoice)
        print(f"   {invoice[:30]}...: {'✅' if result else '❌'}")
    
    print("\n❌ Testando entradas inválidas:")
    for invalid in invalid_inputs:
        result = is_lightning_input(invalid)
        print(f"   {invalid}: {'❌ (correto)' if not result else '✅ (incorreto - deveria falhar)'}")

def test_backend_connectivity():
    """Testa conectividade com backend"""
    print("\n🌐 TESTE: Conectividade com Backend")
    
    handler = LightningAddressHandler()
    
    # Testa endpoint principal
    print("\n📡 Testando endpoint principal...")
    try:
        response = requests.get(
            "https://ghostbackend.squarecloud.app/api/process_lightning_address.php",
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 405:  # Method Not Allowed é esperado para GET
            print("   ✅ Endpoint principal está online (405 = método não permitido, mas servidor responde)")
        else:
            print(f"   ⚠️  Resposta inesperada: {response.text[:100]}")
    except requests.RequestException as e:
        print(f"   ❌ Erro: {e}")
    
    # Testa endpoint local
    print("\n🏠 Testando endpoint local...")
    try:
        response = requests.get(
            "http://localhost:8080/api/process_lightning_address.php",
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 405:
            print("   ✅ Endpoint local está online")
        else:
            print(f"   ⚠️  Resposta inesperada: {response.text[:100]}")
    except requests.RequestException as e:
        print(f"   ❌ Erro: {e}")

def test_database_deposit():
    """Testa se há depósitos pendentes no banco"""
    print("\n💾 TESTE: Depósitos Pendentes no Banco")
    
    try:
        # Testa endpoint de depósitos
        response = requests.get(
            "https://ghostbackend.squarecloud.app/rest/deposit.php",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            deposits = data.get('deposits', [])
            print(f"   📊 Total de depósitos: {len(deposits)}")
            
            # Filtra depósitos Lightning pendentes
            lightning_pending = [
                d for d in deposits 
                if d.get('rede') in ['lightning', '⚡ Lightning'] 
                and d.get('status') in ['confirmado', 'pending', 'awaiting_client_invoice']
                and not d.get('blockchainTxID')
            ]
            
            print(f"   ⚡ Lightning pendentes: {len(lightning_pending)}")
            
            for deposit in lightning_pending[:3]:  # Mostra até 3
                print(f"   📋 ID: {deposit.get('id')}, ChatID: {deposit.get('chatid')}, "
                      f"Valor: {deposit.get('send')} BTC, Status: {deposit.get('status')}")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"   ❌ Erro: {e}")

async def test_full_flow():
    """Testa o fluxo completo simulado"""
    print("\n🎯 TESTE: Fluxo Completo Simulado")
    
    # Simula dados de usuário
    chat_id = "7910260237"  # ID de teste
    lightning_address = "test@phoenixwallet.me"
    
    print(f"   👤 Chat ID: {chat_id}")
    print(f"   ⚡ Lightning Address: {lightning_address}")
    
    # Verifica se é válido
    if is_lightning_input(lightning_address):
        print("   ✅ Lightning Address válido")
    else:
        print("   ❌ Lightning Address inválido")
        return
    
    # Simula chamada ao backend
    handler = LightningAddressHandler()
    
    print("   🔄 Testando chamada ao backend...")
    try:
        # Simula payload
        payload = {
            "chat_id": chat_id,
            "user_input": lightning_address
        }
        
        # Tenta chamada real (só para teste de conectividade)
        response = requests.post(
            "https://ghostbackend.squarecloud.app/api/process_lightning_address.php",
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   📊 Resposta: {result}")
        else:
            print(f"   ⚠️  Erro: {response.text[:200]}")
            
    except requests.RequestException as e:
        print(f"   ❌ Erro de conexão: {e}")

def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DO FLUXO LIGHTNING")
    print("=" * 60)
    
    test_lightning_detection()
    test_backend_connectivity()
    test_database_deposit()
    asyncio.run(test_full_flow())
    
    print("\n" + "=" * 60)
    print("🏁 TESTES CONCLUÍDOS")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Inicie o bot: python bot.py")
    print("   2. Faça uma compra PIX")
    print("   3. Aguarde confirmação do PIX")
    print("   4. Digite um Lightning Address")
    print("   5. Verifique se o pagamento foi processado")

if __name__ == "__main__":
    main()
