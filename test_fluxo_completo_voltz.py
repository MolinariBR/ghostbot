#!/usr/bin/env python3
"""
Teste completo da integração Ghost Bot + Backend Voltz
Este teste simula o fluxo completo do usuário:
1. Bot registra pedido via bot_register_deposit.php
2. Backend processa e gera invoice Lightning automaticamente
3. Bot verifica status e exibe invoice/QR code ao usuário
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from api.voltz import VoltzAPI
import requests

class TestFluxoCompleto:
    def __init__(self):
        self.voltz = VoltzAPI(backend_url='http://localhost:8000/voltz')
        self.backend_url = "http://localhost:8000"
        self.test_user_id = 7910260237  # Chat ID de teste
        self.test_deposit_id = None
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_backend_connectivity(self):
        """Testa conectividade com o backend"""
        self.log("🔍 Testando conectividade com o backend...")
        
        try:
            response = requests.get(f"{self.backend_url}/api/user_api.php")
            if response.status_code == 200:
                self.log("✅ Backend acessível")
                return True
            else:
                self.log(f"❌ Backend respondeu com status {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao conectar com backend: {e}")
            return False
    
    def register_deposit(self, amount_brl, amount_sats):
        """Registra um depósito no backend via bot_register_deposit.php"""
        self.log(f"📝 Registrando depósito: R$ {amount_brl} ({amount_sats} sats)...")
        
        # Gerar ID único para o depósito
        self.test_deposit_id = str(uuid.uuid4()).replace('-', '')[:16]
        
        payload = {
            'user_id': self.test_user_id,
            'deposit_id': self.test_deposit_id,
            'amount_brl': amount_brl,
            'amount_sats': amount_sats,
            'deposit_type': 'lightning',
            'status': 'pending_invoice'
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/bot_register_deposit.php",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log(f"✅ Depósito registrado com ID: {self.test_deposit_id}")
                    return True
                else:
                    self.log(f"❌ Erro no registro: {result.get('message', 'Erro desconhecido')}")
                    return False
            else:
                self.log(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao registrar depósito: {e}")
            return False
    
    def check_deposit_status(self):
        """Verifica o status do depósito via bot_update_status.php"""
        if not self.test_deposit_id:
            self.log("❌ Nenhum deposit_id para verificar")
            return None
            
        self.log(f"🔍 Verificando status do depósito {self.test_deposit_id}...")
        
        try:
            response = requests.get(
                f"{self.backend_url}/api/bot_update_status.php",
                params={'deposit_id': self.test_deposit_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 'unknown')
                self.log(f"📊 Status atual: {status}")
                
                if 'invoice' in result and result['invoice']:
                    self.log(f"⚡ Invoice disponível: {result['invoice'][:50]}...")
                    
                if 'qr_code' in result and result['qr_code']:
                    self.log(f"📱 QR Code disponível: {result['qr_code'][:50]}...")
                
                return result
            else:
                self.log(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro ao verificar status: {e}")
            return None
    
    def wait_for_invoice_generation(self, max_wait_seconds=60):
        """Aguarda a geração automática do invoice pelo backend"""
        self.log("⏳ Aguardando geração automática do invoice...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_seconds:
            status_data = self.check_deposit_status()
            
            if status_data:
                if status_data.get('status') == 'invoice_generated' and status_data.get('invoice'):
                    self.log("✅ Invoice gerado automaticamente pelo backend!")
                    return status_data
                elif status_data.get('status') == 'error':
                    self.log(f"❌ Erro no processamento: {status_data.get('message', 'Erro desconhecido')}")
                    return None
            
            self.log("⏳ Aguardando... (verificando novamente em 5s)")
            time.sleep(5)
        
        self.log("⏰ Timeout - Invoice não foi gerado no tempo esperado")
        return None
    
    def test_voltz_api_direct(self):
        """Testa a API Voltz diretamente"""
        self.log("🔧 Testando API Voltz diretamente...")
        
        try:
            # Teste usando API do create_deposit_request para verificar conectividade
            test_result = self.voltz.create_deposit_request(
                chatid="test_123",
                userid="test_user",
                amount_in_cents=1000,  # R$ 10,00
                taxa=0.05,
                moeda="BTC", 
                send_amount=10000  # 10k sats
            )
            
            if test_result and 'depix_id' in test_result:
                self.log(f"⚡ Teste de depósito criado: {test_result['depix_id']}")
                return True
            else:
                self.log("❌ Falha na criação de depósito de teste")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro na API Voltz: {e}")
            return False
    
    def simulate_user_flow(self, amount_brl=25.0):
        """Simula o fluxo completo do usuário"""
        self.log("🚀 Iniciando simulação do fluxo completo do usuário")
        self.log("=" * 60)
        
        # Calcular valor em sats (usando taxa aproximada)
        sats_per_brl = 1800  # Taxa aproximada para teste
        amount_sats = int(amount_brl * sats_per_brl)
        
        # Etapa 1: Verificar conectividade
        if not self.test_backend_connectivity():
            self.log("❌ Teste abortado - problemas de conectividade")
            return False
        
        # Etapa 2: Testar API Voltz diretamente
        if not self.test_voltz_api_direct():
            self.log("❌ Teste abortado - problemas com API Voltz")
            return False
        
        # Etapa 3: Registrar depósito no backend
        if not self.register_deposit(amount_brl, amount_sats):
            self.log("❌ Teste abortado - falha no registro do depósito")
            return False
        
        # Etapa 4: Aguardar processamento automático
        invoice_data = self.wait_for_invoice_generation()
        
        if not invoice_data:
            self.log("❌ Teste falhou - invoice não foi gerado")
            return False
        
        # Etapa 5: Simular exibição para o usuário
        self.log("🎉 SUCESSO! Simulando exibição para o usuário:")
        self.log("-" * 40)
        
        invoice = invoice_data.get('invoice', '')
        qr_code = invoice_data.get('qr_code', '')
        
        # Formatar mensagem como o bot faria
        user_message = self.voltz.format_invoice_message(
            amount_sats=amount_sats,
            payment_request=invoice,
            qr_code_url=qr_code
        )
        
        print(user_message)
        self.log("-" * 40)
        self.log("✅ Fluxo completo testado com sucesso!")
        
        return True
    
    def run_integration_tests(self):
        """Executa bateria completa de testes"""
        self.log("🧪 Iniciando bateria completa de testes de integração")
        self.log("=" * 80)
        
        tests = [
            ("Conectividade Backend", self.test_backend_connectivity),
            ("API Voltz Direta", self.test_voltz_api_direct),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n📋 Executando: {test_name}")
            try:
                if test_func():
                    self.log(f"✅ {test_name}: PASSOU")
                    passed += 1
                else:
                    self.log(f"❌ {test_name}: FALHOU")
            except Exception as e:
                self.log(f"💥 {test_name}: ERRO - {e}")
        
        self.log(f"\n📊 Resumo dos testes unitários: {passed}/{total} passaram")
        
        # Teste do fluxo completo
        self.log(f"\n🚀 Executando teste do fluxo completo...")
        if self.simulate_user_flow():
            self.log("🎉 TODOS OS TESTES PASSARAM!")
            return True
        else:
            self.log("❌ FALHA NO TESTE DO FLUXO COMPLETO")
            return False

def main():
    """Função principal"""
    print("🤖 Ghost Bot - Teste de Integração Voltz")
    print("=" * 50)
    
    tester = TestFluxoCompleto()
    
    try:
        success = tester.run_integration_tests()
        
        if success:
            print("\n🎊 INTEGRAÇÃO VALIDADA COM SUCESSO!")
            print("O bot está pronto para usar com pagamentos Lightning via Voltz.")
        else:
            print("\n⚠️  INTEGRAÇÃO PRECISA DE AJUSTES")
            print("Verifique os logs acima para identificar problemas.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")

if __name__ == "__main__":
    main()
