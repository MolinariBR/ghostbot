#!/usr/bin/env python3
"""
Teste do Monitor da Carteira Voltz
Verifica saldo, transações e correlações com depósitos
"""

import requests
import json
import sys
import os
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append('/home/mau/bot/ghost')

class VoltzWalletTester:
    def __init__(self):
        self.backend_url = "https://useghost.squareweb.app"
        self.monitor_url = f"{self.backend_url}/api/voltz_monitor_api.php"
        
    def test_wallet_monitor(self):
        """Testa o monitor da carteira Voltz"""
        print("🔍 TESTANDO MONITOR DA CARTEIRA VOLTZ")
        print("=" * 60)
        
        try:
            # Teste 1: Relatório em formato texto
            print("📋 1. Relatório em formato texto legível:")
            print("-" * 40)
            
            response = requests.get(
                self.monitor_url,
                params={'limit': 20},
                timeout=30
            )
            
            if response.status_code == 200:
                print(response.text)
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                print(response.text[:500])
                
            print("\n" + "=" * 60)
            
            # Teste 2: Relatório em formato JSON
            print("📋 2. Dados detalhados em JSON:")
            print("-" * 40)
            
            response_json = requests.get(
                self.monitor_url,
                params={'format': 'json', 'limit': 10},
                timeout=30
            )
            
            if response_json.status_code == 200:
                data = response_json.json()
                
                if data.get('success'):
                    print("✅ Monitor funcionando!")
                    print(f"📅 Timestamp: {data.get('timestamp')}")
                    
                    # Saldo
                    balance = data.get('balance', {})
                    if balance.get('success'):
                        print(f"💰 Saldo: {balance.get('balance_sat', 0)} sats")
                        print(f"₿ BTC: {balance.get('balance_btc', 0):.8f}")
                    else:
                        print(f"❌ Erro no saldo: {balance.get('error')}")
                    
                    # Estatísticas
                    stats = data.get('summary', {})
                    print(f"📊 Total de transações: {stats.get('total_transactions', 0)}")
                    print(f"⬇️ Entradas: {stats.get('incoming_count', 0)}")
                    print(f"⬆️ Saídas: {stats.get('outgoing_count', 0)}")
                    print(f"💸 Taxas: {stats.get('total_fees_sat', 0)} sats")
                    print(f"📈 Fluxo líquido: {stats.get('net_flow_sat', 0)} sats")
                    
                    # Últimas transações
                    payments = data.get('payments', {}).get('correlated', [])
                    if payments:
                        print(f"\n🔄 Últimas {len(payments)} transações:")
                        for i, payment in enumerate(payments[:5], 1):
                            amount = payment.get('amount', 0)
                            amount_sat = int(abs(amount) / 1000) if amount else 0
                            type_icon = "⬇️" if amount > 0 else "⬆️"
                            status = payment.get('status', 'unknown')
                            hash_short = payment.get('payment_hash', 'N/A')[:16] + '...'
                            correlated = "✅" if payment.get('is_correlated') else "❌"
                            
                            print(f"   {i}. {type_icon} {amount_sat} sats - {status}")
                            print(f"      🔗 {hash_short} - Correlacionado: {correlated}")
                            
                            if payment.get('deposit_match'):
                                deposit = payment['deposit_match']
                                depix_id = deposit.get('depix_id', 'N/A')
                                amount_brl = deposit.get('amount_in_cents', 0) / 100
                                print(f"      💼 Depósito: {depix_id} (R$ {amount_brl})")
                    
                else:
                    print(f"❌ Erro no monitor: {data.get('error')}")
                    
            else:
                print(f"❌ Erro HTTP {response_json.status_code}")
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
    
    def test_specific_payment(self, payment_hash=None):
        """Testa busca de pagamento específico"""
        if not payment_hash:
            print("⚠️ Nenhum payment_hash fornecido para teste específico")
            return
            
        print(f"\n🔍 TESTANDO PAGAMENTO ESPECÍFICO: {payment_hash[:16]}...")
        print("-" * 60)
        
        try:
            # Aqui você poderia adicionar um endpoint específico para buscar um pagamento
            # Por enquanto, vamos apenas procurar no relatório geral
            response = requests.get(
                self.monitor_url,
                params={'format': 'json', 'limit': 100},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get('payments', {}).get('correlated', [])
                
                found = False
                for payment in payments:
                    if payment.get('payment_hash') == payment_hash:
                        found = True
                        print("✅ Pagamento encontrado!")
                        print(f"🔗 Hash: {payment.get('payment_hash')}")
                        print(f"💰 Valor: {payment.get('amount', 0)} msat")
                        print(f"📊 Status: {payment.get('status')}")
                        print(f"🔗 Correlacionado: {'✅' if payment.get('is_correlated') else '❌'}")
                        
                        if payment.get('deposit_match'):
                            deposit = payment['deposit_match']
                            print(f"💼 Depósito correspondente:")
                            print(f"   🆔 Depix ID: {deposit.get('depix_id')}")
                            print(f"   💰 Valor: R$ {deposit.get('amount_in_cents', 0)/100}")
                            print(f"   📊 Status: {deposit.get('status')}")
                        break
                
                if not found:
                    print("❌ Pagamento não encontrado no histórico recente")
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def show_menu(self):
        """Exibe menu interativo"""
        print("\n🔧 MENU DO TESTE VOLTZ WALLET MONITOR")
        print("=" * 50)
        print("1. 📊 Relatório completo da carteira")
        print("2. 🔍 Buscar pagamento específico")
        print("3. 📋 Relatório em JSON")
        print("4. 🚪 Sair")
        print("-" * 50)
        
        choice = input("Escolha uma opção (1-4): ").strip()
        
        if choice == "1":
            self.test_wallet_monitor()
        elif choice == "2":
            payment_hash = input("Digite o payment_hash: ").strip()
            self.test_specific_payment(payment_hash)
        elif choice == "3":
            self.test_json_output()
        elif choice == "4":
            print("👋 Saindo...")
            return False
        else:
            print("❌ Opção inválida")
        
        return True
    
    def test_json_output(self):
        """Testa saída JSON pura"""
        try:
            response = requests.get(
                self.monitor_url,
                params={'format': 'json', 'limit': 5},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

def main():
    tester = VoltzWalletTester()
    
    if len(sys.argv) > 1:
        # Modo não-interativo
        if sys.argv[1] == "monitor":
            tester.test_wallet_monitor()
        elif sys.argv[1] == "payment" and len(sys.argv) > 2:
            tester.test_specific_payment(sys.argv[2])
        elif sys.argv[1] == "json":
            tester.test_json_output()
        else:
            print("Uso: python test_voltz_monitor.py [monitor|payment <hash>|json]")
    else:
        # Modo interativo
        while tester.show_menu():
            input("\n⏎ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
