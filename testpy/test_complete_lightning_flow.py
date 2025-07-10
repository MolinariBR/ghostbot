#!/usr/bin/env python3
"""
Teste específico para verificar se o bot processa depósitos Lightning pendentes
"""

import requests
import json
import time
import sys

# Adiciona o diretório do projeto ao path
sys.path.append('/home/mau/bot/ghost')

def test_lightning_detection():
    """Testa se o bot detecta depósitos Lightning pendentes"""
    
    print("⚡ TESTE DE DETECÇÃO LIGHTNING")
    print("=" * 50)
    
    try:
        # Importa o token do bot
        from tokens import Config
        bot_token = Config.TELEGRAM_BOT_TOKEN
        chat_id = "7910260237"
        
        # URL da API do Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Sequência de testes
        messages = [
            "/start",
            "🛒 Comprar",
            "Oi",
            "Status",
            "Lightning"
        ]
        
        for i, message_text in enumerate(messages, 1):
            print(f"\n📤 TESTE {i}/{len(messages)}: '{message_text}'")
            
            payload = {
                "chat_id": chat_id,
                "text": message_text
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                resp_data = response.json()
                if resp_data.get('ok'):
                    msg_id = resp_data['result']['message_id']
                    print(f"✅ Mensagem enviada! ID: {msg_id}")
                    
                    # Aguarda um pouco entre mensagens
                    if i < len(messages):
                        print("⏳ Aguardando 3 segundos...")
                        time.sleep(3)
                else:
                    print(f"❌ Erro: {resp_data}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
        
        print("\n🎯 TODOS OS TESTES ENVIADOS!")
        print("📱 Verifique o chat do Telegram para ver as respostas do bot")
        
        # Verifica se há novos logs
        print("\n⏳ Aguardando 10 segundos para o bot processar todas as mensagens...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_recent_api_activity():
    """Verifica se houve atividade recente na API do bot"""
    
    print("\n📡 VERIFICANDO ATIVIDADE RECENTE DA API...")
    print("-" * 40)
    
    try:
        from tokens import Config
        bot_token = Config.TELEGRAM_BOT_TOKEN
        
        # Verifica updates recentes
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        params = {"limit": 5, "offset": -5}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                updates = data.get('result', [])
                print(f"📊 Últimos {len(updates)} updates:")
                
                for update in updates[-3:]:  # Últimos 3
                    update_id = update.get('update_id')
                    message = update.get('message', {})
                    text = message.get('text', 'N/A')
                    date = message.get('date', 0)
                    
                    print(f"   • Update {update_id}: '{text}' (timestamp: {date})")
                
                return True
            else:
                print(f"❌ Erro na API: {data}")
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return False

if __name__ == "__main__":
    # Executa testes
    print("🚀 INICIANDO TESTE COMPLETO DO FLUXO LIGHTNING")
    print("=" * 60)
    
    # Teste 1: Envia mensagens variadas
    success = test_lightning_detection()
    
    if success:
        # Teste 2: Verifica atividade da API
        check_recent_api_activity()
        
        print("\n" + "=" * 60)
        print("🎯 RESUMO DO TESTE:")
        print("✅ Mensagens enviadas ao bot")
        print("📱 Bot deveria ter detectado depósitos Lightning pendentes")
        print("⚡ Se funcionando, bot enviou solicitação de Lightning Address")
        print("📋 Verificar chat do Telegram para confirmar funcionamento")
        print("=" * 60)
    else:
        print("\n❌ TESTE FALHOU - Verifique configurações")
