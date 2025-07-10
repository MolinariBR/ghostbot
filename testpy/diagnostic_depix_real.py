#!/usr/bin/env python3
"""
Diagnóstico Depix ID Real: 0197e9e7d0d17dfc9b9ee24c0c36ba2a
Teste do fluxo completo de pagamento Lightning
"""

import requests
import json
import time
import sqlite3

class DepixDiagnostic:
    
    def __init__(self, depix_id):
        self.depix_id = depix_id
        self.base_url = "https://useghost.squareweb.app"
        self.logs = []
        
    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        self.logs.append(log_msg)
        print(log_msg)
    
    def consultar_api_depix(self):
        """ETAPA 1: Consultar API Eulen Depix"""
        self.log("📡 ETAPA 1: Consultando API Eulen Depix...")
        
        try:
            url = f"https://depix.eulen.app/api/deposit-status?id={self.depix_id}"
            self.log(f"🔗 URL: {url}")
            
            response = requests.get(url, timeout=30)
            self.log(f"📊 HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Resposta JSON válida recebida")
                self.log(f"📋 Dados: {json.dumps(data, indent=2)}")
                return {'success': True, 'data': data}
            else:
                self.log(f"❌ HTTP Error: {response.status_code}")
                self.log(f"📄 Response: {response.text}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.log(f"💥 Exceção na consulta API: {e}")
            return {'success': False, 'error': str(e)}
    
    def verificar_banco_local(self):
        """ETAPA 2: Verificar banco local"""
        self.log("🗄️ ETAPA 2: Verificando banco local...")
        
        try:
            conn = sqlite3.connect('/home/mau/bot/ghostbackend/data/deposit.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM deposit WHERE depix_id = ?", (self.depix_id,))
            deposit = cursor.fetchone()
            
            if deposit:
                # Obter nomes das colunas
                columns = [description[0] for description in cursor.description]
                deposit_dict = dict(zip(columns, deposit))
                
                self.log("✅ Depósito encontrado no banco local")
                self.log(f"📋 Status atual: {deposit_dict.get('status', 'N/A')}")
                self.log(f"💰 Valor: {deposit_dict.get('amount_in_cents', 'N/A')} centavos")
                self.log(f"🔗 BlockchainTxID: {deposit_dict.get('blockchainTxID', 'VAZIO')}")
                self.log(f"⚡ Lightning Status: {deposit_dict.get('lightning_status', 'N/A')}")
                self.log(f"📅 Criado em: {deposit_dict.get('created_at', 'N/A')}")
                
                conn.close()
                return {'success': True, 'deposit': deposit_dict}
            else:
                self.log("❌ Depósito NÃO encontrado no banco local")
                conn.close()
                return {'success': False, 'error': 'Depósito não encontrado'}
                
        except Exception as e:
            self.log(f"💥 Erro ao consultar banco: {e}")
            return {'success': False, 'error': str(e)}
    
    def criar_deposito_teste(self, api_data=None):
        """ETAPA 3: Criar depósito de teste"""
        self.log("🆕 ETAPA 3: Criando depósito de teste...")
        
        try:
            # Usar dados da API se disponível
            if api_data and 'response' in api_data:
                amount = api_data['response'].get('amount', 5000)
                blockchain_txid = api_data['response'].get('blockchainTxID', f'teste_{int(time.time())}')
            else:
                amount = 5000  # R$ 50,00
                blockchain_txid = f'teste_{int(time.time())}'
            
            conn = sqlite3.connect('/home/mau/bot/ghostbackend/data/deposit.db')
            cursor = conn.cursor()
            
            sql = """
            INSERT OR REPLACE INTO deposit (
                depix_id, chatid, amount_in_cents, taxa, moeda, rede, address,
                forma_pagamento, send, status, blockchainTxID, comprovante, 
                user_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """
            
            values = (
                self.depix_id,
                '7910260237',  # Chat teste
                amount,
                '0.05',  # 5%
                'BTC',
                'lightning',
                'voltz@mail.com',
                'PIX',
                str(int(amount * 0.95 / 3.5)),  # sats aproximado
                'confirmed',  # Status confirmado
                blockchain_txid,
                '',  # Comprovante vazio
                '7910260237'
            )
            
            cursor.execute(sql, values)
            conn.commit()
            conn.close()
            
            self.log("✅ Depósito criado/atualizado com sucesso")
            self.log(f"💰 Valor: R$ {amount/100:.2f}")
            self.log(f"🔗 BlockchainTxID: {blockchain_txid}")
            
            return {'success': True, 'blockchain_txid': blockchain_txid}
            
        except Exception as e:
            self.log(f"💥 Erro ao criar depósito: {e}")
            return {'success': False, 'error': str(e)}
    
    def simular_webhook_depix(self, blockchain_txid=None):
        """ETAPA 4: Simular webhook Depix"""
        self.log("🔔 ETAPA 4: Simulando webhook Depix...")
        
        if not blockchain_txid:
            blockchain_txid = f'teste_{int(time.time())}_{self.depix_id[-8:]}'
        
        try:
            webhook_url = f"{self.base_url}/depix/webhook.php"
            payload = {
                'id': self.depix_id,
                'blockchainTxID': blockchain_txid,
                'status': 'confirmado',
                'timestamp': int(time.time()),
                'amount': 5000,  # R$ 50,00
                'test_mode': True
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0'
            }
            
            self.log(f"🔗 Webhook URL: {webhook_url}")
            self.log(f"📦 Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=30)
            
            self.log(f"📊 Webhook HTTP Status: {response.status_code}")
            self.log(f"📄 Webhook Response: {response.text}")
            
            if response.status_code == 200:
                self.log("✅ Webhook enviado com sucesso")
                return {'success': True, 'blockchain_txid': blockchain_txid}
            else:
                self.log(f"❌ Webhook falhou com código {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.log(f"💥 Erro no webhook: {e}")
            return {'success': False, 'error': str(e)}
    
    def executar_cron_lightning(self):
        """ETAPA 5: Executar cron Lightning"""
        self.log("⚡ ETAPA 5: Executando cron Lightning...")
        
        try:
            cron_url = f"{self.base_url}/api/lightning_cron_endpoint_final.php"
            self.log(f"🔗 Cron URL: {cron_url}")
            
            response = requests.get(cron_url, timeout=30)
            
            self.log(f"📊 Cron HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"📋 Cron Response: {json.dumps(data, indent=2)}")
                
                # Verificar se nosso depix_id foi processado
                if 'results' in data:
                    for result in data['results']:
                        if result.get('depix_id') == self.depix_id:
                            self.log("🎯 Nosso depix_id encontrado no cron!")
                            self.log(f"📋 Status: {json.dumps(result, indent=2)}")
                            break
                    else:
                        self.log("⚠️ Nosso depix_id NÃO foi encontrado no cron")
                
                return {'success': True, 'data': data}
            else:
                self.log(f"❌ Cron falhou com código {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.log(f"💥 Erro no cron: {e}")
            return {'success': False, 'error': str(e)}
    
    def executar_diagnostico_completo(self):
        """Executa diagnóstico completo"""
        self.log("🔬 INICIANDO DIAGNÓSTICO COMPLETO")
        self.log("=" * 60)
        
        resultados = {}
        
        # 1. Consultar API Depix
        resultados['api_depix'] = self.consultar_api_depix()
        
        # 2. Verificar banco local
        resultados['banco_inicial'] = self.verificar_banco_local()
        
        # 3. Criar depósito se não existir
        if not resultados['banco_inicial']['success']:
            api_data = resultados['api_depix'].get('data') if resultados['api_depix']['success'] else None
            resultados['criar_deposito'] = self.criar_deposito_teste(api_data)
        
        # 4. Simular webhook
        blockchain_txid = None
        if resultados['api_depix']['success']:
            blockchain_txid = resultados['api_depix']['data'].get('response', {}).get('blockchainTxID')
        
        resultados['webhook'] = self.simular_webhook_depix(blockchain_txid)
        
        # 5. Aguardar processamento
        self.log("⏳ Aguardando 3 segundos para processamento...")
        time.sleep(3)
        
        # 6. Verificar banco após webhook
        resultados['banco_pos_webhook'] = self.verificar_banco_local()
        
        # 7. Executar cron Lightning
        resultados['cron_lightning'] = self.executar_cron_lightning()
        
        self.log("🏁 DIAGNÓSTICO COMPLETO FINALIZADO")
        self.log("=" * 60)
        
        return {
            'depix_id': self.depix_id,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'resultados': resultados,
            'logs': self.logs
        }

if __name__ == "__main__":
    depix_id = '0197e9e7d0d17dfc9b9ee24c0c36ba2a'
    diagnostic = DepixDiagnostic(depix_id)
    
    resultado = diagnostic.executar_diagnostico_completo()
    
    print("\n" + "="*60)
    print("📊 RESUMO FINAL")
    print("="*60)
    
    for etapa, result in resultado['resultados'].items():
        status = "✅ SUCESSO" if result.get('success', False) else "❌ FALHA"
        print(f"{etapa:.<30} {status}")
    
    # Salvar resultado em arquivo
    with open('/tmp/depix_diagnostic.json', 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Resultado completo salvo em: /tmp/depix_diagnostic.json")
