#!/usr/bin/env python3
"""
Teste completo do fluxo de compra - Da solicitação ao envio dos BTC
Simula todo o processo: pedido -> pagamento -> confirmação -> envio BTC
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from decimal import Decimal

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa módulos internos do Ghost Bot
from ghost.api.lightning_address import LightningAddressResolver
from ghost.api.api_binance import binance_api
from ghost.api.api_coingecko import coingecko_api
from ghost.limites.limite_valor import LimitesValor
from ghost.limites.comissao import ComissaoCalculator
from ghost.handlers.lightning_handler import GhostBotLightningHandler

class TesteFluxoCompleto:
    def __init__(self):
        try:
            from tokens import Config
            self.bot_token = Config.TELEGRAM_BOT_TOKEN
            self.chat_id = "7910260237"
            self.backend_url = "https://useghost.squareweb.app"
            self.telegram_api_url = f"https://api.telegram.org/bot{self.bot_token}"
            
            # Dados do teste
            self.valor_compra = "10"  # Valor mínimo correto é R$ 10,00
            self.lightning_address = "bouncyflight79@walletofsatoshi.com"
            self.pedido_id = None
            self.teste_iniciado = datetime.now()
            
            # Inicializa handlers e APIs
            self.lightning_handler = GhostBotLightningHandler(self.bot_token)
            self.limites = LimitesValor()
            self.comissao_calc = ComissaoCalculator()
            
            # Escolhe API de cotação (Binance como primária, CoinGecko como fallback)
            self.api_cotacao = binance_api
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            sys.exit(1)
    
    def log_passo(self, passo, mensagem):
        """Log formatado para cada passo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 📋 PASSO {passo}: {mensagem}")
        print("-" * 60)
    
    def enviar_mensagem_bot(self, texto, aguardar=3):
        """Envia mensagem para o bot via Telegram API"""
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": texto
            }
            
            response = requests.post(
                f"{self.telegram_api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                resp_data = response.json()
                if resp_data.get('ok'):
                    msg_id = resp_data['result']['message_id']
                    print(f"✅ Mensagem enviada: '{texto}' (ID: {msg_id})")
                    if aguardar > 0:
                        print(f"⏳ Aguardando {aguardar}s para resposta...")
                        time.sleep(aguardar)
                    return True
                else:
                    print(f"❌ Erro API: {resp_data}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro enviando mensagem: {e}")
        
        return False
    
    def calcular_comissao_fallback(self, valor_reais):
        """Fallback para cálculo de comissão quando a API falha"""
        try:
            valor = float(valor_reais)
            
            # Estrutura de comissões do Ghost Bot
            if valor >= 10 and valor <= 500:
                # Faixa de R$ 10 a R$ 500: 10%
                taxa_percentual = 10.0
                taxa_fixa = 0.0
                comissao_total = valor * 0.10
                
            elif valor > 500 and valor <= 1000:
                # Faixa de R$ 500 a R$ 1000: 7%
                taxa_percentual = 7.0
                taxa_fixa = 0.0
                comissao_total = valor * 0.07
                
            elif valor > 1000:
                # Acima de R$ 1000: 5%
                taxa_percentual = 5.0
                taxa_fixa = 0.0
                comissao_total = valor * 0.05
                
            else:
                # Abaixo de R$ 10 (não deveria acontecer devido aos limites)
                taxa_percentual = 10.0
                taxa_fixa = 0.0
                comissao_total = valor * 0.10
            
            print(f"📊 Comissão fallback calculada:")
            print(f"   💰 Valor: R$ {valor:.2f}")
            print(f"   📈 Taxa: {taxa_percentual:.1f}%")
            print(f"   💸 Comissão: R$ {comissao_total:.2f}")
            
            return {
                'valor_original': valor,
                'percentual': taxa_percentual / 100,  # Converte para decimal
                'fixo': taxa_fixa,
                'comissao_total': comissao_total,
                'taxa_percentual': taxa_percentual
            }
            
        except Exception as e:
            print(f"❌ Erro no fallback de comissão: {e}")
            # Fallback final: 10% para valores até R$ 500
            return {
                'valor_original': float(valor_reais),
                'percentual': 0.10,
                'fixo': 0.0,
                'comissao_total': float(valor_reais) * 0.10,
                'taxa_percentual': 10.0
            }

    def criar_pedido_backend(self):
        """Cria um pedido direto no backend para simular a compra"""
        try:
            # Usa a mesma estrutura dos outros testes
            self.depix_id = f"DEPIX_{self.chat_id}_{int(time.time())}"
            
            # Valida limites antes de criar pedido
            if not self.validar_limites_valor():
                return False
            
            # Calcula comissão usando nosso sistema
            valor_decimal = Decimal(str(self.valor_compra))
            try:
                comissao_info = self.comissao_calc.calcular_comissao(float(valor_decimal), 'BTC')
                
                if comissao_info and isinstance(comissao_info, dict):
                    # Verifica se tem todas as chaves necessárias
                    if 'comissao_total' in comissao_info:
                        print(f"💰 Comissão calculada: R$ {comissao_info['comissao_total']:.2f}")
                        if 'percentual' in comissao_info and 'fixo' in comissao_info:
                            print(f"   📊 {comissao_info['percentual']*100:.1f}% + R$ {comissao_info['fixo']:.2f}")
                            taxa_percentual = float(comissao_info['percentual'] * 100)
                        else:
                            # Usa o fallback se não tem os campos necessários
                            print("⚠️ Comissão incompleta, usando fallback inteligente")
                            comissao_fallback = self.calcular_comissao_fallback(self.valor_compra)
                            taxa_percentual = comissao_fallback['taxa_percentual']
                    else:
                        # Usa o fallback se não tem comissao_total
                        print("⚠️ Comissão sem 'comissao_total', usando fallback inteligente")
                        comissao_fallback = self.calcular_comissao_fallback(self.valor_compra)
                        taxa_percentual = comissao_fallback['taxa_percentual']
                else:
                    # Usa o fallback se comissao_info é inválido
                    print("⚠️ Comissão inválida, usando fallback inteligente")
                    comissao_fallback = self.calcular_comissao_fallback(self.valor_compra)
                    taxa_percentual = comissao_fallback['taxa_percentual']
                    
            except Exception as e:
                print(f"⚠️ Erro calculando comissão: {e}")
                print("🔄 Usando fallback inteligente de comissão")
                comissao_fallback = self.calcular_comissao_fallback(self.valor_compra)
                taxa_percentual = comissao_fallback['taxa_percentual']
            
            # Calcula valor BTC usando nossa API de cotação
            valor_btc = self.calcular_valor_btc_real()
            
            payload = {
                "chatid": self.chat_id,
                "moeda": "BTC",
                "rede": "⚡ Lightning", 
                "amount_in_cents": int(float(self.valor_compra) * 100),  # Converte para centavos
                "taxa": taxa_percentual,
                "address": self.lightning_address,
                "forma_pagamento": "PIX",
                "send": float(valor_btc),  # Valor BTC calculado via API real
                "user_id": int(self.chat_id),
                "depix_id": self.depix_id,
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
                    print(f"✅ Pedido criado no backend!")
                    print(f"   📋 ID: {self.pedido_id}")
                    print(f"   💰 Valor: R$ {self.valor_compra}")
                    print(f"   ⚡ Rede: Lightning")
                    print(f"   🆔 depix_id: {self.depix_id}")
                    print(f"   📊 Taxa: {taxa_percentual:.1f}%")
                    return True
                else:
                    print(f"❌ Erro criando pedido: {data}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Erro criando pedido: {e}")
        return False
    
    def simular_pagamento_pix(self):
        """Simula confirmação de pagamento PIX"""
        if not self.pedido_id:
            print("❌ Pedido ID não encontrado!")
            return False
        
        try:
            # Simula apenas mudando status para pago
            print(f"✅ Pagamento PIX simulado!")
            print(f"   📋 Pedido: {self.pedido_id}")
            print(f"   ✅ Status: Pago (simulado)")
            print("   💡 Na produção, o Smart PIX Monitor detectaria automaticamente")
            return True
                
        except Exception as e:
            print(f"❌ Erro simulando pagamento: {e}")
        
        return False
    
    def verificar_pedido_pendente(self):
        """Verifica se o bot detecta o pedido como pendente (busca por depix_id se possível, nunca processa múltiplos)"""
        try:
            # Primeiro tenta buscar diretamente por depix_id (se o backend suportar)
            url_get_by_depix = f"{self.backend_url}/rest/deposit.php?action=get&depix_id={self.depix_id}"
            response = requests.get(url_get_by_depix, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Se vier um pedido único, já retorna
                    if isinstance(data, dict) and str(data.get("depix_id")) == str(self.depix_id):
                        print(f"✅ Pedido encontrado por depix_id!")
                        self._print_pedido_resumido(data)
                        return True
                except Exception as e:
                    print(f"⚠️ Erro ao decodificar resposta por depix_id: {e}")
                # Se não encontrou, faz fallback para busca na lista

            # Fallback: busca na lista de pedidos do usuário
            url_list = f"{self.backend_url}/rest/deposit.php?action=list&chatid={self.chat_id}"
            response = requests.get(url_list, timeout=15)
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"[DEBUG] Resposta bruta da API de pedidos: {json.dumps(data, indent=2)}")
                    pedidos = data.get('deposits', [])
                    encontrados = [p for p in pedidos if str(p.get("depix_id")) == str(self.depix_id)]
                    if len(encontrados) == 1:
                        pedido = encontrados[0]
                        print(f"✅ Pedido encontrado no backend!")
                        self._print_pedido_resumido(pedido)
                        return True
                    elif len(encontrados) > 1:
                        print(f"⚠️ Atenção: Mais de um pedido com o mesmo depix_id encontrado! Isso não deveria acontecer.")
                        for pedido in encontrados:
                            self._print_pedido_resumido(pedido, prefixo='[DUPLICADO] ')
                        return True  # Considera encontrado, mas alerta
                    else:
                        print("⚠️ Pedido não encontrado na consulta (filtrando por depix_id)")
                        return False
                except json.JSONDecodeError:
                    print("⚠️ Resposta não é JSON válido")
                    return False
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Erro verificando pendentes: {e}")
        return False

    def _print_pedido_resumido(self, pedido, prefixo=''):
        """Exibe apenas os campos essenciais do pedido, ignorando campos nulos/irrelevantes"""
        print(f"   {prefixo}📋 ID: {pedido.get('id', pedido.get('depix_id'))}")
        print(f"   {prefixo}💰 Valor: R$ {pedido.get('amount_in_cents', 0)/100}")
        print(f"   {prefixo}⚡ Rede: {pedido.get('rede')}")
        print(f"   {prefixo}🆔 depix_id: {pedido.get('depix_id')}")
        print(f"   {prefixo}� Status: {pedido.get('status')}")
        if pedido.get('blockchainTxID'):
            print(f"   {prefixo}🔗 blockchainTxID: {pedido.get('blockchainTxID')}")
        if pedido.get('address'):
            print(f"   {prefixo}🏷️ Address: {pedido.get('address')}")
        if pedido.get('created_at'):
            print(f"   {prefixo}📅 Criado: {pedido.get('created_at')}")
    
    def verificar_logs_bot(self):
        """Verifica os logs recentes do bot no servidor"""
        try:
            print("📋 VERIFICANDO LOGS DO BOT NO SERVIDOR:")
            
            # Lista de possíveis endpoints de logs no servidor
            log_endpoints = [
                f"{self.backend_url}/logs/bot.log",
                f"{self.backend_url}/logs/fluxo.log", 
                f"{self.backend_url}/api/logs.php",
                f"{self.backend_url}/admin/logs.php",
                f"{self.backend_url}/diagnostic/logs.php",
                f"{self.backend_url}/rest/logs.php"
            ]
            
            logs_encontrados = False
            
            for endpoint in log_endpoints:
                try:
                    print(f"\n🔍 Tentando acessar: {endpoint}")
                    response = requests.get(endpoint, timeout=10)
                    
                    if response.status_code == 200:
                        content = response.text
                        
                        # Verifica se parece ser um log válido
                        if any(keyword in content.lower() for keyword in 
                               ['lightning', 'bot', 'telegram', 'error', 'info', 'debug']):
                            print(f"✅ Log encontrado em: {endpoint}")
                            
                            # Mostra as últimas linhas relevantes
                            lines = content.split('\n')
                            recent_lines = [line for line in lines[-20:] if line.strip()]
                            
                            print(f"📄 Últimas entradas relevantes:")
                            for line in recent_lines:
                                if any(keyword in line.lower() for keyword in 
                                       ['lightning', 'pendente', 'endereço', 'invoice', 'erro', 'address']):
                                    print(f"   🔍 {line.strip()}")
                            
                            logs_encontrados = True
                        else:
                            print(f"⚠️ Endpoint acessível mas não parece ser log")
                    
                    elif response.status_code == 404:
                        print(f"❌ Não encontrado (404)")
                    elif response.status_code == 403:
                        print(f"❌ Acesso negado (403)")
                    else:
                        print(f"❌ HTTP {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    print(f"⏱️ Timeout")
                except requests.exceptions.ConnectionError:
                    print(f"🔌 Erro de conexão")
                except Exception as e:
                    print(f"❌ Erro: {e}")
            
            if not logs_encontrados:
                print("\n⚠️ Nenhum log acessível via HTTP encontrado.")
                print("💡 Os logs podem estar em:")
                print("   - Arquivos protegidos no servidor")
                print("   - Endpoint admin que requer autenticação")
                print("   - Sistema de logs centralizado")
                print("   - Console/terminal do servidor")
            
            return logs_encontrados
            
        except Exception as e:
            print(f"❌ Erro verificando logs do servidor: {e}")
            return False
    
    def simular_envio_lightning_address(self):
        """Simula o cliente fornecendo Lightning Address usando o handler integrado"""
        try:
            # Valida o Lightning Address usando o handler
            if not self.lightning_handler.is_lightning_address(self.lightning_address):
                print(f"❌ Lightning Address inválido: {self.lightning_address}")
                return False
            
            print(f"✅ Lightning Address validado: {self.lightning_address}")
            
            # Envia a mensagem
            result = self.enviar_mensagem_bot(self.lightning_address, 5)
            
            if result:
                print("📋 Lightning Address processado pelo handler interno")
            
            return result
            
        except Exception as e:
            print(f"❌ Erro no handler Lightning: {e}")
            return self.enviar_mensagem_bot(self.lightning_address, 5)  # Fallback
    
    def verificar_finalizacao(self):
        """Verifica se o pedido foi finalizado e BTC enviado"""
        if not self.pedido_id:
            return False
        
        try:
            # Consulta o status do pedido
            response = requests.get(
                f"{self.backend_url}/rest/deposit.php?action=get&id={self.pedido_id}",
                timeout=15
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    print(f"📋 STATUS FINAL DO PEDIDO:")
                    print(f"   📋 ID: {data.get('id', self.pedido_id)}")
                    print(f"   💰 Valor: R$ {data.get('amount_in_cents', 0)/100}")
                    print(f"   📊 Status: {data.get('status', 'N/A')}")
                    print(f"   ⚡ Rede: {data.get('rede', 'N/A')}")
                    print(f"   � Lightning Address: {data.get('address', 'N/A')}")
                    print(f"   📅 Criado: {data.get('created_at', 'N/A')}")
                    
                    status = data.get("status", "").lower()
                    if status in ['finalizado', 'enviado', 'concluido', 'completed', 'sent']:
                        print("🎉 PEDIDO FINALIZADO COM SUCESSO!")
                        return True
                    else:
                        print(f"⚠️ Pedido ainda em andamento (Status: {status})")
                        return False
                        
                except json.JSONDecodeError:
                    print("⚠️ Resposta não é JSON válido")
                    return False
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro verificando finalização: {e}")
        
        return False
    
    def validar_limites_valor(self):
        """Valida se o valor está dentro dos limites permitidos"""
        try:
            valor = float(self.valor_compra)
            
            # Verifica limites mínimos e máximos
            if valor < self.limites.PIX_COMPRA_MIN:
                print(f"❌ Valor abaixo do mínimo: R$ {valor:.2f} < R$ {self.limites.PIX_COMPRA_MIN:.2f}")
                return False
            
            if valor > self.limites.PIX_COMPRA_MAX:
                print(f"❌ Valor acima do máximo: R$ {valor:.2f} > R$ {self.limites.PIX_COMPRA_MAX:.2f}")
                return False
            
            print(f"✅ Valor dentro dos limites: R$ {self.limites.PIX_COMPRA_MIN:.2f} ≤ R$ {valor:.2f} ≤ R$ {self.limites.PIX_COMPRA_MAX:.2f}")
            return True
            
        except Exception as e:
            print(f"❌ Erro validando limites: {e}")
            return False
    
    def calcular_valor_btc_real(self):
        """Calcula o valor BTC usando nossa API de cotação real"""
        try:
            print("💰 Obtendo cotação real do Bitcoin...")
            
            # Tenta Binance primeiro
            try:
                price_brl = self.api_cotacao.get_btc_price_brl()
                valor_btc = Decimal(str(self.valor_compra)) / price_brl
                print(f"✅ Binance - BTC/BRL: R$ {price_brl:,.2f}")
                print(f"📊 R$ {self.valor_compra} = {valor_btc:.8f} BTC")
                return valor_btc
                
            except Exception as e:
                print(f"⚠️ Erro na Binance: {e}")
                print("🔄 Tentando CoinGecko como fallback...")
                
                # Fallback para CoinGecko
                price_brl = coingecko_api.get_btc_price_brl()
                valor_btc = Decimal(str(self.valor_compra)) / price_brl
                print(f"✅ CoinGecko - BTC/BRL: R$ {price_brl:,.2f}")
                print(f"📊 R$ {self.valor_compra} = {valor_btc:.8f} BTC")
                return valor_btc
                
        except Exception as e:
            print(f"❌ Erro em todas as APIs: {e}")
            # Fallback final
            fallback_price = Decimal('350000')  # R$ 350k estimado
            valor_btc = Decimal(str(self.valor_compra)) / fallback_price
            print(f"⚠️ Usando cotação estimada: R$ {fallback_price:,.2f}")
            print(f"📊 R$ {self.valor_compra} = {valor_btc:.8f} BTC (estimado)")
            return valor_btc
    
    def calcular_sats_equivalente(self, valor_reais):
        """Calcula o valor em sats equivalente ao valor em reais usando nossa API"""
        try:
            print(f"🔢 Calculando {valor_reais} reais em sats...")
            
            # Usa o mesmo método de cotação real
            valor_btc = self.calcular_valor_btc_real()
            valor_sats = int(valor_btc * 100_000_000)  # 1 BTC = 100M sats
            
            print(f"📊 Resultado: {valor_sats:,} sats")
            return valor_sats
            
        except Exception as e:
            print(f"❌ Erro calculando sats: {e}")
            # Fallback para valor mínimo
            return 1000

    def enviar_btc_lightning_real(self):
        """Envia BTC real para o Lightning Address usando Voltz"""
        try:
            print("\n🚀 Enviando BTC real via Lightning Address (Voltz)...")
            
            # 1. Calcula valor em sats baseado na cotação atual
            valor_sats = self.calcular_sats_equivalente(self.valor_compra)
            print(f"🔢 Valor calculado para envio: {valor_sats:,} sats")
            
            # 2. Resolver Lightning Address para invoice BOLT11
            resolver = LightningAddressResolver()
            result = resolver.resolve_to_bolt11(self.lightning_address, valor_sats)
            if not result['success']:
                print(f"❌ Erro ao resolver Lightning Address: {result['error']}")
                return False
            bolt11 = result['bolt11']
            print(f"✅ Invoice BOLT11 obtido: {bolt11[:60]}...")
            
            # 3. Chamar backend Voltz para pagar a invoice
            payload = {
                'action': 'pay_invoice',
                'depix_id': self.depix_id,
                'client_invoice': bolt11
            }
            response = requests.post(f"{self.backend_url}/voltz/voltz_rest.php", json=payload, timeout=30)
            print(f"[DEBUG] Resposta Voltz pay_invoice: HTTP {response.status_code} - {response.text}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"🎉 Pagamento Lightning enviado com sucesso! Hash: {data.get('payment_hash')}")
                    return True
                else:
                    print(f"❌ Erro Voltz: {data.get('error', data)}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Erro no envio Lightning real: {e}")
        return False

    def executar_teste_completo(self):
        """Executa o teste completo do fluxo de compra"""
        
        print("🚀 INICIANDO TESTE COMPLETO DO FLUXO DE COMPRA")
        print("=" * 70)
        print(f"💰 Valor da compra: R$ {self.valor_compra}")
        print(f"⚡ Rede: Lightning")
        print(f"📱 Chat ID: {self.chat_id}")
        print(f"🌐 Backend: {self.backend_url}")
        print(f"🔢 Valor Lightning: calculado via API real (Binance/CoinGecko)")
        print(f"🏦 APIs integradas: {self.api_cotacao.__class__.__name__}")
        print(f"📊 Limites: R$ {self.limites.PIX_COMPRA_MIN} - R$ {self.limites.PIX_COMPRA_MAX}")
        print(f"⚙️ Sistema de comissões: ativado")
        print("=" * 70)
        
        # PASSO 1: Iniciar conversa com bot
        self.log_passo(1, "Iniciando conversa com o bot")
        if not self.enviar_mensagem_bot("/start"):
            print("❌ FALHA: Não foi possível iniciar conversa")
            return False
        
        # PASSO 2: Acessar menu de compra
        self.log_passo(2, "Acessando menu de compra")
        if not self.enviar_mensagem_bot("🛒 Comprar"):
            print("❌ FALHA: Não foi possível acessar menu")
            return False
        
        # PASSO 3: Criar pedido no backend
        self.log_passo(3, "Criando pedido no backend")
        if not self.criar_pedido_backend():
            print("❌ FALHA: Não foi possível criar pedido")
            return False
        
        # PASSO 4: Simular pagamento PIX
        self.log_passo(4, "Simulando confirmação de pagamento PIX")
        if not self.simular_pagamento_pix():
            print("❌ FALHA: Não foi possível simular pagamento")
            return False
        
        # PASSO 5: Aguardar detecção do bot
        self.log_passo(5, "Aguardando bot detectar pedido pago")
        print("⏳ Aguardando 15 segundos para o bot processar...")
        time.sleep(15)
        
        # PASSO 6: Verificar se bot detectou pedido
        self.log_passo(6, "Verificando se bot detectou pedido pendente")
        if not self.verificar_pedido_pendente():
            print("⚠️ AVISO: Pedido pode não ter sido detectado ainda")
        
        # PASSO 7: Simular comando para verificar status
        self.log_passo(7, "Verificando status no bot")
        self.enviar_mensagem_bot("Status", 5)
        
        # PASSO 8: Simular Lightning (para forçar detecção)
        self.log_passo(8, "Forçando detecção Lightning")
        self.enviar_mensagem_bot("Lightning", 8)
        
        # PASSO 9: Verificar logs do bot
        self.log_passo(9, "Verificando logs do bot")
        self.verificar_logs_bot()
        
        # PASSO 10: Simular fornecimento de Lightning Address
        self.log_passo(10, "Fornecendo Lightning Address")
        if not self.simular_envio_lightning_address():
            print("❌ FALHA: Não foi possível enviar Lightning Address")
            return False

        # NOVO: PASSO 10.1 - Simular webhook Depix (confirmação PIX realista)
        self.log_passo("10.1", "Simulando webhook Depix (confirmação PIX)")
        try:
            webhook_payload = {
                "id": self.depix_id,
                "status": "paid",
                "payment_method": "pix",
                "amount": int(float(self.valor_compra) * 100),
                "currency": "BRL",
                "paid_at": datetime.now().isoformat(),
                "customer": {"id": self.chat_id},
                "metadata": {"chat_id": self.chat_id, "lightning_address": self.lightning_address}
            }
            response = requests.post(
                f"{self.backend_url}/square_webhook.php",
                json=webhook_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                print("✅ Webhook Depix simulado com sucesso!")
            else:
                print(f"⚠️ Webhook Depix retornou HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Erro simulando webhook Depix: {e}")

        # NOVO: PASSO 10.1.2 - Envio real de BTC via Lightning Address (Voltz)
        self.log_passo("10.1.2", "Enviando BTC real via Lightning Address (Voltz)")
        if not self.enviar_btc_lightning_real():
            print("⚠️ AVISO: Envio Lightning real falhou (pode ser temporário)")
            print("📋 Continuando teste para verificar outras funcionalidades...")

        # NOVO: PASSO 10.2 - Simular envio de blockchainTxID (BTC enviado)
        self.log_passo("10.2", "Simulando envio de blockchainTxID (BTC enviado)")
        try:
            import hashlib
            txid = hashlib.sha256(f"{self.pedido_id}_{time.time()}".encode()).hexdigest()
            payload = {
                "id": self.depix_id,
                "blockchainTxID": txid
            }
            print(f"[DEBUG] Payload webhook blockchainTxID: {json.dumps(payload, indent=2)}")
            # Token de autorização do webhook Depix (ajuste conforme necessário)
            depix_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {depix_token}"
            }
            response = requests.post(
                f"{self.backend_url}/depix/webhook.php",
                json=payload,
                headers=headers,
                timeout=30  # Aumenta timeout para 30 segundos
            )
            print(f"[DEBUG] Resposta webhook blockchainTxID: HTTP {response.status_code} - {response.text}")
            if response.status_code == 200:
                print(f"✅ blockchainTxID simulado: {txid}")
            else:
                print(f"⚠️ Webhook blockchainTxID retornou HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Erro simulando envio de blockchainTxID: {e}")

        # PASSO 11: Aguardar processamento final
        self.log_passo(11, "Aguardando processamento final")
        print("⏳ Aguardando 20 segundos para processamento completo...")
        time.sleep(20)
        
        # PASSO 12: Verificar finalização
        self.log_passo(12, "Verificando finalização do pedido")
        sucesso_final = self.verificar_finalizacao()
        
        # RESUMO FINAL
        print("\n" + "=" * 70)
        print("🎯 RESUMO DO TESTE COMPLETO")
        print("=" * 70)
        
        tempo_total = datetime.now() - self.teste_iniciado
        print(f"⏱️ Tempo total: {tempo_total.total_seconds():.1f}s")
        print(f"📋 Pedido ID: {self.pedido_id}")
        print(f"💰 Valor: R$ {self.valor_compra}")
        print(f"⚡ Lightning Address: {self.lightning_address}")
        
        if sucesso_final:
            print("🎉 TESTE COMPLETO: SUCESSO!")
            print("✅ Fluxo completo funcionando corretamente")
        else:
            print("⚠️ TESTE PARCIAL: Algumas etapas podem precisar de verificação manual")
            print("📱 Verifique o chat do Telegram para detalhes")
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Verificar chat do Telegram para confirmação")
        print("2. Verificar interface web (transacoes.php)")
        print("3. Verificar logs completos se necessário")
        print("=" * 70)
        
        return sucesso_final

if __name__ == "__main__":
    teste = TesteFluxoCompleto()
    teste.executar_teste_completo()
