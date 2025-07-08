#!/usr/bin/env python3
"""
INVESTIGAÇÃO LOGS VOLTZ - Análise detalhada dos logs Lightning
==============================================================

Script para investigar logs específicos do Voltz Lightning.
"""

import requests
import json
import time

def verificar_logs_voltz():
    """Verifica logs específicos do Voltz."""
    print("📋 VERIFICAÇÃO DE LOGS VOLTZ")
    print("=" * 40)
    
    # Tentar acessar possíveis endpoints de log
    log_endpoints = [
        "https://useghost.squareweb.app/voltz/logs/",
        "https://useghost.squareweb.app/logs/voltz.log",
        "https://useghost.squareweb.app/logs/lightning.log",
        "https://useghost.squareweb.app/voltz/debug.php",
        "https://useghost.squareweb.app/voltz/status.php"
    ]
    
    for endpoint in log_endpoints:
        try:
            print(f"📡 Testando: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   📄 Conteúdo: {response.text[:200]}...")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        print("-" * 30)

def testar_voltz_debug():
    """Testa endpoint de debug do Voltz."""
    print("\n🐛 TESTE DEBUG VOLTZ")
    print("=" * 40)
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    
    # Testa diferentes ações de debug
    debug_actions = [
        {"action": "debug"},
        {"action": "status"},
        {"action": "check_node"},
        {"action": "test_lightning"},
        {"action": "get_info"}
    ]
    
    for payload in debug_actions:
        try:
            print(f"🔍 Testando ação: {payload['action']}")
            response = requests.post(url, json=payload, timeout=15)
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text[:300]}...")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        print("-" * 30)

def testar_timeout_voltz():
    """Testa o Voltz com timeout maior para ver se é problema de tempo."""
    print("\n⏱️ TESTE TIMEOUT EXTENDIDO")
    print("=" * 40)
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    depix_id = "test_timeout_" + str(int(time.time()))
    
    payload = {
        "action": "process_deposit",
        "depix_id": depix_id
    }
    
    print(f"🎯 Testando com depix_id: {depix_id}")
    print("⏱️ Timeout extendido: 60 segundos...")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Resposta completa: {response.text}")
    except requests.exceptions.Timeout:
        print("⏰ Timeout ainda ocorreu após 60 segundos")
        print("❌ Indica problema no nó Lightning ou processamento interno")
    except Exception as e:
        print(f"❌ Outro erro: {e}")

def verificar_nodejs_backend():
    """Verifica se há um backend Node.js rodando."""
    print("\n🟢 VERIFICAÇÃO NODE.JS")
    print("=" * 40)
    
    node_endpoints = [
        "https://useghost.squareweb.app:3000/health",
        "https://useghost.squareweb.app:8080/health",
        "https://useghost.squareweb.app/api/health",
        "https://useghost.squareweb.app/node/health"
    ]
    
    for endpoint in node_endpoints:
        try:
            print(f"📡 Testando Node.js: {endpoint}")
            response = requests.get(endpoint, timeout=5)
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:100]}...")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def analisar_resposta_voltz():
    """Analisa a resposta do voltz_rest.php em detalhes."""
    print("\n🔬 ANÁLISE DETALHADA VOLTZ")
    print("=" * 40)
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    
    # Teste GET primeiro
    print("📡 Teste GET (sem payload)...")
    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Resposta: {repr(response.text)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n📡 Teste POST com action vazia...")
    try:
        response = requests.post(url, json={}, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {repr(response.text)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n📡 Teste POST com action inválida...")
    try:
        payload = {"action": "invalid_action"}
        response = requests.post(url, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {repr(response.text)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def testar_voltz_simples():
    """Teste muito simples do Voltz."""
    print("\n🎯 TESTE VOLTZ ULTRA SIMPLES")
    print("=" * 40)
    
    url = "https://useghost.squareweb.app/voltz/voltz_rest.php"
    
    # Primeira chamada: sem timeout para ver o que acontece
    print("📡 Chamada sem timeout definido...")
    try:
        start_time = time.time()
        response = requests.post(url, json={"action": "test"})
        end_time = time.time()
        
        print(f"   ✅ Completou em {end_time - start_time:.2f} segundos")
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
    except Exception as e:
        end_time = time.time()
        print(f"   ❌ Erro após {end_time - start_time:.2f} segundos: {e}")

def main():
    print("🔍 INVESTIGAÇÃO LOGS VOLTZ LIGHTNING")
    print("=" * 50)
    
    # 1. Verificar logs disponíveis
    verificar_logs_voltz()
    
    # 2. Testar debug
    testar_voltz_debug()
    
    # 3. Analisar resposta detalhada
    analisar_resposta_voltz()
    
    # 4. Teste simples
    testar_voltz_simples()
    
    # 5. Verificar Node.js
    verificar_nodejs_backend()
    
    # 6. Teste com timeout extendido
    testar_timeout_voltz()
    
    print(f"\n✅ Investigação concluída")

if __name__ == "__main__":
    main()
