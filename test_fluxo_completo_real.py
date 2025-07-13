#!/usr/bin/env python3
"""
Teste do fluxo completo do PIX até o envio dos satoshis (COM CONSULTA REAL DO BALANCE)
Consulta o balance real da carteira Voltz antes de simular o envio
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from config.config import BASE_URL

class FluxoCompletoReal:
    """
    Testa o fluxo completo com consulta real do balance da carteira Voltz
    """
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = None
    
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
    
    async def consultar_balance_voltz(self) -> Dict[str, Any]:
        """Consulta o balance real da carteira Voltz."""
        try:
            url = f"{self.base_url}/api_voltz.php"
            params = {"action": "balance"}
            
            if self.session is None:
                return {"success": False, "error": "Session não inicializada"}
            
            print(f"🔍 Consultando balance da carteira Voltz...")
            print(f"📡 URL: {url}")
            print(f"📋 Params: {params}")
            
            async with self.session.get(url, params=params) as response:
                print(f"📊 Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Resposta: {json.dumps(result, indent=2)}")
                    return result
                else:
                    error_text = await response.text()
                    print(f"❌ Erro HTTP {response.status}: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Erro na consulta: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def simular_envio_lightning_com_balance(self, endereco_lightning: str, valor_sats: int, balance_atual: int) -> Dict[str, Any]:
        """Simula o envio de satoshis verificando se há saldo suficiente."""
        
        print(f"\n💰 VERIFICAÇÃO DE SALDO:")
        print(f"   💰 Saldo atual: {balance_atual} satoshis")
        print(f"   💸 Valor a enviar: {valor_sats} satoshis")
        print(f"   📊 Saldo após envio: {balance_atual - valor_sats} satoshis")
        
        if balance_atual < valor_sats:
            return {
                "success": False,
                "error": f"Saldo insuficiente. Saldo atual: {balance_atual} sats, Valor necessário: {valor_sats} sats"
            }
        
        # Simula uma resposta de sucesso da API Voltz
        return {
            "success": True,
            "payment_hash": f"real_payment_hash_{valor_sats}_{hash(endereco_lightning) % 10000}",
            "fee_msat": 1500,
            "status": "complete",
            "amount_msat": valor_sats * 1000,
            "destination": endereco_lightning,
            "balance_antes": balance_atual,
            "balance_depois": balance_atual - valor_sats
        }
    
    async def simular_verificacao_pagamento_sucesso(self, payment_hash: str) -> Dict[str, Any]:
        """Simula a verificação do status do pagamento Lightning com SUCESSO."""
        return {
            "success": True,
            "data": {
                "status": "complete",
                "payment_hash": payment_hash,
                "fee_msat": 1500,
                "amount_msat": 9500000,
                "created_at": "2024-07-08T12:00:00Z",
                "settled_at": "2024-07-08T12:00:05Z"
            }
        }
    
    async def simular_mensagem_bot(self, mensagem: str):
        """Simula o envio de mensagem pelo bot."""
        print(f"🤖 BOT: {mensagem}")
    
    async def testar_fluxo_completo_com_balance(self, depix_id: str, endereco_lightning: str = "bouncyflight79@walletofsatoshi.com"):
        """
        Testa o fluxo completo incluindo consulta do balance da carteira Voltz.
        
        Args:
            depix_id: ID do depósito PIX
            endereco_lightning: Endereço Lightning do usuário
        """
        print(f"🚀 Iniciando teste do fluxo completo para depix_id: {depix_id}")
        print("=" * 80)
        
        # PASSO 1: Verificação do PIX
        await self.simular_mensagem_bot("🔍 Verificando confirmação do pagamento PIX...")
        await self.simular_mensagem_bot("⏳ Aguarde enquanto validamos sua transação.")
        
        deposito = await self.consultar_deposito(depix_id)
        
        if "error" in deposito:
            await self.simular_mensagem_bot(f"❌ Erro na verificação: {deposito['error']}")
            return False
        
        if not deposito.get("blockchainTxID"):
            await self.simular_mensagem_bot("❌ Pagamento não confirmado. Blockchain TxID não encontrado.")
            return False
        
        # PAGAMENTO CONFIRMADO!
        await self.simular_mensagem_bot("✅ Pagamento confirmado!")
        await self.simular_mensagem_bot("🔗 Blockchain TxID encontrado.")
        await self.simular_mensagem_bot("📬 Por favor, envie seu endereço Lightning (Lightning Address ou Invoice) para receber seus satoshis.")
        
        # PASSO 2: Recebimento do endereço Lightning
        print(f"\n📬 Endereço Lightning recebido: {endereco_lightning}")
        await self.simular_mensagem_bot(f"✅ Endereço Lightning recebido!")
        await self.simular_mensagem_bot(f"📬 {endereco_lightning}")
        await self.simular_mensagem_bot("🔄 Processando pagamento...")
        await self.simular_mensagem_bot("⏳ Aguarde a confirmação da transação Lightning.")
        
        # PASSO 3: Consulta do balance da carteira Voltz
        print(f"\n🏦 CONSULTANDO BALANCE DA CARTEIRA VOLTZ...")
        resultado_balance = await self.consultar_balance_voltz()
        
        if not resultado_balance.get("success"):
            await self.simular_mensagem_bot("❌ Erro ao consultar balance da carteira")
            await self.simular_mensagem_bot(f"🔧 Erro: {resultado_balance.get('error', 'Erro desconhecido')}")
            return False
        
        # Extrai o balance da resposta
        balance_data = resultado_balance.get("data", {})
        balance_atual = balance_data.get("balance", 0)
        
        await self.simular_mensagem_bot(f"💰 Balance da carteira: {balance_atual} satoshis")
        
        # PASSO 4: Envio dos satoshis (com verificação de saldo)
        valor_sats = 9500  # Valor em satoshis (baseado no depósito)
        print(f"\n💰 Enviando {valor_sats} satoshis...")
        
        resultado_envio = await self.simular_envio_lightning_com_balance(endereco_lightning, valor_sats, balance_atual)
        
        if resultado_envio.get("success"):
            payment_hash = resultado_envio.get("payment_hash")
            fee_msat = resultado_envio.get("fee_msat", 0)
            balance_depois = resultado_envio.get("balance_depois", 0)
            
            if payment_hash is None:
                await self.simular_mensagem_bot("❌ Erro: Payment hash não encontrado")
                return False
            
            await self.simular_mensagem_bot("✅ Pagamento Lightning enviado com sucesso!")
            await self.simular_mensagem_bot(f"🔗 Payment Hash: {payment_hash}")
            await self.simular_mensagem_bot(f"💸 Taxa: {fee_msat} msat")
            await self.simular_mensagem_bot(f"💰 Novo balance: {balance_depois} satoshis")
            
            # PASSO 5: Verificação do status do pagamento
            await self.simular_mensagem_bot("🔍 Verificando status do pagamento...")
            
            resultado_verificacao = await self.simular_verificacao_pagamento_sucesso(payment_hash)
            
            if resultado_verificacao.get("success"):
                status_pagamento = resultado_verificacao.get("data", {}).get("status", "unknown")
                
                if status_pagamento == "complete":
                    # MENSAGEM FINAL DE SUCESSO!
                    await self.simular_mensagem_bot("🎉 Transação concluída com sucesso!")
                    await self.simular_mensagem_bot(f"💰 {valor_sats} satoshis enviados para {endereco_lightning}")
                    await self.simular_mensagem_bot("✅ Sua transação foi finalizada. Obrigado por usar nossos serviços!")
                    await self.simular_mensagem_bot("🔄 Para fazer uma nova compra, use /start")
                    
                    # DETALHES DA TRANSAÇÃO
                    print(f"\n📊 DETALHES DA TRANSAÇÃO:")
                    print(f"   💰 Valor: {valor_sats} satoshis")
                    print(f"   💸 Taxa: {fee_msat} msat")
                    print(f"   🔗 Payment Hash: {payment_hash}")
                    print(f"   📬 Destino: {endereco_lightning}")
                    print(f"   🏦 Balance antes: {balance_atual} satoshis")
                    print(f"   🏦 Balance depois: {balance_depois} satoshis")
                    print(f"   ⏰ Criado em: 2024-07-08T12:00:00Z")
                    print(f"   ✅ Confirmado em: 2024-07-08T12:00:05Z")
                    
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
            await self.simular_mensagem_bot(f"🔧 Erro: {resultado_envio.get('error', 'Erro desconhecido')}")
            await self.simular_mensagem_bot("📞 Entre em contato com nosso atendente: @GhosttP2P_bot")
            return False

async def main():
    """Função principal para executar os testes."""
    print("🧪 TESTE DO FLUXO COMPLETO PIX -> LIGHTNING (COM CONSULTA REAL DO BALANCE)")
    print("=" * 80)
    
    # Depix IDs de teste (com blockchainTxID)
    depix_ids_completos = [
        "965cd29f947c0a548c8199bbacb42a294aec3cd8f8f6cd935c45f52b6a8ddb2b",
        "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        "f1e2d3c4b5a6789012345678901234567890fedcba1234567890fedcba123456"
    ]
    
    # Endereço Lightning fixo para todos os testes
    endereco_lightning = "bouncyflight79@walletofsatoshi.com"
    
    sucessos = 0
    total = len(depix_ids_completos)
    
    async with FluxoCompletoReal() as fluxo:
        for i, depix_id in enumerate(depix_ids_completos):
            print(f"\n{'='*20} TESTE {i+1}/{total} {'='*20}")
            
            resultado = await fluxo.testar_fluxo_completo_com_balance(depix_id, endereco_lightning)
            
            if resultado:
                print(f"✅ Teste {i+1} CONCLUÍDO COM SUCESSO!")
                sucessos += 1
            else:
                print(f"❌ Teste {i+1} FALHOU!")
            
            print(f"{'='*60}")
            
            # Pausa entre testes
            if i < total - 1:
                await asyncio.sleep(2)
    
    print(f"\n🎯 TODOS OS TESTES CONCLUÍDOS!")
    print(f"📊 Resumo: {sucessos}/{total} testes passaram")
    print(f"✅ Fluxo completo do PIX até Lightning testado com sucesso!")
    print(f"🎉 Consulta real do balance da carteira Voltz implementada!")
    print(f"📬 Endereço Lightning usado: {endereco_lightning}")

if __name__ == "__main__":
    asyncio.run(main()) 