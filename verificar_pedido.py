#!/usr/bin/env python3
"""
Teste rápido para verificar se o pedido foi criado no backend
"""

import requests
import json

def verificar_pedido():
    """Verifica se o pedido 71 foi criado"""
    
    print("🔍 Verificando pedido ID 71 no backend...")
    
    try:
        # Primeira tentativa: consulta direta
        response = requests.get(
            "https://useghost.squareweb.app/rest/deposit.php?action=get&id=71",
            timeout=10
        )
        
        print(f"📡 Status HTTP: {response.status_code}")
        print(f"📄 Resposta: {response.text[:500]}...")  # Primeiros 500 chars
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON válido: {json.dumps(data, indent=2)}")
            except:
                print("❌ Resposta não é JSON válido")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_pedido()
