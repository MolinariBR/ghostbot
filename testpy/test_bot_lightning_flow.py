#!/usr/bin/env python3
"""
Teste do Fluxo Lightning Bot - Simula ação que o bot deveria fazer
Monitora endpoint Lightning e simula envio de mensagem quando detecta status "awaiting_client_invoice"
"""

import requests
import json
import time
from datetime import datetime

LIGHTNING_ENDPOINT = "https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php"

def check_lightning_deposits():
    """Verifica depósitos Lightning aguardando cliente"""
    try:
        print(f"[{datetime.now()}] Consultando endpoint Lightning...")
        
        response = requests.get(LIGHTNING_ENDPOINT, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ Erro na resposta: {data.get('error', 'Erro desconhecido')}")
            return
        
        results = data.get('results', [])
        total = data.get('total_pending', 0)
        
        print(f"✅ Encontrados {total} depósitos Lightning")
        
        awaiting_invoice = []
        for result in results:
            depix_id = result.get('depix_id')
            result_data = result.get('result', {})
            status = result_data.get('status')
            
            if status == 'awaiting_client_invoice':
                awaiting_invoice.append({
                    'depix_id': depix_id,
                    'amount_sats': result_data.get('amount_sats', 0),
                    'message': result_data.get('message', '')
                })
        
        print(f"📋 Depósitos aguardando invoice do cliente: {len(awaiting_invoice)}")
        
        for deposit in awaiting_invoice:
            print(f"\n🔔 AÇÃO NECESSÁRIA:")
            print(f"   📄 Depix ID: {deposit['depix_id']}")
            print(f"   ⚡ Valor: {deposit['amount_sats']} sats")
            print(f"   💬 Status: {deposit['message']}")
            
            # Simular ação do bot
            simulate_bot_action(deposit)
        
        # Destaque especial para o depix_id real
        real_deposit = next((d for d in awaiting_invoice if d['depix_id'] == '0197e9e7d0d17dfc9b9ee24c0c36ba2a'), None)
        if real_deposit:
            print(f"\n🎯 DEPÓSITO REAL DETECTADO!")
            print(f"   📄 {real_deposit['depix_id']}")
            print(f"   ⚡ {real_deposit['amount_sats']} sats")
            print(f"   ✅ Bot deveria solicitar Lightning Address/Invoice do cliente")
        else:
            print(f"\n⚠️  Depósito real 0197e9e7d0d17dfc9b9ee24c0c36ba2a não encontrado em awaiting_client_invoice")
        
        return awaiting_invoice
        
    except requests.exceptions.Timeout:
        print("⏰ Timeout na consulta Lightning endpoint")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return []

def simulate_bot_action(deposit):
    """Simula ação que o bot deveria fazer"""
    depix_id = deposit['depix_id']
    amount_sats = deposit['amount_sats']
    
    print(f"🤖 SIMULANDO AÇÃO DO BOT para {depix_id}:")
    print(f"   📤 Deveria enviar mensagem: 'Seu depósito PIX foi confirmado!'")
    print(f"   📤 Deveria solicitar: 'Envie seu Lightning Address ou BOLT11 invoice para receber {amount_sats} sats'")
    print(f"   📤 Deveria aguardar resposta do usuário com endereço Lightning")

def get_deposit_details(depix_id):
    """Consulta detalhes específicos de um depósito"""
    try:
        url = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

def main():
    print("🚀 Iniciando teste do fluxo Lightning Bot")
    print("="*60)
    
    # Verificar depósitos Lightning
    awaiting_deposits = check_lightning_deposits()
    
    # Verificar detalhes do depósito real especificamente
    print(f"\n🔍 Verificando detalhes do depósito real...")
    real_details = get_deposit_details('0197e9e7d0d17dfc9b9ee24c0c36ba2a')
    if real_details:
        print(f"✅ Detalhes encontrados: {json.dumps(real_details, indent=2)}")
    else:
        print(f"❌ Não foi possível obter detalhes do depósito real")
    
    print(f"\n📊 RESUMO:")
    print(f"   • Total com status 'awaiting_client_invoice': {len(awaiting_deposits)}")
    print(f"   • Depósito real detectado: {'✅' if any(d['depix_id'] == '0197e9e7d0d17dfc9b9ee24c0c36ba2a' for d in awaiting_deposits) else '❌'}")
    print(f"   • Bot deveria estar enviando mensagens para esses depósitos")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"   1. Verificar se bot tem cron job monitorando Lightning endpoint")
    print(f"   2. Verificar se bot está enviando mensagens quando detecta awaiting_client_invoice")
    print(f"   3. Testar fluxo completo: usuário responde com Lightning Address → pagamento")

if __name__ == "__main__":
    main()
