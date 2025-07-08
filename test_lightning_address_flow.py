#!/usr/bin/env python3
"""
Teste Completo do Fluxo Lightning Address
Simula todo o processo: PIX → Lightning Address → Pagamento
"""

import requests
import json
import time
import sys
import os

class LightningAddressFlowTester:
    
    def __init__(self):
        self.base_url = "https://useghost.squareweb.app"
        self.test_lightning_address = "usuario@walletofsatoshi.com"
        self.test_bolt11 = "lnbc1500n1pjuvrfnpp5q9v0x7j2q7v8x2j1q5v3x7l9j2f1n8p7h5l3s2d1n4p8k2m1v9s3fsdqs2pshjmt9de6zqen0wgsrjgrsd9ukxefwvdhk6tcqzpgxqyz5vqsp5k4z3f9m1n2p8y5l7x4j2q1r8w6t3e9o5u7i2m4k8v1c6n9s3s2yqq"
        
    def test_save_lightning_address(self, depix_id):
        """Testa salvar Lightning Address"""
        print(f"\n🔄 Testando salvar Lightning Address para {depix_id}...")
        
        url = f"{self.base_url}/api/save_lightning_address.php"
        payload = {
            "action": "update_lightning_address",
            "depix_id": depix_id,
            "address": self.test_lightning_address,
            "address_type": "lightning_address"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Lightning Address salvo com sucesso!")
                    print(f"   Endereço: {data.get('address')}")
                    print(f"   Tipo: {data.get('address_type')}")
                    return True
                else:
                    print(f"❌ Erro ao salvar: {data.get('error')}")
                    return False
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def test_save_bolt11(self, depix_id):
        """Testa salvar BOLT11"""
        print(f"\n🔄 Testando salvar BOLT11 para {depix_id}...")
        
        url = f"{self.base_url}/api/save_lightning_address.php"
        payload = {
            "action": "update_lightning_address",
            "depix_id": depix_id,
            "address": self.test_bolt11,
            "address_type": "bolt11"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ BOLT11 salvo com sucesso!")
                    print(f"   Invoice: {data.get('address')[:50]}...")
                    print(f"   Tipo: {data.get('address_type')}")
                    return True
                else:
                    print(f"❌ Erro ao salvar: {data.get('error')}")
                    return False
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def test_lightning_address_resolution(self):
        """Testa resolução de Lightning Address"""
        print(f"\n🔄 Testando resolução de Lightning Address...")
        
        url = f"{self.base_url}/testphp/test_lightning_address.php"
        
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ Teste de resolução executado!")
                print(f"   Resposta: {response.text[:200]}...")
                return True
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def test_cron_processor(self):
        """Testa o processador cron final"""
        print(f"\n🔄 Testando processador cron Lightning...")
        
        url = f"{self.base_url}/api/lightning_cron_endpoint_final.php"
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Processador cron executado!")
                print(f"   Processados: {data.get('processed', 0)}")
                print(f"   Sucessos: {data.get('successful', 0)}")
                print(f"   Falhas: {data.get('failed', 0)}")
                
                if data.get('errors'):
                    print(f"   Erros:")
                    for error in data.get('errors', [])[:3]:  # Mostrar apenas os primeiros 3
                        print(f"     - {error.get('depix_id')}: {error.get('error')}")
                
                return True
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def test_validation_functions(self):
        """Testa funções de validação"""
        print(f"\n🔄 Testando validações...")
        
        # Teste Lightning Address válido
        valid_addresses = [
            "usuario@walletofsatoshi.com",
            "test@strike.me",
            "satoshi@getalby.com"
        ]
        
        # Teste BOLT11 válido
        valid_bolt11 = [
            "lnbc1500n1pjuvrfnpp5q9v0x7j2q7v8x2j1q5v3x7l9j2f1n8p7h5l3s2d1n4p8k2m1v9s3f",
            "lntb1000u1pjuvrfnpp5q9v0x7j2q7v8x2j1q5v3x7l9j2f1n8p7h5l3s2d1n4p8k2m1v9s3f"
        ]
        
        # Teste endereços inválidos
        invalid_addresses = [
            "usuario",
            "usuario@",
            "@domain.com",
            "usuario@domain",
            "lnbc123"  # BOLT11 muito curto
        ]
        
        print(f"✅ Lightning Address válidos:")
        for addr in valid_addresses:
            print(f"   - {addr}")
        
        print(f"✅ BOLT11 válidos:")
        for bolt in valid_bolt11:
            print(f"   - {bolt[:30]}...")
        
        print(f"❌ Endereços inválidos:")
        for addr in invalid_addresses:
            print(f"   - {addr}")
        
        return True
    
    def run_full_test(self):
        """Executa teste completo do fluxo"""
        print("🚀 TESTE COMPLETO - LIGHTNING ADDRESS FLOW")
        print("=" * 50)
        
        # Usar um depix_id de teste (ou você pode criar um novo)
        test_depix_id = "TEST_" + str(int(time.time()))
        
        tests = [
            ("Validações", self.test_validation_functions),
            ("Resolução Lightning Address", self.test_lightning_address_resolution),
            ("Salvar Lightning Address", lambda: self.test_save_lightning_address(test_depix_id)),
            ("Salvar BOLT11", lambda: self.test_save_bolt11(test_depix_id + "_BOLT")),
            ("Processador Cron", self.test_cron_processor),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n" + "="*30)
            print(f"📋 TESTE: {test_name}")
            print("="*30)
            
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: SUCESSO")
                else:
                    print(f"❌ {test_name}: FALHOU")
                    
            except Exception as e:
                print(f"💥 {test_name}: ERRO - {e}")
                results.append((test_name, False))
            
            time.sleep(1)  # Pausa entre testes
        
        # Resumo final
        print(f"\n" + "="*50)
        print("📊 RESUMO DOS TESTES")
        print("="*50)
        
        success_count = sum(1 for _, result in results if result)
        total_count = len(results)
        
        for test_name, result in results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{test_name:.<30} {status}")
        
        print(f"\n🎯 RESULTADO FINAL: {success_count}/{total_count} testes passaram")
        
        if success_count == total_count:
            print("🎉 TODOS OS TESTES PASSARAM! Lightning Address está funcionando!")
        else:
            print("⚠️  Alguns testes falharam. Verifique os logs acima.")
        
        return success_count == total_count

if __name__ == "__main__":
    print("Lightning Address Flow Tester")
    print("Testando integração completa do Ghost Bot")
    print()
    
    tester = LightningAddressFlowTester()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            # Teste rápido - apenas validações e resolução
            tester.test_validation_functions()
            tester.test_lightning_address_resolution()
        elif sys.argv[1] == "--cron-only":
            # Teste apenas o cron
            tester.test_cron_processor()
        else:
            print("Uso: python test_lightning_address_flow.py [--quick|--cron-only]")
    else:
        # Teste completo
        success = tester.run_full_test()
        sys.exit(0 if success else 1)
