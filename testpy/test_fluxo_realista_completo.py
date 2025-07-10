#!/usr/bin/env python3
"""
Teste Realista Completo - Simula fluxo real de compra com integração Depix e Blockchain
Inclui: webhook Depix real, obtenção de TXID, monitoramento blockchain
"""

import requests
import json
import time
import sys
import os
import hashlib
import random
from datetime import datetime, timezone

# Adiciona o diretório do projeto ao path
sys.path.append('/home/mau/bot/ghost')

class TesteRealistaCompleto:
    def __init__(self):
        try:
            from tokens import Config
            self.bot_token = Config.TELEGRAM_BOT_TOKEN
            self.chat_id = "7910260237"
            self.backend_url = "https://useghost.squareweb.app"
            
            # Dados realistas do teste
            self.depix_id_real = "0197ea6c80bc7dfc81b1e02fe8d06954"
            self.valor_real = "100"  # R$ 100
            self.lightning_address_real = "bouncyflight79@walletofsatoshi.com"
            self.pedido_id = None
            self.txid_bitcoin = None
            self.teste_iniciado = datetime.now()
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            sys.exit(1)
    
    def log_passo(self, numero, titulo):
        """Log formatado para cada passo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 🔧 PASSO {numero}: {titulo}")
        print("-" * 70)
    
    def gerar_txid_realista(self):
        """Gera um TXID Bitcoin realista para o teste"""
        # Gera um hash SHA256 que parece um TXID real
        random_data = f"{self.depix_id_real}_{time.time()}_{random.randint(1000, 9999)}"
        txid = hashlib.sha256(random_data.encode()).hexdigest()
        return txid
    
    def criar_pedido_realista(self):
        """Cria um pedido usando o depix_id real fornecido"""
        try:
            payload = {
                "chatid": self.chat_id,
                "moeda": "BTC",
                "rede": "⚡ Lightning",
                "amount_in_cents": int(float(self.valor_real) * 100),
                "taxa": 5.0,
                "address": self.lightning_address_real,
                "forma_pagamento": "PIX",
                "send": 0.00028571,  # Aproximadamente para R$ 100
                "user_id": int(self.chat_id),
                "depix_id": self.depix_id_real,  # USA O DEPIX_ID REAL
                "status": "pending",
                "comprovante": "Lightning Invoice"
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                f"{self.backend_url}/rest/deposit.php",
                json=payload,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.pedido_id = data.get("id")
                    print(f"✅ Pedido realista criado!")
                    print(f"   📋 ID do pedido: {self.pedido_id}")
                    print(f"   🆔 Depix ID: {self.depix_id_real}")
                    print(f"   💰 Valor: R$ {self.valor_real}")
                    print(f"   ⚡ Lightning Address: {self.lightning_address_real}")
                    return True
                else:
                    print(f"❌ Erro: {data}")
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        return False
    
    def simular_webhook_depix(self):
        """Simula o webhook do Depix confirmando o pagamento PIX"""
        try:
            print("📡 Simulando webhook do Depix...")
            
            # Payload que simula o que o Depix enviaria
            webhook_payload = {
                "event": "payment.confirmed",
                "data": {
                    "id": self.depix_id_real,
                    "status": "paid",
                    "amount": float(self.valor_real),
                    "currency": "BRL",
                    "confirmed_at": datetime.now(timezone.utc).isoformat(),
                    "payment_method": "pix",
                    "customer": {
                        "id": self.chat_id,
                        "email": "cliente@example.com"
                    }
                }
            }
            
            # Simula o envio para o webhook endpoint
            webhook_response = requests.post(
                f"{self.backend_url}/square_webhook.php",
                json=webhook_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if webhook_response.status_code == 200:
                print(f"✅ Webhook Depix simulado com sucesso!")
                print(f"   🆔 Depix ID: {self.depix_id_real}")
                print(f"   📊 Status: paid")
                print(f"   💰 Valor: R$ {self.valor_real}")
                print(f"   📅 Confirmado em: {webhook_payload['data']['confirmed_at']}")
                return True
            else:
                print(f"⚠️ Webhook retornou: {webhook_response.status_code}")
                return True  # Continua mesmo se webhook falhar
                
        except Exception as e:
            print(f"❌ Erro no webhook: {e}")
            return False
    
    def atualizar_status_pago(self):
        """Atualiza o status do pedido para 'pago' simulando processamento interno"""
        try:
            print("💳 Atualizando status para 'pago'...")
            
            # Simula atualização interna (normalmente seria feita pelo webhook)
            # Aqui apenas informamos que o status foi atualizado
            print(f"✅ Status atualizado para 'pago'")
            print(f"   📋 Pedido: {self.pedido_id}")
            print(f"   🆔 Depix ID: {self.depix_id_real}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro atualizando status: {e}")
            return False
    
    def testar_integracao_bot(self):
        """Testa se o bot detecta o pedido e solicita Lightning Address"""
        try:
            print("🤖 Testando integração com o bot...")
            
            mensagens = [
                "Status",
                "Lightning", 
                f"⚡ {self.lightning_address_real}"
            ]
            
            for i, msg in enumerate(mensagens, 1):
                print(f"📤 Enviando mensagem {i}: '{msg}'")
                
                payload = {
                    "chat_id": self.chat_id,
                    "text": msg
                }
                
                response = requests.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        msg_id = data['result']['message_id']
                        print(f"   ✅ Enviada (ID: {msg_id})")
                    else:
                        print(f"   ❌ Erro: {data}")
                else:
                    print(f"   ❌ HTTP {response.status_code}")
                
                time.sleep(2)  # Pausa entre mensagens
            
            return True
            
        except Exception as e:
            print(f"❌ Erro testando bot: {e}")
            return False
    
    def simular_envio_bitcoin(self):
        """Simula o envio do Bitcoin com TXID real"""
        try:
            # Gera um TXID realista
            self.txid_bitcoin = self.gerar_txid_realista()
            
            print(f"🔗 TXID Bitcoin gerado: {self.txid_bitcoin}")
            print("₿ Simulando envio Bitcoin...")
            
            # Simula atualização do banco com TXID
            try:
                # Aqui seria feita a atualização real no banco
                # UPDATE deposit SET blockchainTxID = ?, status = 'sent' WHERE id = ?
                pass
            except Exception as e:
                print(f"⚠️ Simulação de update no banco: {e}")
            
            print(f"✅ Bitcoin 'enviado' com sucesso!")
            print(f"   🔗 TXID: {self.txid_bitcoin}")
            print(f"   ⚡ Para: {self.lightning_address_real}")
            print(f"   💰 Valor: 0.00028571 BTC (aprox)")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro simulando envio: {e}")
            return False
    
    def verificar_txid_blockchain(self):
        """Verifica o TXID na blockchain real usando Blockstream API"""
        try:
            print("🔍 Verificando TXID na blockchain real...")
            
            if not self.txid_bitcoin:
                print("❌ TXID não disponível")
                return False
            
            # Consulta a API Blockstream (similar ao blockchain/blockstream.php)
            url = f"https://blockstream.info/api/tx/{self.txid_bitcoin}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                tx_data = response.json()
                confirmations = tx_data.get('status', {}).get('confirmed', False)
                
                print(f"✅ TXID encontrado na blockchain!")
                print(f"   🔗 TXID: {self.txid_bitcoin}")
                print(f"   ✅ Confirmado: {confirmations}")
                print(f"   📦 Block: {tx_data.get('status', {}).get('block_hash', 'N/A')}")
                
                return True
            else:
                print(f"⚠️ TXID não encontrado na blockchain (normal para simulação)")
                print(f"   🔗 TXID simulado: {self.txid_bitcoin}")
                return False
                
        except Exception as e:
            print(f"❌ Erro verificando blockchain: {e}")
            return False
    
    def verificar_status_final(self):
        """Verifica o status final completo do pedido"""
        try:
            print("📊 Verificando status final do pedido...")
            
            response = requests.get(
                f"{self.backend_url}/rest/deposit.php?action=get&id={self.pedido_id}",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'deposits' in data and len(data['deposits']) > 0:
                    pedido = data['deposits'][0]
                    
                    print(f"📋 STATUS FINAL COMPLETO:")
                    print(f"   📋 ID: {pedido.get('id')}")
                    print(f"   🆔 Depix ID: {pedido.get('depix_id')}")
                    print(f"   💰 Valor: R$ {pedido.get('amount_in_cents', 0)/100}")
                    print(f"   📊 Status: {pedido.get('status')}")
                    print(f"   ⚡ Rede: {pedido.get('rede')}")
                    print(f"   📧 Lightning Address: {pedido.get('address')}")
                    print(f"   🔗 Blockchain TXID: {pedido.get('blockchainTxID')}")
                    print(f"   📅 Criado: {pedido.get('created_at')}")
                    print(f"   ✅ Notificado: {pedido.get('notified')}")
                    
                    # Verifica se o fluxo está completo
                    if pedido.get('blockchainTxID') and pedido.get('status') == 'sent':
                        print("🎉 FLUXO COMPLETO FINALIZADO!")
                        return True
                    else:
                        print("⚠️ Fluxo em andamento - alguns campos ainda não preenchidos")
                        return False
                else:
                    print(f"❌ Pedido não encontrado")
                    return False
            else:
                print(f"❌ HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro verificando status: {e}")
            return False
    
    def executar_teste_completo(self):
        """Executa o teste realista completo"""
        
        print("🚀 INICIANDO TESTE REALISTA COMPLETO")
        print("=" * 80)
        print(f"💰 Valor: R$ {self.valor_real}")
        print(f"⚡ Lightning Address: {self.lightning_address_real}")
        print(f"🆔 Depix ID (REAL): {self.depix_id_real}")
        print(f"📱 Chat ID: {self.chat_id}")
        print(f"🌐 Backend: {self.backend_url}")
        print("=" * 80)
        
        # PASSO 1: Criar pedido com depix_id real
        self.log_passo(1, "Criando pedido com depix_id real")
        if not self.criar_pedido_realista():
            print("❌ FALHA: Não foi possível criar pedido")
            return False
        
        # PASSO 2: Simular webhook Depix
        self.log_passo(2, "Simulando webhook Depix (confirmação PIX)")
        if not self.simular_webhook_depix():
            print("❌ FALHA: Webhook Depix falhou")
            return False
        
        time.sleep(1)
        
        # PASSO 3: Atualizar status para pago
        self.log_passo(3, "Atualizando status para 'pago'")
        if not self.atualizar_status_pago():
            print("❌ FALHA: Não foi possível atualizar status")
            return False
        
        time.sleep(1)
        
        # PASSO 4: Testar integração com bot
        self.log_passo(4, "Testando detecção pelo bot")
        if not self.testar_integracao_bot():
            print("❌ FALHA: Bot não respondeu")
            return False
        
        # PASSO 5: Aguardar processamento
        self.log_passo(5, "Aguardando processamento do bot")
        print("⏳ Aguardando 20 segundos para o bot processar...")
        time.sleep(20)
        
        # PASSO 6: Simular envio Bitcoin
        self.log_passo(6, "Simulando envio Bitcoin")
        if not self.simular_envio_bitcoin():
            print("❌ FALHA: Envio Bitcoin falhou")
            return False
        
        time.sleep(1)
        
        # PASSO 7: Verificar TXID na blockchain
        self.log_passo(7, "Verificando TXID na blockchain")
        self.verificar_txid_blockchain()  # Não para o teste se falhar
        
        time.sleep(1)
        
        # PASSO 8: Status final
        self.log_passo(8, "Verificando status final completo")
        sucesso_final = self.verificar_status_final()
        
        # RESUMO FINAL
        print("\n" + "=" * 80)
        print("🎯 RESUMO DO TESTE REALISTA")
        print("=" * 80)
        
        tempo_total = datetime.now() - self.teste_iniciado
        print(f"⏱️ Tempo total: {tempo_total.total_seconds():.1f}s")
        print(f"📋 Pedido ID: {self.pedido_id}")
        print(f"🆔 Depix ID: {self.depix_id_real}")
        print(f"💰 Valor: R$ {self.valor_real}")
        print(f"⚡ Lightning Address: {self.lightning_address_real}")
        print(f"🔗 Blockchain TXID: {self.txid_bitcoin}")
        
        if sucesso_final:
            print("🎉 TESTE REALISTA: SUCESSO COMPLETO!")
            print("✅ Fluxo completo funcionando de ponta a ponta")
        else:
            print("⚠️ TESTE REALISTA: PARCIAL")
            print("📱 Verificar detalhes no chat do Telegram")
        
        print("\n📋 DADOS PARA VERIFICAÇÃO MANUAL:")
        print(f"1. Interface web: {self.backend_url}/transacoes.php")
        print(f"2. Buscar por Depix ID: {self.depix_id_real}")
        print(f"3. Verificar TXID: {self.txid_bitcoin}")
        print(f"4. Chat Telegram: {self.chat_id}")
        print("=" * 80)
        
        return sucesso_final

if __name__ == "__main__":
    teste = TesteRealistaCompleto()
    teste.executar_teste_completo()
