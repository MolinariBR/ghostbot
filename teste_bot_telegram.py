#!/usr/bin/env python3
"""
Teste final: Enviar mensagem via Telegram Bot API para testar fluxo Lightning
"""

import requests
import json
import os
import sys

# Adiciona o diretório do projeto ao path
sys.path.append('/home/mau/bot/ghost')

def test_telegram_message():
    """Envia mensagem de teste via Telegram Bot API"""
    
    print("📱 TESTE VIA TELEGRAM BOT API")
    print("=" * 40)
    
    try:
        # Importa o token do bot
        from tokens import Config
        bot_token = Config.TELEGRAM_BOT_TOKEN
        chat_id = "7910260237"  # Chat ID que tem depósitos Lightning pendentes
        
        # URL da API do Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Mensagem de teste
        message_text = "/start"
        
        payload = {
            "chat_id": chat_id,
            "text": message_text
        }
        
        print(f"📤 Enviando mensagem para chat ID: {chat_id}")
        print(f"💬 Mensagem: {message_text}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get('ok'):
                print("✅ Mensagem enviada com sucesso!")
                print(f"📊 Message ID: {resp_data['result']['message_id']}")
                
                print("\n🎯 PRÓXIMOS PASSOS:")
                print("1. O bot deveria responder ao /start")
                print("2. Como há depósitos Lightning pendentes para este chat:")
                print("   - Bot deveria detectar depósitos com status 'awaiting_client_invoice'")
                print("   - Enviar mensagem solicitando Lightning Address ou Invoice")
                print("3. Verifique os logs do bot para confirmar o processamento")
                
                # Lista alguns depósitos pendentes para referência
                print("\n📋 DEPÓSITOS LIGHTNING PENDENTES (alguns exemplos):")
                lightning_deposits = [
                    {"id": 47, "valor": "R$ 50,00", "sats": "8037", "depix_id": "sim_1751990221_260237"},
                    {"id": 46, "valor": "R$ 50,00", "sats": "1357", "depix_id": "0197e9e7d0d17dfc9b9ee24c0c36ba2a"},
                    {"id": 45, "valor": "R$ 15,00", "sats": "1500", "depix_id": "teste_ln_1751975661_9ea40e"},
                ]
                
                for dep in lightning_deposits:
                    print(f"   • ID {dep['id']}: {dep['valor']} → {dep['sats']} sats (depix: {dep['depix_id']})")
                
                return True
                
            else:
                print(f"❌ Erro na resposta da API: {resp_data}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_logs_bot():
    """Verifica se há logs recentes do bot sobre Lightning"""
    
    print("\n📄 VERIFICANDO LOGS DO BOT...")
    print("-" * 30)
    
    log_files = [
        "/home/mau/bot/ghost/bot.log",
        "/home/mau/bot/ghost/fluxo.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📋 Últimas linhas de {log_file}:")
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Mostra as últimas 10 linhas
                    for line in lines[-10:]:
                        if 'lightning' in line.lower() or 'awaiting' in line.lower():
                            print(f"   ⚡ {line.strip()}")
                        else:
                            print(f"   📝 {line.strip()}")
            except Exception as e:
                print(f"   ❌ Erro ao ler log: {e}")
        else:
            print(f"   ⚠️ Log não encontrado: {log_file}")

if __name__ == "__main__":
    # Envia mensagem de teste
    success = test_telegram_message()
    
    if success:
        import time
        print("\n⏳ Aguardando 5 segundos para o bot processar...")
        time.sleep(5)
        
        # Verifica logs
        verificar_logs_bot()
        
        print("\n🎯 TESTE CONCLUÍDO!")
        print("✅ Se o bot detectou os depósitos Lightning, ele deveria ter enviado mensagens")
        print("📱 Verifique o chat do Telegram para confirmar as mensagens do bot")
    else:
        print("\n❌ TESTE FALHOU!")
        print("Verifique as configurações do bot e token")
