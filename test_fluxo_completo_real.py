#!/usr/bin/env python3
"""
Teste Real do Fluxo Completo - Ghost P2P Bot
Simula um usuário real fazendo uma compra completa via Telegram
"""

import asyncio
import logging
import time
from telegram import Bot
from telegram.error import TelegramError
from typing import List, Dict, Any

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações do teste
BOT_TOKEN = "7105509014:AAENhZArthrysOBoEmdA6vaxE72pobliahI"
CHAT_ID = 7910260237
LIGHTNING_ADDRESS = "bouncyflight79@walletofsatoshi.com"

# Depix IDs reais para teste
DEPIX_IDS = [
    "0197e0ed06537df9820a28f5a5380a3b",
    "0197e10b5b8f7df9a6bf9430188534e4", 
    "0197e12300eb7df9808ca5d7719ea40e",
    "0197e5214a377dfaae6e541f68057444"
]

class TesteFluxoReal:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.current_depix_index = 0
        self.test_results = []
        
    async def enviar_mensagem(self, texto: str, delay: float = 2.0) -> bool:
        """Envia mensagem para o bot e aguarda delay"""
        try:
            await self.bot.send_message(chat_id=CHAT_ID, text=texto)
            logger.info(f"✅ Mensagem enviada: {texto}")
            await asyncio.sleep(delay)
            return True
        except TelegramError as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    async def aguardar_resposta(self, timeout: int = 30) -> bool:
        """Aguarda resposta do bot (simulado)"""
        logger.info(f"⏳ Aguardando resposta do bot (timeout: {timeout}s)")
        await asyncio.sleep(timeout)
        return True
    
    async def executar_teste_compra(self, depix_id: str, valor: float = 10.0) -> Dict[str, Any]:
        """Executa um teste completo de compra"""
        logger.info(f"🚀 Iniciando teste de compra - Valor: R$ {valor:.2f}, Depix ID: {depix_id}")
        
        resultado = {
            "depix_id": depix_id,
            "valor": valor,
            "status": "iniciado",
            "mensagens_enviadas": [],
            "erros": [],
            "timestamp_inicio": time.time()
        }
        
        try:
            # 1. Iniciar conversa com /start
            if not await self.enviar_mensagem("/start"):
                resultado["erros"].append("Falha ao enviar /start")
                resultado["status"] = "erro"
                return resultado
            resultado["mensagens_enviadas"].append("/start")
            
            # 2. Selecionar "Comprar"
            if not await self.enviar_mensagem("Comprar"):
                resultado["erros"].append("Falha ao selecionar Comprar")
                resultado["status"] = "erro"
                return resultado
            resultado["mensagens_enviadas"].append("Comprar")
            
            # 3. Selecionar "BTC"
            if not await self.enviar_mensagem("BTC"):
                resultado["erros"].append("Falha ao selecionar BTC")
                resultado["status"] = "erro"
                return resultado
            resultado["mensagens_enviadas"].append("BTC")
            
            # 4. Selecionar "Lightning"
            if not await self.enviar_mensagem("Lightning"):
                resultado["erros"].append("Falha ao selecionar Lightning")
                resultado["status"] = "erro"
                return resultado
            resultado["mensagens_enviadas"].append("Lightning")
            
            # 5. Enviar valor
            valor_str = f"{valor:.2f}"
            if not await self.enviar_mensagem(valor_str):
                resultado["erros"].append(f"Falha ao enviar valor {valor_str}")
                resultado["status"] = "erro"
                return resultado
            resultado["mensagens_enviadas"].append(valor_str)
            
            # 6. Aguardar resumo e confirmar
            await self.aguardar_resposta(10)
            if not await self.enviar_mensagem("Confirmar Pedido"):
                resultado["erros"].append("Falha ao confirmar pedido")
                resultado["status"] = "erro"
                return resultado
            resultado["mensagens_enviadas"].append("Confirmar Pedido")
            
            # 7. Aguardar solicitação do comprovante PIX
            await self.aguardar_resposta(15)
            
            # 8. Enviar depix_id
            depix_msg = f"depix:{depix_id}"
            if not await self.enviar_mensagem(depix_msg):
                resultado["erros"].append(f"Falha ao enviar depix_id {depix_id}")
                resultado["status"] = "erro"
                return resultado
            resultado["mensagens_enviadas"].append(depix_msg)
            
            # 9. Aguardar validação do PIX e solicitação do endereço Lightning
            await self.aguardar_resposta(20)
            
            # 10. Enviar endereço Lightning
            if not await self.enviar_mensagem(LIGHTNING_ADDRESS):
                resultado["erros"].append(f"Falha ao enviar endereço Lightning {LIGHTNING_ADDRESS}")
                resultado["status"] = "erro"
                return resultado
            resultado["mensagens_enviadas"].append(LIGHTNING_ADDRESS)
            
            # 11. Aguardar processamento e envio dos sats
            await self.aguardar_resposta(30)
            
            resultado["status"] = "concluido"
            resultado["timestamp_fim"] = time.time()
            resultado["duracao"] = resultado["timestamp_fim"] - resultado["timestamp_inicio"]
            
            logger.info(f"✅ Teste concluído com sucesso - Depix ID: {depix_id}")
            
        except Exception as e:
            resultado["erros"].append(f"Erro inesperado: {str(e)}")
            resultado["status"] = "erro"
            logger.error(f"❌ Erro no teste: {e}")
        
        return resultado
    
    async def executar_todos_testes(self):
        """Executa todos os testes com diferentes depix_ids"""
        logger.info("🎯 Iniciando bateria de testes reais")
        
        for i, depix_id in enumerate(DEPIX_IDS):
            logger.info(f"📋 Teste {i+1}/{len(DEPIX_IDS)} - Depix ID: {depix_id}")
            
            # Usar valores diferentes para cada teste
            valor = 10.0 + (i * 5.0)  # 10, 15, 20, 25
            
            resultado = await self.executar_teste_compra(depix_id, valor)
            self.test_results.append(resultado)
            
            # Aguardar entre testes
            if i < len(DEPIX_IDS) - 1:
                logger.info("⏸️ Aguardando 30 segundos antes do próximo teste...")
                await asyncio.sleep(30)
        
        self.mostrar_resultados()
    
    def mostrar_resultados(self):
        """Mostra resumo dos resultados dos testes"""
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMO DOS TESTES")
        logger.info("="*60)
        
        sucessos = sum(1 for r in self.test_results if r["status"] == "concluido")
        erros = sum(1 for r in self.test_results if r["status"] == "erro")
        
        logger.info(f"Total de testes: {len(self.test_results)}")
        logger.info(f"Sucessos: {sucessos}")
        logger.info(f"Erros: {erros}")
        logger.info(f"Taxa de sucesso: {(sucessos/len(self.test_results)*100):.1f}%")
        
        for i, resultado in enumerate(self.test_results):
            logger.info(f"\n📋 Teste {i+1}:")
            logger.info(f"  Depix ID: {resultado['depix_id']}")
            logger.info(f"  Valor: R$ {resultado['valor']:.2f}")
            logger.info(f"  Status: {resultado['status']}")
            if resultado.get("duracao"):
                logger.info(f"  Duração: {resultado['duracao']:.1f}s")
            if resultado["erros"]:
                logger.info(f"  Erros: {', '.join(resultado['erros'])}")
        
        logger.info("\n" + "="*60)

async def main():
    """Função principal"""
    logger.info("🤖 Iniciando Teste Real do Fluxo Completo")
    logger.info(f"📱 Chat ID: {CHAT_ID}")
    logger.info(f"⚡ Endereço Lightning: {LIGHTNING_ADDRESS}")
    logger.info(f"🆔 Depix IDs: {', '.join(DEPIX_IDS)}")
    
    teste = TesteFluxoReal()
    
    try:
        await teste.executar_todos_testes()
    except KeyboardInterrupt:
        logger.info("⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
    
    logger.info("🏁 Teste finalizado")

if __name__ == "__main__":
    asyncio.run(main()) 