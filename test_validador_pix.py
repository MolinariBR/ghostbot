#!/usr/bin/env python3
"""
Script de teste para o validador de depósito PIX
Testa as APIs do backend para verificar se estão funcionando corretamente
"""

import asyncio
import aiohttp
from config.config import BASE_URL

async def test_consultar_status_pagamento():
    """Testa a API de consulta de status de pagamento"""
    print("🔍 Testando consulta de status de pagamento...")
    
    # Teste com um depix_id fictício
    depix_id = "test_123456"
    
    try:
        url = f"{BASE_URL}/payment_status/check.php"
        params = {"depix_id": depix_id}
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                print(f"📡 Status HTTP: {response.status}")
                print(f"📡 URL: {url}")
                print(f"📡 Parâmetros: {params}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Resposta: {data}")
                else:
                    text = await response.text()
                    print(f"❌ Erro HTTP {response.status}: {text}")
                    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

async def test_consultar_deposito():
    """Testa a API de consulta de depósito"""
    print("\n🔍 Testando consulta de depósito...")
    
    # Teste com um depix_id fictício
    depix_id = "test_123456"
    
    try:
        url = f"{BASE_URL}/rest/deposit.php"
        params = {"action": "get", "depix_id": depix_id}
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                print(f"📡 Status HTTP: {response.status}")
                print(f"📡 URL: {url}")
                print(f"📡 Parâmetros: {params}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Resposta: {data}")
                else:
                    text = await response.text()
                    print(f"❌ Erro HTTP {response.status}: {text}")
                    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

async def test_base_url():
    """Testa se a BASE_URL está acessível"""
    print("🔍 Testando BASE_URL...")
    print(f"📡 BASE_URL: {BASE_URL}")
    
    try:
        # Testa se o servidor está respondendo
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(BASE_URL) as response:
                print(f"📡 Status HTTP: {response.status}")
                if response.status == 200:
                    print("✅ Servidor está respondendo")
                else:
                    print(f"⚠️ Servidor retornou status {response.status}")
                    
    except Exception as e:
        print(f"❌ Erro ao acessar BASE_URL: {e}")

async def main():
    """Função principal de teste"""
    print("🧪 Iniciando testes do validador de PIX...\n")
    
    await test_base_url()
    await test_consultar_status_pagamento()
    await test_consultar_deposito()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    asyncio.run(main()) 