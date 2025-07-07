#!/usr/bin/env python3
"""
Teste local direto da integração Ghost Bot + Backend Voltz
Testa diretamente os arquivos PHP sem precisar de servidor web
"""

import subprocess
import json
import time
import uuid
from datetime import datetime
from api.voltz import VoltzAPI
import os

class TestVoltzLocal:
    def __init__(self):
        self.backend_path = "/home/mau/bot/ghostbackend"
        self.voltz_path = f"{self.backend_path}/voltz"
        self.api_path = f"{self.backend_path}/api"
        self.test_user_id = 7910260237
        self.test_deposit_id = None
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_php_files_exist(self):
        """Verifica se os arquivos PHP necessários existem"""
        self.log("🔍 Verificando arquivos PHP do backend...")
        
        required_files = [
            f"{self.api_path}/bot_register_deposit.php",
            f"{self.api_path}/bot_update_status.php", 
            f"{self.voltz_path}/voltz_invoice.php",
            f"{self.voltz_path}/voltz_status.php",
            f"{self.voltz_path}/voltz_pay.php"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
            else:
                self.log(f"✅ {os.path.basename(file_path)} encontrado")
        
        if missing_files:
            self.log(f"❌ Arquivos faltando: {missing_files}")
            return False
        
        self.log("✅ Todos os arquivos PHP necessários estão presentes")
        return True
    
    def test_database_connection(self):
        """Testa conexão com banco de dados"""
        self.log("🔍 Testando conexão com banco de dados...")
        
        test_script = f"""
<?php
require_once '{self.backend_path}/config/db.php';

try {{
    $db = new PDO("sqlite:{$self.backend_path}/data/deposit.db");
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    echo json_encode(['success' => true, 'message' => 'Conexão OK']);
}} catch(PDOException $e) {{
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}}
?>
"""
        
        try:
            # Salva script temporário
            temp_file = f"{self.backend_path}/test_db.php"
            with open(temp_file, 'w') as f:
                f.write(test_script)
            
            # Executa PHP
            result = subprocess.run(['php', temp_file], capture_output=True, text=True)
            
            # Remove arquivo temporário
            os.remove(temp_file)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get('success'):
                    self.log("✅ Banco de dados acessível")
                    return True
                else:
                    self.log(f"❌ Erro no banco: {response.get('error')}")
                    return False
            else:
                self.log(f"❌ Erro PHP: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao testar banco: {e}")
            return False
    
    def test_register_deposit_direct(self):
        """Testa registro de depósito diretamente via PHP"""
        self.log("📝 Testando registro de depósito via PHP direto...")
        
        # Gerar ID único
        self.test_deposit_id = f"test_{int(time.time())}"
        
        test_script = f"""
<?php
require_once '{self.backend_path}/config/db.php';

// Simular dados POST
$_POST = array(
    'chatid' => '{self.test_user_id}',
    'userid' => 'test_user',
    'amount_in_cents' => 2500,
    'taxa' => 0.05,
    'moeda' => 'BTC', 
    'rede' => 'lightning',
    'address' => 'voltz@mail.com',
    'forma_pagamento' => 'PIX',
    'send' => 45000,
    'status' => 'pending',
    'depix_id' => '{self.test_deposit_id}'
);

// Incluir arquivo de registro
include '{self.api_path}/bot_register_deposit.php';
?>
"""
        
        try:
            temp_file = f"{self.backend_path}/test_register.php"
            with open(temp_file, 'w') as f:
                f.write(test_script)
            
            result = subprocess.run(['php', temp_file], capture_output=True, text=True)
            os.remove(temp_file)
            
            if result.returncode == 0:
                self.log(f"✅ Depósito registrado via PHP direto: {self.test_deposit_id}")
                self.log(f"📄 Resposta: {result.stdout[:100]}...")
                return True
            else:
                self.log(f"❌ Erro PHP: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao registrar via PHP: {e}")
            return False
    
    def test_voltz_invoice_generation(self):
        """Testa geração de invoice via Voltz PHP"""
        self.log("⚡ Testando geração de invoice Lightning...")
        
        test_script = f"""
<?php
require_once '{self.voltz_path}/voltz_invoice.php';

// Simular criação de invoice para 45000 sats
$amount_sats = 45000;
$description = 'Teste Ghost Bot';

$invoice_data = createInvoice($amount_sats, $description);
echo json_encode($invoice_data);
?>
"""
        
        try:
            temp_file = f"{self.backend_path}/test_invoice.php"
            with open(temp_file, 'w') as f:
                f.write(test_script)
            
            result = subprocess.run(['php', temp_file], capture_output=True, text=True)
            os.remove(temp_file)
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if response.get('success') and response.get('invoice'):
                        self.log("✅ Invoice Lightning gerado com sucesso!")
                        self.log(f"⚡ Invoice: {response['invoice'][:50]}...")
                        return True
                    else:
                        self.log(f"❌ Falha na geração: {response}")
                        return False
                except json.JSONDecodeError:
                    self.log(f"❌ Resposta inválida: {result.stdout}")
                    return False
            else:
                self.log(f"❌ Erro PHP: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao gerar invoice: {e}")
            return False
    
    def run_local_tests(self):
        """Executa todos os testes locais"""
        self.log("🧪 Iniciando testes locais da integração Voltz")
        self.log("=" * 60)
        
        tests = [
            ("Arquivos PHP", self.test_php_files_exist),
            ("Banco de Dados", self.test_database_connection),
            ("Registro Depósito", self.test_register_deposit_direct),
            ("Geração Invoice", self.test_voltz_invoice_generation)
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
        
        self.log(f"\n📊 Resumo: {passed}/{total} testes passaram")
        
        if passed == total:
            self.log("🎉 TODOS OS TESTES LOCAIS PASSARAM!")
            self.log("A integração Voltz está funcionando corretamente!")
            return True
        else:
            self.log("❌ ALGUNS TESTES FALHARAM")
            self.log("Verifique a configuração do backend.")
            return False

def main():
    print("🤖 Ghost Bot - Teste Local Integração Voltz")
    print("=" * 50)
    
    tester = TestVoltzLocal()
    
    try:
        success = tester.run_local_tests()
        
        if success:
            print("\n🎊 INTEGRAÇÃO VALIDADA LOCALMENTE!")
            print("O backend Voltz está pronto para uso.")
        else:
            print("\n⚠️  INTEGRAÇÃO PRECISA DE AJUSTES")
            print("Verifique os logs e arquivos do backend.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")

if __name__ == "__main__":
    main()
