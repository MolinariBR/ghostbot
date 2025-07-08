#!/usr/bin/env python3
"""
Teste específico do endpoint cron Lightning
Identifica e corrige problemas no cron
"""

import requests
import json
import time
import sys

class CronTester:
    def __init__(self):
        self.base_url = "https://useghost.squareweb.app"
        self.chat_id = "7910260237"
        
    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def testar_cron_basico(self):
        """Teste básico do cron sem parâmetros"""
        self.log("🔄 Testando cron básico...")
        
        try:
            url = f"{self.base_url}/api/lightning_cron_endpoint_final.php"
            response = requests.get(url, timeout=30)
            
            self.log(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log("✅ Resposta JSON válida")
                    self.log(f"📋 Dados: {json.dumps(data, indent=2)}")
                    return True
                except json.JSONDecodeError:
                    self.log("❌ Resposta não é JSON válido")
                    self.log(f"📄 Resposta bruta: {response.text}")
                    return False
            else:
                self.log(f"❌ HTTP Error: {response.status_code}")
                self.log(f"📄 Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"💥 Exceção: {e}")
            return False
    
    def testar_cron_com_chat_id(self):
        """Teste do cron com chat_id específico"""
        self.log(f"🔄 Testando cron com chat_id: {self.chat_id}")
        
        try:
            url = f"{self.base_url}/api/lightning_cron_endpoint_final.php?chat_id={self.chat_id}"
            response = requests.get(url, timeout=30)
            
            self.log(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log("✅ Resposta JSON válida")
                    self.log(f"📋 Dados: {json.dumps(data, indent=2)}")
                    
                    # Verificar se há resultados
                    if 'results' in data:
                        self.log(f"📈 Encontrados {len(data['results'])} depósitos pendentes")
                        for i, result in enumerate(data['results']):
                            self.log(f"  [{i+1}] Depix ID: {result.get('depix_id')}")
                            self.log(f"      Status: {result.get('status')}")
                            self.log(f"      BlockchainTxID: {result.get('blockchainTxID', 'N/A')}")
                    else:
                        self.log("⚠️  Campo 'results' não encontrado na resposta")
                    
                    return True
                except json.JSONDecodeError:
                    self.log("❌ Resposta não é JSON válido")
                    self.log(f"📄 Resposta bruta: {response.text}")
                    return False
            else:
                self.log(f"❌ HTTP Error: {response.status_code}")
                self.log(f"📄 Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"💥 Exceção: {e}")
            return False
    
    def testar_notifier(self):
        """Teste do lightning_notifier"""
        self.log(f"🔔 Testando lightning_notifier...")
        
        try:
            url = f"{self.base_url}/api/lightning_notifier.php?chat_id={self.chat_id}"
            response = requests.get(url, timeout=30)
            
            self.log(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log("✅ Notifier funcionando")
                    self.log(f"📋 Dados: {json.dumps(data, indent=2)}")
                    return True
                except json.JSONDecodeError:
                    self.log("❌ Resposta do notifier não é JSON")
                    self.log(f"📄 Resposta: {response.text}")
                    return False
            else:
                self.log(f"❌ Notifier falhou: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"💥 Exceção no notifier: {e}")
            return False
    
    def verificar_depositos_pendentes(self):
        """Verifica depósitos pendentes via REST API"""
        self.log("📊 Verificando depósitos pendentes...")
        
        try:
            url = f"{self.base_url}/rest/deposit.php?chat_id={self.chat_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                deposits = data.get('deposits', [])
                
                self.log(f"📈 Encontrados {len(deposits)} depósitos para chat_id {self.chat_id}")
                
                pendentes = 0
                confirmados = 0
                
                for deposit in deposits:
                    status = deposit.get('status')
                    blockchain_txid = deposit.get('blockchainTxID')
                    
                    if status == 'confirmed' and blockchain_txid and blockchain_txid.strip():
                        confirmados += 1
                        self.log(f"  ✅ {deposit.get('depix_id')} - Confirmado com TxID: {blockchain_txid}")
                    else:
                        pendentes += 1
                        self.log(f"  ⏳ {deposit.get('depix_id')} - Status: {status}, TxID: {blockchain_txid or 'VAZIO'}")
                
                self.log(f"📊 Resumo: {confirmados} confirmados, {pendentes} pendentes")
                return {'confirmados': confirmados, 'pendentes': pendentes, 'total': len(deposits)}
                
            else:
                self.log(f"❌ Erro ao consultar depósitos: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"💥 Erro na consulta: {e}")
            return None
    
    def executar_teste_completo(self):
        """Executa bateria completa de testes"""
        self.log("🧪 INICIANDO TESTE COMPLETO DO CRON LIGHTNING")
        self.log("="*60)
        
        resultados = {}
        
        # 1. Verificar depósitos pendentes
        self.log("\n1️⃣ VERIFICANDO DEPÓSITOS PENDENTES")
        resultados['depositos'] = self.verificar_depositos_pendentes()
        
        # 2. Testar cron básico
        self.log("\n2️⃣ TESTANDO CRON BÁSICO")
        resultados['cron_basico'] = self.testar_cron_basico()
        
        # 3. Testar cron com chat_id
        self.log("\n3️⃣ TESTANDO CRON COM CHAT_ID")
        resultados['cron_chat_id'] = self.testar_cron_com_chat_id()
        
        # 4. Testar notifier
        self.log("\n4️⃣ TESTANDO LIGHTNING NOTIFIER")
        resultados['notifier'] = self.testar_notifier()
        
        # 5. Resumo final
        self.log("\n" + "="*60)
        self.log("📊 RESUMO DOS TESTES")
        self.log("="*60)
        
        for teste, resultado in resultados.items():
            if teste == 'depositos':
                if resultado:
                    status = f"✅ {resultado['confirmados']} confirmados, {resultado['pendentes']} pendentes"
                else:
                    status = "❌ FALHA"
            else:
                status = "✅ SUCESSO" if resultado else "❌ FALHA"
            
            self.log(f"{teste:.<30} {status}")
        
        # Determinar se há problemas críticos
        problemas_criticos = []
        
        if not resultados.get('cron_basico'):
            problemas_criticos.append("Cron básico falhando")
        
        if not resultados.get('cron_chat_id'):
            problemas_criticos.append("Cron com chat_id falhando")
        
        if not resultados.get('notifier'):
            problemas_criticos.append("Lightning notifier falhando")
        
        if problemas_criticos:
            self.log("\n🚨 PROBLEMAS CRÍTICOS DETECTADOS:")
            for problema in problemas_criticos:
                self.log(f"  ❌ {problema}")
            
            self.log("\n🔧 SUGESTÕES:")
            self.log("  1. Verificar logs do PHP no servidor")
            self.log("  2. Verificar sintaxe do arquivo lightning_cron_endpoint_final.php")
            self.log("  3. Verificar conexão com banco de dados")
            self.log("  4. Verificar se todas as funções estão importadas corretamente")
            
            return False
        else:
            self.log("\n🎉 TODOS OS TESTES PASSARAM!")
            return True

def main():
    """Função principal"""
    print("🧪 Teste do Cron Lightning")
    print("="*40)
    
    tester = CronTester()
    
    if len(sys.argv) > 1:
        tester.chat_id = sys.argv[1]
        print(f"👤 Chat ID: {tester.chat_id}")
    
    sucesso = tester.executar_teste_completo()
    
    return 0 if sucesso else 1

if __name__ == "__main__":
    exit(main())
