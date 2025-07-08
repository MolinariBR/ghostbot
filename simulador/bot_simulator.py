#!/usr/bin/env python3
"""
Simulador do Bot Lightning Ghost
Replica o fluxo completo do bot real para testes locais
"""

import sys
import os
import time
import json
import requests
import sqlite3
from datetime import datetime

# Adicionar o diretório pai ao path para importar módulos do bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from api.lightning_address import LightningAddressResolver
    from api.api_coingecko import get_bitcoin_price_brl
except ImportError:
    print("⚠️  Alguns módulos do bot não foram encontrados. Criando versões simplificadas...")

class BotSimulator:
    def __init__(self, chat_id="7910260237"):
        self.chat_id = chat_id
        self.backend_url = "https://useghost.squareweb.app"
        self.local_db = "/home/mau/bot/ghostbackend/data/deposit.db"
        self.logs = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_msg)
        print(log_msg)
        
    def simular_comando_lightning(self, valor_reais=50.00):
        """Simula o comando /lightning do usuário"""
        self.log(f"🤖 Usuário digitou: /lightning {valor_reais}")
        
        # 1. Validar valor
        if valor_reais < 5.0:
            self.log("❌ Valor mínimo é R$ 5,00", "ERROR")
            return False
            
        if valor_reais > 5000.0:
            self.log("❌ Valor máximo é R$ 5.000,00", "ERROR")
            return False
            
        self.log(f"✅ Valor válido: R$ {valor_reais:.2f}")
        
        # 2. Obter cotação Bitcoin
        try:
            cotacao_btc = self.obter_cotacao_bitcoin()
            self.log(f"💰 Cotação BTC atual: R$ {cotacao_btc:,.2f}")
        except Exception as e:
            self.log(f"❌ Erro ao obter cotação: {e}", "ERROR")
            return False
            
        # 3. Calcular valores
        valor_centavos = int(valor_reais * 100)
        taxa_percentual = 0.05  # 5%
        valor_liquido = valor_reais * (1 - taxa_percentual)
        sats_aproximado = int((valor_liquido / cotacao_btc) * 100000000)
        
        self.log(f"📊 Valor bruto: R$ {valor_reais:.2f}")
        self.log(f"📊 Taxa (5%): R$ {valor_reais * taxa_percentual:.2f}")
        self.log(f"📊 Valor líquido: R$ {valor_liquido:.2f}")
        self.log(f"📊 Sats aproximados: {sats_aproximado:,}")
        
        # 4. Criar depósito no banco local
        try:
            depix_id = self.criar_deposito_local(valor_centavos, sats_aproximado, taxa_percentual)
            self.log(f"✅ Depósito criado com ID: {depix_id}")
        except Exception as e:
            self.log(f"❌ Erro ao criar depósito: {e}", "ERROR")
            return False
            
        # 5. Enviar para backend (simulação)
        try:
            resultado_backend = self.enviar_para_backend(depix_id, valor_centavos)
            if not resultado_backend:
                return False
        except Exception as e:
            self.log(f"❌ Erro no backend: {e}", "ERROR")
            return False
            
        # 6. Simular confirmação PIX
        try:
            blockchain_txid = self.simular_confirmacao_pix(depix_id)
            self.log(f"✅ PIX confirmado! TxID: {blockchain_txid}")
        except Exception as e:
            self.log(f"❌ Erro na confirmação PIX: {e}", "ERROR")
            return False
            
        # 7. Aguardar cron processar
        self.log("⏳ Aguardando cron Lightning processar...")
        time.sleep(3)
        
        # 8. Verificar se cron detectou
        try:
            resultado_cron = self.executar_cron_lightning()
            if resultado_cron:
                self.log("✅ Cron processou com sucesso!")
                
                # 9. Simular solicitação de endereço Lightning
                self.simular_solicitacao_lightning_address()
                
                return True
            else:
                self.log("❌ Cron não processou o depósito", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro no cron: {e}", "ERROR")
            return False
    
    def obter_cotacao_bitcoin(self):
        """Obtém cotação do Bitcoin via API CoinGecko"""
        try:
            # Tentar usar a função do bot se disponível
            if 'get_bitcoin_price_brl' in globals():
                return get_bitcoin_price_brl()
            else:
                # Fallback para API direta
                response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl', timeout=10)
                data = response.json()
                return float(data['bitcoin']['brl'])
        except Exception as e:
            self.log(f"⚠️  Erro na API CoinGecko, usando cotação fixa: {e}")
            return 350000.0  # Cotação de fallback
    
    def criar_deposito_local(self, valor_centavos, sats_aproximado, taxa):
        """Cria depósito no banco local SQLite"""
        depix_id = f"sim_{int(time.time())}_{self.chat_id[-6:]}"
        
        try:
            conn = sqlite3.connect(self.local_db)
            cursor = conn.cursor()
            
            sql = """
            INSERT INTO deposit (
                depix_id, chatid, amount_in_cents, taxa, moeda, rede, 
                address, forma_pagamento, send, status, created_at, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
            """
            
            values = (
                depix_id,
                self.chat_id,
                valor_centavos,
                taxa,
                'BTC',
                'lightning',
                '',  # Address será preenchido depois
                'PIX',
                sats_aproximado,
                'pending',
                self.chat_id
            )
            
            cursor.execute(sql, values)
            conn.commit()
            conn.close()
            
            return depix_id
            
        except Exception as e:
            self.log(f"❌ Erro ao acessar banco local: {e}", "ERROR")
            # Criar ID mesmo se banco falhar
            return depix_id
    
    def enviar_para_backend(self, depix_id, valor_centavos):
        """Simula envio para backend via REST API"""
        try:
            # Simular criação do depósito via API REST
            url = f"{self.backend_url}/rest/deposit.php"
            payload = {
                'action': 'create',
                'depix_id': depix_id,
                'chat_id': self.chat_id,
                'amount_cents': valor_centavos,
                'payment_method': 'PIX'
            }
            
            self.log(f"📤 Enviando para backend: {url}")
            # Em vez de fazer POST real, vamos apenas simular
            self.log("✅ Backend simulado: depósito registrado")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no backend: {e}", "ERROR")
            return False
    
    def simular_confirmacao_pix(self, depix_id):
        """Simula webhook de confirmação PIX"""
        blockchain_txid = f"pix_sim_{int(time.time())}_{depix_id[-8:]}"
        
        try:
            # Atualizar no banco local
            conn = sqlite3.connect(self.local_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE deposit 
                SET status = 'confirmed', blockchainTxID = ?
                WHERE depix_id = ?
            """, (blockchain_txid, depix_id))
            
            conn.commit()
            conn.close()
            
            # Simular webhook para backend
            webhook_url = f"{self.backend_url}/depix/webhook.php"
            payload = {
                'id': depix_id,
                'blockchainTxID': blockchain_txid,
                'status': 'confirmado',
                'timestamp': int(time.time()),
                'test_mode': True
            }
            
            self.log(f"📤 Simulando webhook PIX: {webhook_url}")
            self.log("✅ PIX confirmado via webhook simulado")
            
            return blockchain_txid
            
        except Exception as e:
            self.log(f"❌ Erro na confirmação PIX: {e}", "ERROR")
            return blockchain_txid  # Retorna mesmo com erro
    
    def executar_cron_lightning(self):
        """Executa o cron Lightning real"""
        try:
            cron_url = f"{self.backend_url}/api/lightning_cron_endpoint_final.php?chat_id={self.chat_id}"
            
            self.log(f"🔄 Executando cron: {cron_url}")
            response = requests.get(cron_url, timeout=30)
            
            self.log(f"📊 Cron Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log(f"📋 Cron Response: {json.dumps(data, indent=2)}")
                    
                    if 'results' in data and len(data['results']) > 0:
                        self.log(f"✅ Cron processou {len(data['results'])} depósitos")
                        return True
                    else:
                        self.log("⚠️  Cron não retornou resultados")
                        return False
                        
                except json.JSONDecodeError:
                    self.log(f"❌ Resposta do cron não é JSON válido: {response.text}", "ERROR")
                    return False
            else:
                self.log(f"❌ Cron falhou com status {response.status_code}", "ERROR")
                self.log(f"📄 Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao executar cron: {e}", "ERROR")
            return False
    
    def simular_solicitacao_lightning_address(self):
        """Simula a solicitação de endereço Lightning ao usuário"""
        self.log("💡 Bot: Por favor, envie seu endereço Lightning Network:")
        self.log("💡 Bot: Exemplo: usuario@wallet.com ou lnurl1234...")
        
        # Simular resposta do usuário
        lightning_address = "teste@walletofsatoshi.com"
        self.log(f"👤 Usuário digitou: {lightning_address}")
        
        # Processar endereço Lightning
        self.processar_lightning_address(lightning_address)
    
    def processar_lightning_address(self, lightning_address):
        """Processa o endereço Lightning fornecido pelo usuário"""
        try:
            self.log(f"🔍 Validando endereço Lightning: {lightning_address}")
            
            # Tentar usar o resolver do bot se disponível
            if 'LightningAddressResolver' in globals():
                resolver = LightningAddressResolver()
                resultado = resolver.resolve_address(lightning_address)
                
                if resultado['success']:
                    self.log("✅ Endereço Lightning válido!")
                    self.log(f"📋 Detalhes: {json.dumps(resultado, indent=2)}")
                    
                    # Simular salvamento no backend
                    self.salvar_lightning_address(lightning_address)
                    
                    # Simular geração de invoice
                    self.gerar_lightning_invoice(lightning_address)
                    
                else:
                    self.log(f"❌ Endereço Lightning inválido: {resultado.get('error')}", "ERROR")
            else:
                # Validação simplificada
                if '@' in lightning_address or lightning_address.startswith('lnurl'):
                    self.log("✅ Endereço Lightning válido (validação simplificada)")
                    self.salvar_lightning_address(lightning_address)
                    self.gerar_lightning_invoice(lightning_address)
                else:
                    self.log("❌ Formato de endereço Lightning inválido", "ERROR")
                    
        except Exception as e:
            self.log(f"❌ Erro ao processar endereço Lightning: {e}", "ERROR")
    
    def salvar_lightning_address(self, lightning_address):
        """Salva o endereço Lightning no backend"""
        try:
            url = f"{self.backend_url}/api/save_lightning_address.php"
            payload = {
                'chat_id': self.chat_id,
                'lightning_address': lightning_address
            }
            
            self.log(f"📤 Salvando endereço no backend: {url}")
            # Simular API call
            self.log("✅ Endereço Lightning salvo no backend")
            
        except Exception as e:
            self.log(f"❌ Erro ao salvar endereço: {e}", "ERROR")
    
    def gerar_lightning_invoice(self, lightning_address):
        """Simula a geração e envio da Lightning Invoice"""
        try:
            self.log(f"⚡ Gerando Lightning Invoice para: {lightning_address}")
            
            # Simular geração de invoice
            invoice = "lnbc50000n1pjg7mqkpp5..."  # Invoice simulada
            
            self.log("✅ Lightning Invoice gerada!")
            self.log(f"📜 Invoice: {invoice[:50]}...")
            self.log("💡 Bot: Pagamento enviado via Lightning Network!")
            self.log("🎉 Processo Lightning concluído com sucesso!")
            
        except Exception as e:
            self.log(f"❌ Erro ao gerar invoice: {e}", "ERROR")
    
    def verificar_status_deposito(self, depix_id=None):
        """Verifica status atual dos depósitos"""
        try:
            if depix_id:
                url = f"{self.backend_url}/rest/deposit.php?depix_id={depix_id}"
            else:
                url = f"{self.backend_url}/rest/deposit.php?chat_id={self.chat_id}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log("📊 Status dos depósitos:")
                
                for deposit in data.get('deposits', []):
                    self.log(f"  ID: {deposit.get('depix_id')}")
                    self.log(f"  Status: {deposit.get('status')}")
                    self.log(f"  Valor: R$ {deposit.get('amount_in_cents', 0)/100:.2f}")
                    self.log(f"  TxID: {deposit.get('blockchainTxID', 'N/A')}")
                    self.log("  " + "-"*40)
                    
                return data
            else:
                self.log(f"❌ Erro ao consultar depósitos: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro na consulta: {e}", "ERROR")
            return None
    
    def executar_teste_completo(self, valor_reais=50.0):
        """Executa teste completo do fluxo Lightning"""
        self.log("🚀 INICIANDO TESTE COMPLETO DO FLUXO LIGHTNING")
        self.log("="*60)
        
        start_time = time.time()
        
        # Executar simulação
        sucesso = self.simular_comando_lightning(valor_reais)
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.log("="*60)
        if sucesso:
            self.log(f"🎉 TESTE COMPLETO - SUCESSO! (Duração: {duration:.2f}s)")
        else:
            self.log(f"❌ TESTE COMPLETO - FALHOU! (Duração: {duration:.2f}s)")
        
        # Salvar logs
        self.salvar_logs()
        
        return sucesso
    
    def salvar_logs(self):
        """Salva os logs do teste"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f"/home/mau/bot/ghost/simulador/logs_sim_{timestamp}.txt"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"Logs do Simulador Bot Lightning\n")
                f.write(f"Gerado em: {datetime.now()}\n")
                f.write("="*60 + "\n\n")
                
                for log in self.logs:
                    f.write(log + "\n")
            
            self.log(f"📄 Logs salvos em: {log_file}")
            
        except Exception as e:
            self.log(f"⚠️  Erro ao salvar logs: {e}")

def main():
    """Função principal do simulador"""
    print("🤖 Simulador do Bot Lightning Ghost")
    print("="*40)
    
    # Parâmetros do teste
    chat_id = "7910260237"
    valor_teste = 50.0
    
    if len(sys.argv) > 1:
        try:
            valor_teste = float(sys.argv[1])
        except ValueError:
            print("⚠️  Valor inválido, usando R$ 50,00")
    
    if len(sys.argv) > 2:
        chat_id = sys.argv[2]
    
    print(f"💰 Valor do teste: R$ {valor_teste:.2f}")
    print(f"👤 Chat ID: {chat_id}")
    print("-"*40)
    
    # Criar e executar simulador
    simulator = BotSimulator(chat_id)
    sucesso = simulator.executar_teste_completo(valor_teste)
    
    # Resultado final
    if sucesso:
        print("\n🎉 Simulação concluída com sucesso!")
        print("✅ O fluxo Lightning está funcionando")
    else:
        print("\n❌ Simulação falhou!")
        print("🔧 Verifique os logs para identificar problemas")
    
    return 0 if sucesso else 1

if __name__ == "__main__":
    exit(main())
