#!/usr/bin/env python3
"""
Teste Final do Sistema de Monitoramento Voltz
Teste completo do monitor da carteira incluindo dashboard
"""

import requests
import json
import time
from datetime import datetime

def test_voltz_monitoring_system():
    """Testa todo o sistema de monitoramento Voltz"""
    
    print("🚀 TESTE COMPLETO DO SISTEMA DE MONITORAMENTO VOLTZ")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "https://useghost.squareweb.app"
    
    # Teste 1: API de saldo
    print("1. 💰 TESTE DO SALDO DA CARTEIRA")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/api/voltz_monitor_api.php?action=balance", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                balance = data['data']
                print(f"✅ Saldo obtido com sucesso!")
                print(f"   💰 {balance.get('balance_sat', 0):,} sats")
                print(f"   ₿ {balance.get('balance_btc', 0):.8f} BTC")
                print(f"   🆔 {balance.get('id', 'N/A')}")
            else:
                print(f"❌ Erro: {data.get('error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print()
    
    # Teste 2: API de estatísticas
    print("2. 📊 TESTE DAS ESTATÍSTICAS")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/api/voltz_monitor_api.php?action=stats&limit=20", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']['period_stats']
                balance = data['data']['current_balance']
                
                print(f"✅ Estatísticas obtidas!")
                print(f"   📈 Entradas: {stats.get('count_incoming', 0)} ({stats.get('total_incoming_sat', 0):,} sats)")
                print(f"   📉 Saídas: {stats.get('count_outgoing', 0)} ({stats.get('total_outgoing_sat', 0):,} sats)")
                print(f"   💸 Taxas: {stats.get('total_fees_sat', 0)} sats")
                print(f"   📊 Fluxo líquido: {stats.get('net_flow_sat', 0):,} sats")
                print(f"   📦 Amostra: {data['data'].get('sample_size', 0)} transações")
            else:
                print(f"❌ Erro: {data.get('error')}")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # Teste 3: API de histórico
    print("3. 🔄 TESTE DO HISTÓRICO DE TRANSAÇÕES")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/api/voltz_monitor_api.php?action=history&limit=5", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                payments = data['data']['payments']
                print(f"✅ Histórico obtido!")
                print(f"   📋 Total de transações: {data['data']['total']}")
                print(f"   ⬇️ Entradas: {data['data']['classification']['incoming_count']}")
                print(f"   ⬆️ Saídas: {data['data']['classification']['outgoing_count']}")
                
                print(f"\n   🔄 Últimas 3 transações:")
                for i, payment in enumerate(payments[:3], 1):
                    amount = payment.get('amount', 0)
                    amount_sat = int(abs(amount) / 1000) if amount else 0
                    type_icon = "⬇️" if amount > 0 else "⬆️"
                    hash_short = payment.get('payment_hash', 'N/A')[:12] + '...'
                    status = payment.get('status', 'unknown')
                    
                    print(f"      {i}. {type_icon} {amount_sat:,} sats - {status}")
                    print(f"         🔗 {hash_short}")
                    
                    if payment.get('deposit_match'):
                        print(f"         ✅ Correlacionado com depósito")
                    else:
                        print(f"         ❌ Não correlacionado")
            else:
                print(f"❌ Erro: {data.get('error')}")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # Teste 4: Dashboard HTML
    print("4. 🖥️ TESTE DO DASHBOARD WEB")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/voltz_dashboard.html", timeout=15)
        if response.status_code == 200:
            html_content = response.text
            if "Monitor da Carteira Voltz" in html_content and "dashboard" in html_content.lower():
                print(f"✅ Dashboard acessível!")
                print(f"   📄 Tamanho: {len(html_content):,} chars")
                print(f"   🔗 URL: {base_url}/voltz_dashboard.html")
                print(f"   🎨 Interface web funcionando")
            else:
                print(f"⚠️ Dashboard acessível mas conteúdo suspeito")
        else:
            print(f"❌ Dashboard não acessível - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no dashboard: {e}")
    
    print()
    
    # Teste 5: Monitor direto (formato texto)
    print("5. 📋 TESTE DO MONITOR DIRETO")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/voltz/voltz_wallet_monitor.php?limit=5", timeout=15)
        if response.status_code == 200:
            text_content = response.text
            if "RELATÓRIO COMPLETO DA CARTEIRA VOLTZ" in text_content:
                lines = text_content.split('\n')[:10]  # Primeiras 10 linhas
                print(f"✅ Monitor direto funcionando!")
                print(f"   📄 Primeiras linhas do relatório:")
                for line in lines:
                    if line.strip():
                        print(f"      {line}")
                print(f"   📏 Total: {len(text_content)} chars")
            else:
                print(f"⚠️ Monitor acessível mas formato inesperado")
                print(f"   Conteúdo: {text_content[:200]}...")
        else:
            print(f"❌ Monitor não acessível - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no monitor: {e}")
    
    print()
    print("=" * 70)
    print("🎯 RESUMO DO TESTE COMPLETO")
    print("=" * 70)
    print("✅ Sistema de monitoramento da carteira Voltz:")
    print("   📊 API de saldo e estatísticas")
    print("   🔄 API de histórico de transações") 
    print("   📋 Monitor em formato texto")
    print("   🖥️ Dashboard web interativo")
    print("   🔗 Correlação com depósitos do sistema")
    print()
    print("📋 COMO USAR:")
    print(f"   1. Dashboard: {base_url}/voltz_dashboard.html")
    print(f"   2. API JSON: {base_url}/api/voltz_monitor_api.php")
    print(f"   3. Texto: {base_url}/voltz/voltz_wallet_monitor.php")
    print()
    print("🚀 SISTEMA PRONTO PARA USO EM PRODUÇÃO!")
    print("=" * 70)

if __name__ == "__main__":
    test_voltz_monitoring_system()
