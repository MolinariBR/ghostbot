import asyncio
import logging
import os
import aiohttp
from typing import Dict, Optional
from tokens import Config

logger = logging.getLogger("handlers.fluxo_envio_invoice")

CAMPOS_OBRIGATORIOS = [
    "blockchainTxID", "chat_id", "depix_id", "data", "valor", "taxa", "moeda"
]

API_URL = "https://useghost.squareweb.app/api/deposit_pendentes.php"
API_TOKEN = getattr(Config, "API_LISTA_PENDENTES_KEY", "SUA_CHAVE_AQUI")

async def buscar_dados_deposito(depix_id: str) -> Optional[Dict]:
    """
    Busca os dados do depósito via API REST do backend (com header X-API-KEY).
    """
    try:
        async with aiohttp.ClientSession() as session:
            params = {"depix_id": depix_id}
            headers = {"X-API-KEY": API_TOKEN}
            async with session.get(API_URL, params=params, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Espera que a API retorne {'success': True, 'deposit': {...}}
                    if data.get("success") and data.get("deposit"):
                        return data["deposit"]
    except Exception as e:
        logger.error(f"Erro ao buscar depósito depix_id={depix_id} via API: {e}")
    return None

async def acionar_voltz_e_enviar_invoice(dados: Dict, chat_id: str, bot=None):
    """
    Chama o Voltz para criar o invoice e envia ao cliente.
    """
    # TODO: Implementar integração real com Voltz e envio Telegram
    logger.info(f"Invoice enviado para chat_id={chat_id} | dados={dados}")
    # Exemplo de envio: await bot.send_message(chat_id, "Seu invoice está aqui: ...")

async def fluxo_envio_invoice(depix_id: str, chat_id: str, is_lightning: bool = False, bot=None):
    tentativas = 0
    while tentativas < 5:
        dados = await buscar_dados_deposito(depix_id)
        campos_necessarios = CAMPOS_OBRIGATORIOS + (["rede"] if is_lightning else [])
        if dados and all(dados.get(c) for c in campos_necessarios):
            await acionar_voltz_e_enviar_invoice(dados, chat_id, bot=bot)
            return
        tentativas += 1
        logger.info(f"Tentativa {tentativas}/5 para depix_id={depix_id} chat_id={chat_id}")
        await asyncio.sleep(2)  # Reduzido temporariamente para 2 segundos para teste
    # Se não conseguiu, envia mensagem de atendimento manual
    logger.warning(f"Falha após 5 tentativas para depix_id={depix_id} chat_id={chat_id}. Encaminhar para suporte.")
    if bot:
        await bot.send_message(
            chat_id=chat_id,
            text="Não foi possível processar automaticamente seu pagamento. Por favor, entre em contato com o suporte: @GhosttP2P"
        )
