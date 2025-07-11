#!/usr/bin/env python3
"""
Script para configurar e testar o backend local
"""
import subprocess
import time
import requests
import json

def start_local_backend():
    """Inicia o backend PHP local"""
    print("🚀 Iniciando backend PHP local...")
    
    try:
        # Navega para o diretório do backend
        backend_dir = "/home/mau/bot/ghostbackend"
        
        # Inicia servidor PHP
        process = subprocess.Popen([
            "php", "-S", "localhost:8080", "-t", "."
        ], cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Servidor PHP iniciado (PID: {process.pid})")
        print("📍 URL: http://localhost:8080")
        
        # Aguarda servidor inicializar
        time.sleep(3)
        
        # Testa conectividade
        try:
            response = requests.get("http://localhost:8080/rest/deposit.php", timeout=5)
            print(f"✅ Backend acessível - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro testando backend: {e}")
        
        return process
        
    except Exception as e:
        print(f"❌ Erro iniciando backend: {e}")
        return None

def test_lightning_endpoint():
    """Testa o endpoint de Lightning Address"""
    print("\n🧪 Testando endpoint Lightning Address...")
    
    payload = {
        "chat_id": "7910260237",
        "user_input": "test@phoenixwallet.me"
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/process_lightning_address.php",
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso: {result.get('success', False)}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    print("🔧 CONFIGURAÇÃO DO BACKEND LOCAL")
    print("=" * 50)
    
    # Inicia backend
    process = start_local_backend()
    
    if process:
        try:
            # Testa endpoint
            test_lightning_endpoint()
            
            print("\n🎯 INSTRUÇÕES:")
            print("1. Backend rodando em http://localhost:8080")
            print("2. Teste o bot agora com Lightning Address")
            print("3. Pressione Ctrl+C para parar o servidor")
            
            # Mantém servidor rodando
            process.wait()
            
        except KeyboardInterrupt:
            print("\n🛑 Parando servidor...")
            process.terminate()
            process.wait()
            print("✅ Servidor parado")
    
    else:
        print("❌ Falha ao iniciar backend local")

if __name__ == "__main__":
    main()
