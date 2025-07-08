#!/usr/bin/env python3

# Teste local simples
print("🧪 TESTE LOCAL SIMPLES")
print("=" * 30)

# Seus depix_ids
depix_ids = [
    "0197e0ed06537df9820a28f5a5380a3b",
    "0197e10b5b8f7df9a6bf9430188534e4",
    "0197e12300eb7df9808ca5d7719ea40e",
    "0197e5214a377dfaae6e541f68057444"
]

print("✅ Depix IDs disponíveis para teste:")
for i, depix_id in enumerate(depix_ids, 1):
    print(f"{i}. {depix_id}")

depix_id = depix_ids[0]
print(f"\n🎯 Testando: {depix_id}")

# Teste da API Voltz local
try:
    import sys
    sys.path.append('/home/mau/bot/ghost')
    
    from api.voltz import VoltzAPI
    print("✅ Módulo Voltz importado com sucesso")
    
    voltz = VoltzAPI(backend_url='https://useghost.squareweb.app')
    print("✅ VoltzAPI inicializada")
    
    # Teste de conectividade básica
    print("🔍 Testando conectividade...")
    import requests
    
    # Teste simples
    response = requests.get("https://useghost.squareweb.app/", timeout=5)
    print(f"✅ Conectividade OK (Status: {response.status_code})")
    
    print(f"\n📋 RESULTADO:")
    print(f"• Depix ID para teste: {depix_id}")
    print(f"• Módulo Voltz: OK")
    print(f"• Conectividade: OK")
    print(f"• Próximo passo: Testar criação/webhook manual")
    
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n✅ Teste local concluído!")
