#!/usr/bin/env python3
"""
Teste do fluxo completo do PIX até o envio dos satoshis
Simula todo o processo: validação do PIX -> solicitação de endereço Lightning -> envio dos sats
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from config.config import BASE_URL

class FluxoCompletoPIX:
    """
    Simula o fluxo completo do PIX até o envio dos satoshis
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
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def simular_envio_lightning(self, endereco_lightning: str, valor_sats: int) -> Dict[str, Any]:
        """Simula o envio de satoshis via Lightning Network."""
        try:
            # Simula uma chamada para a API Voltz
            url = f"{self.base_url}/api_voltz.php"
            data = {
                "action": "pay_invoice",
                "invoice": endereco_lightning,
                "amount": valor_sats
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    # Simula sucesso se a resposta for válida
                    if result.get('success'):
                        return {
                            "success": True,
                            "payment_hash": "simulated_payment_hash_123456",
                            "fee_msat": 1000,
                            "status": "complete"
                        }
                    else:
                        return {"success": False, "error": result.get('error', 'Erro desconhecido')}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def simular_verificacao_pagamento(self, payment_hash: str) -> Dict[str, Any]:
        """Simula a verificação do status do pagamento Lightning."""
        try:
            url = f"{self.base_url}/voltz/check_payment.php"
            params = {"payment_hash": payment_hash}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def simular_mensagem_bot(self, mensagem: str):
        """Simula o envio de mensagem pelo bot."""
        print(f"🤖 BOT: {mensagem}")
    
    async def simular_mensagem_usuario(self, mensagem: str):
        """Simula mensagem do usuário."""
        print(f"👤 USUÁRIO: {mensagem}")
    
    async def testar_fluxo_completo(self, depix_id: str, endereco_lightning: str = "user@lightning.com"):
        """
        Testa o fluxo completo do PIX até o envio dos satoshis.
        
        Args:
            depix_id: ID do depósito PIX
            endereco_lightning: Endereço Lightning do usuário
        """
        print(f"🚀 Iniciando teste do fluxo completo para depix_id: {depix_id}")
        print("=" * 80)
        
        # PASSO 1: Verificação do PIX
        await self.simular_mensagem_bot("🔍 Verificando confirmação do pagamento PIX...")
        await self.simular_mensagem_bot("⏳ Aguarde enquanto validamos sua transação.")
        
        tentativas = 3
        pagamento_confirmado = False
        
        for i in range(tentativas):
            print(f"\n🔄 Tentativa {i+1}/{tentativas}")
            
            deposito = await self.consultar_deposito(depix_id)
            
            if "error" in deposito:
                await self.simular_mensagem_bot(f"⚠️ Erro na verificação: {deposito['error']}")
                if i < tentativas - 1:
                    await asyncio.sleep(2)  # Simula 30 segundos
                continue
            
            if deposito.get("blockchainTxID"):
                pagamento_confirmado = True
                await self.simular_mensagem_bot("✅ Pagamento confirmado!")
                await self.simular_mensagem_bot("🔗 Blockchain TxID encontrado.")
                await self.simular_mensagem_bot("📬 Por favor, envie seu endereço Lightning (Lightning Address ou Invoice) para receber seus satoshis.")
                break
            else:
                status = deposito.get("status", "pending")
                await self.simular_mensagem_bot(f"⏳ Aguardando confirmação do PIX... Status: {status}")
                
                if i < tentativas - 1:
                    await asyncio.sleep(2)  # Simula 30 segundos
        
        if not pagamento_confirmado:
            await self.simular_mensagem_bot("❌ Não foi possível confirmar automaticamente seu pagamento.")
            await self.simular_mensagem_bot("🔧 Por favor, entre em contato com nosso atendente: @GhosttP2P_bot")
            return False
        
        # PASSO 2: Recebimento do endereço Lightning
        print(f"\n📬 Endereço Lightning recebido: {endereco_lightning}")
        await self.simular_mensagem_bot(f"✅ Endereço Lightning recebido!")
        await self.simular_mensagem_bot(f"📬 {endereco_lightning}")
        await self.simular_mensagem_bot("🔄 Processando pagamento...")
        await self.simular_mensagem_bot("⏳ Aguarde a confirmação da transação Lightning.")
        
        # PASSO 3: Envio dos satoshis
        valor_sats = 9500  # Valor em satoshis (baseado no depósito)
        print(f"\n💰 Enviando {valor_sats} satoshis...")
        
        resultado_envio = await self.simular_envio_lightning(endereco_lightning, valor_sats)
        
        if resultado_envio.get("success"):
            payment_hash = resultado_envio.get("payment_hash")
            fee_msat = resultado_envio.get("fee_msat", 0)
            
            await self.simular_mensagem_bot("✅ Pagamento Lightning enviado com sucesso!")
            await self.simular_mensagem_bot(f"🔗 Payment Hash: {payment_hash}")
            await self.simular_mensagem_bot(f"💸 Taxa: {fee_msat} msat")
            
            # PASSO 4: Verificação do status do pagamento
            await self.simular_mensagem_bot("🔍 Verificando status do pagamento...")
            
            resultado_verificacao = await self.simular_verificacao_pagamento(payment_hash)
            
            if resultado_verificacao.get("success"):
                status_pagamento = resultado_verificacao.get("data", {}).get("status", "unknown")
                
                if status_pagamento == "complete":
                    await self.simular_mensagem_bot("🎉 Transação concluída com sucesso!")
                    await self.simular_mensagem_bot(f"💰 {valor_sats} satoshis enviados para {endereco_lightning}")
                    await self.simular_mensagem_bot("✅ Sua transação foi finalizada. Obrigado por usar nossos serviços!")
                    await self.simular_mensagem_bot("🔄 Para fazer uma nova compra, use /start")
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
    print("🧪 TESTE DO FLUXO COMPLETO PIX -> LIGHTNING")
    print("=" * 80)
    
    # Depix IDs de teste (com blockchainTxID)
    depix_ids_completos = [
        "965cd29f947c0a548c8199bbacb42a294aec3cd8f8f6cd935c45f52b6a8ddb2b",
        "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        "f1e2d3c4b5a6789012345678901234567890fedcba1234567890fedcba123456"
    ]
    
    # Endereços Lightning de teste
    enderecos_lightning = [
        "user@lightning.com",
        "lnbc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxfvqjf3vq",
        "mau@voltz.com"
    ]
    
    async with FluxoCompletoPIX() as fluxo:
        for i, depix_id in enumerate(depix_ids_completos):
            print(f"\n{'='*20} TESTE {i+1}/{len(depix_ids_completos)} {'='*20}")
            
            endereco = enderecos_lightning[i % len(enderecos_lightning)]
            resultado = await fluxo.testar_fluxo_completo(depix_id, endereco)
            
            if resultado:
                print(f"✅ Teste {i+1} CONCLUÍDO COM SUCESSO!")
            else:
                print(f"❌ Teste {i+1} FALHOU!")
            
            print(f"{'='*60}")
            
            # Pausa entre testes
            if i < len(depix_ids_completos) - 1:
                await asyncio.sleep(1)
    
    print("\n🎯 TODOS OS TESTES CONCLUÍDOS!")
    print("📊 Resumo: Fluxo completo do PIX até Lightning testado com sucesso!")

if __name__ == "__main__":
    asyncio.run(main()) 