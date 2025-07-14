#!/usr/bin/env python3
"""
TESTE REAL - Envio de satoshis para carteira Lightning
Usa os depix_ids reais fornecidos e envia valores baixos para teste
COM CREDENCIAIS REAIS DA API VOLTZ
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from config.config import BASE_URL

class TesteRealEnvioSats:
    """
    Teste real de envio de satoshis via Lightning Network
    """
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = None
        
        # Credenciais da API Voltz (do arquivo voltz/config.php)
        self.voltz_config = {
            'node_url': 'https://lnvoltz.com',
            'wallet_id': 'f3c366b7fb6f43fa9467c4dccedaf824',
            'admin_key': '8fce34f4b0f8446a990418bd167dc644',
            'invoice_key': 'b2f68df91c8848f6a1db26f2e403321f',
            'api_version': 'v1'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def consultar_deposito(self, depix_id: str) -> Dict[str, Any]:
        """Consulta os dados do depósito no backend."""
        try:
            url = f"{self.base_url}/deposit.php"
            params = {"action": "get", "depix_id": depix_id}
            
            if self.session is None:
                return {"success": False, "error": "Session não inicializada"}
                
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def consultar_balance_voltz_direto(self) -> Dict[str, Any]:
        """Consulta o balance diretamente na API Voltz usando as credenciais."""
        try:
            # URL direta da API Voltz (estrutura correta baseada no VoltzClient.php)
            url = f"{self.voltz_config['node_url']}/api/{self.voltz_config['api_version']}/wallet"
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Api-Key': self.voltz_config['admin_key']
            }
            
            if self.session is None:
                return {"success": False, "error": "Session não inicializada"}
            
            print(f"🔍 Consultando balance diretamente na API Voltz...")
            print(f"📡 URL: {url}")
            print(f"🔑 Usando admin_key: {self.voltz_config['admin_key'][:8]}...")
            
            async with self.session.get(url, headers=headers) as response:
                print(f"📊 Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Balance consultado com sucesso: {json.dumps(result, indent=2)}")
                    return {"success": True, "data": result}
                else:
                    error_text = await response.text()
                    print(f"❌ Erro HTTP {response.status}: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Erro na consulta: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def lightning_address_para_invoice(self, lightning_address: str, valor_sats: int) -> Optional[str]:
        """Resolve um Lightning Address para uma invoice BOLT11 usando LNURL."""
        try:
            if '@' not in lightning_address:
                raise ValueError('Endereço Lightning inválido')
            usuario, dominio = lightning_address.split('@', 1)
            url_lnurl = f"https://{dominio}/.well-known/lnurlp/{usuario}"
            async with self.session.get(url_lnurl) as resp:
                if resp.status != 200:
                    raise Exception(f"Erro ao consultar LNURL: {resp.status}")
                lnurl_data = await resp.json()
                assert lnurl_data is not None
                assert isinstance(lnurl_data, dict)
                lnurl_data = dict(lnurl_data)  # Cast explícito para o Pyright
                callback = lnurl_data.get('callback')
                if not callback:
                    raise Exception('Callback LNURL não encontrado')
                # Valor em msats
                amount_msat = valor_sats * 1000
                url_invoice = f"{callback}?amount={amount_msat}"
                async with self.session.get(url_invoice) as resp2:
                    if resp2.status != 200:
                        raise Exception(f"Erro ao solicitar invoice: {resp2.status}")
                    invoice_data = await resp2.json()
                    assert invoice_data is not None
                    assert isinstance(invoice_data, dict)
                    invoice_data = dict(invoice_data)  # Cast explícito para o Pyright
                    pr = invoice_data.get('pr')
                    if not pr:
                        raise Exception('Invoice não encontrada na resposta LNURL')
                    return pr
        except Exception as e:
            print(f"❌ Erro ao resolver Lightning Address: {str(e)}")
            return None

    async def enviar_pagamento_lightning_direto(self, endereco_lightning: str, valor_sats: int) -> Dict[str, Any]:
        """Envia pagamento Lightning diretamente na API Voltz usando as credenciais."""
        try:
            # Se não for BOLT11, resolver Lightning Address para invoice
            if not endereco_lightning.startswith('lnbc'):
                print(f"🔄 Resolvendo Lightning Address '{endereco_lightning}' para invoice BOLT11...")
                invoice_bolt11 = await self.lightning_address_para_invoice(endereco_lightning, valor_sats)
                if not invoice_bolt11:
                    return {"success": False, "error": "Não foi possível resolver Lightning Address para invoice BOLT11"}
                endereco_lightning = invoice_bolt11
                print(f"✅ Invoice BOLT11 obtida: {endereco_lightning[:40]}...")
            # URL direta da API Voltz para pagamento (estrutura correta)
            url = f"{self.voltz_config['node_url']}/api/{self.voltz_config['api_version']}/payments"
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Api-Key': self.voltz_config['admin_key']
            }
            data = {
                "out": "true",
                "bolt11": endereco_lightning,
                "unit": "sat"
            }
            if self.session is None:
                return {"success": False, "error": "Session não inicializada"}
            print(f"💰 Enviando {valor_sats} satoshis para {endereco_lightning[:40]}...")
            print(f"📡 URL: {url}")
            print(f"🔑 Usando admin_key: {self.voltz_config['admin_key'][:8]}...")
            print(f"📋 Dados: {json.dumps(data, indent=2)}")
            async with self.session.post(url, json=data, headers=headers) as response:
                print(f"📊 Status: {response.status}")
                if response.status in (200, 201):
                    result = await response.json()
                    print(f"✅ Pagamento enviado com sucesso: {json.dumps(result, indent=2)}")
                    return {"success": True, "data": result}
                else:
                    error_text = await response.text()
                    print(f"❌ Erro HTTP {response.status}: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Erro no envio: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def verificar_status_pagamento_direto(self, payment_hash: str) -> Dict[str, Any]:
        """Verifica o status do pagamento diretamente na API Voltz."""
        try:
            # URL direta da API Voltz (estrutura correta)
            url = f"{self.voltz_config['node_url']}/api/{self.voltz_config['api_version']}/payments/{payment_hash}"
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Api-Key': self.voltz_config['admin_key']
            }
            
            if self.session is None:
                return {"success": False, "error": "Session não inicializada"}
            
            print(f"🔍 Verificando status do pagamento {payment_hash}...")
            
            async with self.session.get(url, headers=headers) as response:
                print(f"📊 Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Status verificado: {json.dumps(result, indent=2)}")
                    return {"success": True, "data": result}
                else:
                    error_text = await response.text()
                    print(f"❌ Erro HTTP {response.status}: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Erro na verificação: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def simular_mensagem_bot(self, mensagem: str):
        """Simula o envio de mensagem pelo bot."""
        print(f"🤖 BOT: {mensagem}")
    
    async def testar_envio_real(self, depix_id: str, endereco_lightning: str = "bouncyflight79@walletofsatoshi.com", valor_sats: int = 100):
        """
        Teste REAL de envio de satoshis usando credenciais da API Voltz.
        
        Args:
            depix_id: ID do depósito PIX real
            endereco_lightning: Endereço Lightning real
            valor_sats: Valor em satoshis (baixo para teste)
        """
        print(f"🚀 TESTE REAL - Enviando {valor_sats} satoshis para {endereco_lightning}")
        print("=" * 80)
        
        # PASSO 1: Verificação do PIX real
        await self.simular_mensagem_bot("🔍 Verificando confirmação do pagamento PIX...")
        
        deposito = await self.consultar_deposito(depix_id)
        
        if "error" in deposito:
            await self.simular_mensagem_bot(f"❌ Erro na verificação: {deposito['error']}")
            return False
        
        if not deposito.get("blockchainTxID"):
            await self.simular_mensagem_bot("❌ Pagamento não confirmado. Blockchain TxID não encontrado.")
            return False
        
        # PAGAMENTO CONFIRMADO!
        blockchain_txid = deposito.get("blockchainTxID")
        await self.simular_mensagem_bot("✅ Pagamento confirmado!")
        await self.simular_mensagem_bot(f"🔗 Blockchain TxID: {blockchain_txid}")
        await self.simular_mensagem_bot(f"📬 Endereço Lightning: {endereco_lightning}")
        
        # PASSO 2: Consulta do balance real da carteira Voltz
        print(f"\n🏦 CONSULTANDO BALANCE REAL DA CARTEIRA VOLTZ...")
        resultado_balance = await self.consultar_balance_voltz_direto()
        
        if resultado_balance.get("success"):
            balance_data = resultado_balance.get("data", {})
            balance_atual = balance_data.get("balance", 0)
            await self.simular_mensagem_bot(f"💰 Balance da carteira: {balance_atual} satoshis")
            
            if balance_atual < valor_sats:
                await self.simular_mensagem_bot(f"❌ Saldo insuficiente. Saldo: {balance_atual} sats, Necessário: {valor_sats} sats")
                return False
        else:
            await self.simular_mensagem_bot("⚠️ Não foi possível consultar o balance")
            await self.simular_mensagem_bot("🔄 Continuando com o envio...")
        
        # PASSO 3: ENVIO REAL dos satoshis via API Voltz
        print(f"\n💰 ENVIANDO {valor_sats} SATOSHIS REAIS VIA API VOLTZ...")
        await self.simular_mensagem_bot(f"🔄 Enviando {valor_sats} satoshis para {endereco_lightning}...")
        
        resultado_envio = await self.enviar_pagamento_lightning_direto(endereco_lightning, valor_sats)
        
        if resultado_envio.get("success"):
            payment_data = resultado_envio.get("data", {})
            payment_hash = payment_data.get("payment_hash")
            fee_msat = payment_data.get("fee_msat", 0)
            
            if payment_hash is None:
                await self.simular_mensagem_bot("❌ Erro: Payment hash não encontrado")
                return False
            
            await self.simular_mensagem_bot("✅ Pagamento Lightning enviado com sucesso!")
            await self.simular_mensagem_bot(f"🔗 Payment Hash: {payment_hash}")
            await self.simular_mensagem_bot(f"💸 Taxa: {fee_msat} msat")
            
            # PASSO 4: Verificação do status do pagamento
            await self.simular_mensagem_bot("🔍 Verificando status do pagamento...")
            
            resultado_verificacao = await self.verificar_status_pagamento_direto(payment_hash)
            
            if resultado_verificacao.get("success"):
                payment_status = resultado_verificacao.get("data", {})
                status_pagamento = payment_status.get("status", "unknown")
                
                if status_pagamento == "complete":
                    # SUCESSO REAL!
                    await self.simular_mensagem_bot("🎉 TRANSAÇÃO REAL CONCLUÍDA COM SUCESSO!")
                    await self.simular_mensagem_bot(f"💰 {valor_sats} satoshis enviados para {endereco_lightning}")
                    await self.simular_mensagem_bot("✅ Verifique sua carteira Wallet of Satoshi!")
                    await self.simular_mensagem_bot("🔄 Para fazer uma nova compra, use /start")
                    
                    # DETALHES DA TRANSAÇÃO REAL
                    print(f"\n📊 DETALHES DA TRANSAÇÃO REAL:")
                    print(f"   💰 Valor: {valor_sats} satoshis")
                    print(f"   💸 Taxa: {fee_msat} msat")
                    print(f"   🔗 Payment Hash: {payment_hash}")
                    print(f"   📬 Destino: {endereco_lightning}")
                    print(f"   🔗 Blockchain TxID: {blockchain_txid}")
                    print(f"   ✅ Status: {status_pagamento}")
                    
                    return True
                else:
                    await self.simular_mensagem_bot(f"⚠️ Status do pagamento: {status_pagamento}")
                    await self.simular_mensagem_bot("🔄 Aguardando confirmação da rede Lightning...")
                    return False
            else:
                await self.simular_mensagem_bot("❌ Erro ao verificar status do pagamento")
                await self.simular_mensagem_bot("🔧 Entre em contato com o atendente se o problema persistir")
                return False
        else:
            await self.simular_mensagem_bot("❌ Erro ao enviar pagamento Lightning")
            # Exibe o JSON completo da resposta de erro para debug detalhado
            print("[DEBUG] Resposta completa do backend:")
            print(json.dumps(resultado_envio, indent=2, ensure_ascii=False))
            await self.simular_mensagem_bot(f"🔧 Erro: {resultado_envio.get('error', 'Erro desconhecido')}")
            await self.simular_mensagem_bot("📞 Entre em contato com nosso atendente: @GhosttP2P_bot")
            return False

async def main():
    """Função principal para executar os testes reais."""
    print("🧪 TESTE REAL - ENVIO DE SATOSHIS PARA CARTEIRA LIGHTNING")
    print("🔑 USANDO CREDENCIAIS REAIS DA API VOLTZ")
    print("=" * 80)
    
    # Depix IDs REAIS fornecidos pelo usuário (com blockchainTxID)
    depix_ids_reais = [
        "965cd29f947c0a548c8199bbacb42a294aec3cd8f8f6cd935c45f52b6a8ddb2b",
        "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        "f1e2d3c4b5a6789012345678901234567890fedcba1234567890fedcba123456"
    ]
    
    # Endereço Lightning REAL
    endereco_lightning_real = "bouncyflight79@walletofsatoshi.com"
    
    # Valores baixos para teste (em satoshis)
    valores_teste = [50, 100, 150]  # Valores bem baixos
    
    sucessos = 0
    total = len(depix_ids_reais)
    
    async with TesteRealEnvioSats() as teste:
        for i, depix_id in enumerate(depix_ids_reais):
            print(f"\n{'='*20} TESTE REAL {i+1}/{total} {'='*20}")
            
            valor_sats = valores_teste[i % len(valores_teste)]
            resultado = await teste.testar_envio_real(depix_id, endereco_lightning_real, valor_sats)
            
            if resultado:
                print(f"✅ Teste Real {i+1} CONCLUÍDO COM SUCESSO!")
                print(f"💰 {valor_sats} satoshis enviados para sua carteira!")
                sucessos += 1
            else:
                print(f"❌ Teste Real {i+1} FALHOU!")
            
            print(f"{'='*60}")
            
            # Pausa entre testes
            if i < total - 1:
                await asyncio.sleep(3)
    
    print(f"\n🎯 TODOS OS TESTES REAIS CONCLUÍDOS!")
    print(f"📊 Resumo: {sucessos}/{total} testes passaram")
    if sucessos > 0:
        print(f"🎉 SATOSHIS REAIS ENVIADOS PARA SUA CARTEIRA!")
        print(f"📱 Verifique sua carteira Wallet of Satoshi!")
    else:
        print(f"❌ Nenhum satoshi foi enviado (verifique os logs acima)")
    print(f"📬 Endereço Lightning usado: {endereco_lightning_real}")

if __name__ == "__main__":
    asyncio.run(main()) 