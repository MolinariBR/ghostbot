#!/usr/bin/env python3
"""
Script de teste para o validador de PIX
"""

import asyncio
import aiohttp
from config.config import BASE_URL

async def consultar_deposito_por_depix_id(depix_id: str):
    """
    Consulta os dados do depósito no backend.
    
    Args:
        depix_id: ID do depósito PIX
        
    Returns:
        Dicionário com os dados do depósito
    """
    try:
        url = f"{BASE_URL}/deposit.php"
        params = {"action": "get", "depix_id": depix_id}
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                print(f"[DEBUG] URL: {url}")
                print(f"[DEBUG] Params: {params}")
                print(f"[DEBUG] Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    print(f"[DEBUG] Error response: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def testar_depix_ids():
    """
    Testa os depix_id fornecidos pelo usuário
    """
    # Depix IDs fornecidos pelo usuário
    depix_ids = [
        "5ee0b16967f9e0f7d6eead010f1af9acf7be09a7203abe515958a84d5848e761",
        "965cd29f947c0a548c8199bbacb42a294aec3cd8f8f6cd935c45f52b6a8ddb2b",
        "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        "f1e2d3c4b5a6789012345678901234567890fedcba1234567890fedcba123456"
    ]
    
    print(f"🔍 Testando validador de PIX com {len(depix_ids)} depix_ids...")
    print(f"🌐 URL Base: {BASE_URL}")
    print("-" * 60)
    
    for i, depix_id in enumerate(depix_ids, 1):
        print(f"\n📋 Teste {i}/{len(depix_ids)}")
        print(f"🆔 Depix ID: {depix_id}")
        
        resultado = await consultar_deposito_por_depix_id(depix_id)
        
        if resultado.get("success") is False:
            print(f"❌ Erro: {resultado.get('error')}")
        elif "error" in resultado:
            print(f"❌ Erro: {resultado.get('error')}")
        else:
            print(f"✅ Sucesso!")
            print(f"   Status: {resultado.get('status', 'N/A')}")
            print(f"   Blockchain TxID: {resultado.get('blockchainTxID', 'N/A')}")
            print(f"   Valor: {resultado.get('amount_in_cents', 'N/A')} centavos")
            print(f"   Data: {resultado.get('created_at', 'N/A')}")
            
            # Verifica se tem blockchainTxID (pagamento confirmado)
            if resultado.get('blockchainTxID'):
                print(f"   🎉 PAGAMENTO CONFIRMADO! Blockchain TxID encontrado.")
            else:
                print(f"   ⏳ Pagamento ainda não confirmado (sem blockchainTxID)")
        
        print("-" * 40)

async def simular_verificacao_completa():
    """
    Simula o processo completo de verificação com tentativas
    """
    print("\n🔄 Simulando processo completo de verificação...")
    print("=" * 60)
    
    # Usa o primeiro depix_id para simular
    depix_id = "5ee0b16967f9e0f7d6eead010f1af9acf7be09a7203abe515958a84d5848e761"
    tentativas = 3
    
    for i in range(tentativas):
        print(f"\n🔄 Tentativa {i+1}/{tentativas}")
        
        resultado = await consultar_deposito_por_depix_id(depix_id)
        
        if resultado.get("blockchainTxID"):
            print("✅ PAGAMENTO CONFIRMADO!")
            print(f"🔗 Blockchain TxID: {resultado.get('blockchainTxID')}")
            print("📬 Próximo passo: Solicitar endereço Lightning")
            return True
        else:
            status = resultado.get("status", "pending")
            print(f"⏳ Aguardando confirmação... Status: {status}")
            
            if i < tentativas - 1:
                print("⏰ Aguardando 5 segundos antes da próxima tentativa...")
                await asyncio.sleep(5)
    
    print("❌ Pagamento não confirmado após todas as tentativas")
    print("📞 Orientar usuário para falar com atendente")
    return False

async def main():
    """
    Função principal do teste
    """
    print("🚀 Iniciando testes do validador de PIX")
    print("=" * 60)
    
    # Teste 1: Verificar todos os depix_ids
    await testar_depix_ids()
    
    # Teste 2: Simular processo completo
    await simular_verificacao_completa()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    asyncio.run(main()) 