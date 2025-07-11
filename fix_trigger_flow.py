#!/usr/bin/env python3
"""
Script para corrigir o fluxo de gatilhos após detecção do blockchainTxID
Este script identifica quando o blockchainTxID é detectado mas o gatilho não é disparado
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Configuração
DEPIX_ID = "0197f6f3c6527dfe9d7ff3bdc3954e93"
CHAT_ID = "7910260237"
USERNAME = "triacorelabs"

def test_trigger_flow():
    """Testa o fluxo de gatilhos manualmente"""
    print("🔧 TESTE DO FLUXO DE GATILHOS")
    print("=" * 50)
    
    # 1. Verificar se o blockchainTxID existe
    print("1. Verificando status do PIX...")
    
    api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0"
    
    headers = {
        "api_key": api_key,
        "Authorization": f"Bearer {api_key}",
        "X-Nonce": "test-fix-123"
    }
    
    try:
        url = f"https://depix.eulen.app/api/deposit-status?id={DEPIX_ID}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ BlockchainTxID: {data.get('blockchainTxID')}")
            
            if data.get('status') == 'depix_sent' and data.get('blockchainTxID'):
                print("✅ Condições atendidas para disparar gatilho!")
                return trigger_address_request(data.get('blockchainTxID'))
            else:
                print("❌ Condições não atendidas")
                return False
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def trigger_address_request(blockchain_txid: str) -> bool:
    """Dispara manualmente o gatilho de solicitação de endereço"""
    print("\n2. Disparando gatilho ADDRESS_REQUESTED...")
    
    try:
        # Importar sistema de gatilhos
        import sys
        sys.path.append('/home/mau/bot/ghost')
        
        from trigger.sistema_gatilhos import trigger_system, TriggerEvent
        
        # Disparar o gatilho
        result = trigger_system.trigger_event(
            TriggerEvent.ADDRESS_REQUESTED,
            CHAT_ID,
            {
                'depix_id': DEPIX_ID,
                'blockchain_txid': blockchain_txid,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        print(f"✅ Gatilho disparado com sucesso: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Erro ao disparar gatilho: {e}")
        return False

def test_message_callback():
    """Testa o callback de mensagens"""
    print("\n3. Testando callback de mensagens...")
    
    try:
        import sys
        sys.path.append('/home/mau/bot/ghost')
        
        from trigger.sistema_gatilhos import trigger_system
        
        # Simular callback de mensagem
        async def test_callback(chat_id: str, text: str, parse_mode: str = 'Markdown'):
            print(f"📨 MENSAGEM SIMULADA para {chat_id}:")
            print(f"📝 {text}")
            return True
        
        # Configurar callback
        trigger_system.set_message_sender(test_callback)
        
        # Disparar solicitação de endereço
        order_data = {
            'chat_id': CHAT_ID,
            'currency': 'Lightning',
            'network': 'Lightning',
            'amount': 10.0,
            'depix_id': DEPIX_ID
        }
        
        trigger_system.send_address_request(CHAT_ID, order_data)
        
        print("✅ Callback testado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no callback: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 INICIANDO CORREÇÃO DO FLUXO DE GATILHOS")
    print("=" * 60)
    
    # Teste 1: Verificar status do PIX
    print("\n📋 TESTE 1: Status do PIX")
    status_ok = test_trigger_flow()
    
    # Teste 2: Callback de mensagens
    print("\n📋 TESTE 2: Callback de mensagens")
    callback_ok = test_message_callback()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print(f"✅ Status PIX: {'OK' if status_ok else 'FALHA'}")
    print(f"✅ Callback: {'OK' if callback_ok else 'FALHA'}")
    
    if status_ok and callback_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("💡 O usuário deve receber a mensagem de solicitação de endereço")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os logs para mais detalhes")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
