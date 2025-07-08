#!/usr/bin/env python3
"""
Teste do fluxo Lightning com depósito real no servidor
Cria depósito via API REST e testa todo o fluxo
"""

import requests
import json
import time
import random

class FluxoLightningTester:
    def __init__(self):
        self.base_url = "https://useghost.squareweb.app"
        self.chat_id = "7910260237"
        
    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def criar_deposito_real(self, valor_reais=25.00):
        """Cria depósito real via API do servidor"""
        self.log(f"💰 Criando depósito de R$ {valor_reais:.2f}")
        
        try:
            # Gerar IDs únicos
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            depix_id = f"teste_flow_{timestamp}_{random_suffix}"
            blockchain_txid = f"pix_test_{timestamp}_{random_suffix}"
            
            valor_centavos = int(valor_reais * 100)
            
            # Simular criação via webhook Depix
            webhook_url = f"{self.base_url}/depix/webhook.php"
            payload = {
                'id': depix_id,
                'blockchainTxID': blockchain_txid,
                'status': 'confirmado',
                'timestamp': timestamp,
                'amount': valor_centavos,
                'chat_id': self.chat_id,
                'rede': 'lightning',
                'test_mode': True
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0'
            }
            
            self.log(f"📤 Webhook: {webhook_url}")
            self.log(f"🆔 Depix ID: {depix_id}")
            self.log(f"🔗 TxID: {blockchain_txid}")
            
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=30)
            
            self.log(f"📊 Webhook Status: {response.status_code}")
            
            if response.status_code == 200:
                self.log("✅ Depósito criado via webhook")
                return depix_id, blockchain_txid
            else:
                self.log(f"❌ Webhook falhou: {response.text}")
                return None, None
                
        except Exception as e:
            self.log(f"💥 Erro ao criar depósito: {e}")
            return None, None
    
    def verificar_deposito(self, depix_id):
        """Verifica se depósito foi criado corretamente"""
        try:
            url = f"{self.base_url}/rest/deposit.php?depix_id={depix_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                deposits = data.get('deposits', [])
                
                if deposits:
                    deposit = deposits[0]
                    self.log("✅ Depósito encontrado:")
                    self.log(f"  Status: {deposit.get('status')}")
                    self.log(f"  Valor: R$ {deposit.get('amount_in_cents', 0)/100:.2f}")
                    self.log(f"  TxID: {deposit.get('blockchainTxID')}")
                    self.log(f"  Rede: {deposit.get('rede')}")
                    return deposit
                else:
                    self.log("❌ Depósito não encontrado")
                    return None
            else:
                self.log(f"❌ Erro na consulta: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"💥 Erro na verificação: {e}")
            return None
    
    def executar_cron_lightning(self):
        """Executa cron Lightning para processar depósito"""
        try:
            self.log("⚡ Executando cron Lightning...")
            
            cron_url = f"{self.base_url}/api/lightning_cron_endpoint_final.php?chat_id={self.chat_id}"
            response = requests.get(cron_url, timeout=30)
            
            self.log(f"📊 Cron Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Cron executado com sucesso")
                
                if 'results' in data and len(data['results']) > 0:
                    self.log(f"📈 Cron processou {len(data['results'])} depósitos")
                    for result in data['results']:
                        self.log(f"  🔹 {result.get('depix_id')}: {result.get('result', {}).get('status')}")
                    return True
                else:
                    self.log("⚠️  Cron não processou nenhum depósito")
                    return False
            else:
                self.log(f"❌ Cron falhou: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"💥 Erro no cron: {e}")
            return False
    
    def verificar_notifier(self):
        """Verifica se notifier está funcionando"""
        try:
            self.log("🔔 Verificando lightning notifier...")
            
            url = f"{self.base_url}/api/lightning_notifier.php?chat_id={self.chat_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Notifier funcionando")
                self.log(f"📊 Pendentes: {data.get('total_pending', 0)}")
                self.log(f"📨 Notificados: {data.get('notified', 0)}")
                return True
            else:
                self.log(f"❌ Notifier falhou: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"💥 Erro no notifier: {e}")
            return False
    
    def executar_teste_completo(self, valor_reais=25.00):
        """Executa teste completo do fluxo Lightning"""
        self.log("🚀 TESTE COMPLETO DO FLUXO LIGHTNING REAL")
        self.log("="*60)
        
        # 1. Criar depósito real
        self.log("\n1️⃣ CRIANDO DEPÓSITO REAL")
        depix_id, blockchain_txid = self.criar_deposito_real(valor_reais)
        
        if not depix_id:
            self.log("❌ Falha na criação do depósito")
            return False
        
        # 2. Aguardar processamento
        self.log("\n⏳ Aguardando processamento (3s)...")
        time.sleep(3)
        
        # 3. Verificar depósito
        self.log("\n2️⃣ VERIFICANDO DEPÓSITO")
        deposit = self.verificar_deposito(depix_id)
        
        if not deposit:
            self.log("❌ Depósito não foi criado corretamente")
            return False
        
        # 4. Executar cron
        self.log("\n3️⃣ EXECUTANDO CRON LIGHTNING")
        cron_ok = self.executar_cron_lightning()
        
        # 5. Verificar notifier
        self.log("\n4️⃣ VERIFICANDO NOTIFIER")
        notifier_ok = self.verificar_notifier()
        
        # 6. Verificar status final
        self.log("\n5️⃣ STATUS FINAL DO DEPÓSITO")
        deposit_final = self.verificar_deposito(depix_id)
        
        # 7. Resultado
        self.log("\n" + "="*60)
        
        if deposit_final and deposit_final.get('status') == 'awaiting_client_invoice':
            self.log("🎉 TESTE COMPLETO - SUCESSO!")
            self.log("✅ Depósito criado e processado corretamente")
            self.log("✅ Status atualizado para 'awaiting_client_invoice'")
            self.log("✅ Bot deve solicitar endereço Lightning ao usuário")
            return True
        else:
            self.log("❌ TESTE COMPLETO - FALHOU!")
            if deposit_final:
                self.log(f"📊 Status final: {deposit_final.get('status')}")
            return False

def main():
    """Função principal"""
    print("🧪 Teste do Fluxo Lightning Real")
    print("="*40)
    
    tester = FluxoLightningTester()
    sucesso = tester.executar_teste_completo(25.00)
    
    return 0 if sucesso else 1

if __name__ == "__main__":
    exit(main())
