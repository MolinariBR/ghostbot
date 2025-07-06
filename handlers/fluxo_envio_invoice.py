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
    while True:
        dados = await buscar_dados_deposito(depix_id)
        campos_necessarios = CAMPOS_OBRIGATORIOS + (["rede"] if is_lightning else [])
        if dados and all(dados.get(c) for c in campos_necessarios):
            await acionar_voltz_e_enviar_invoice(dados, chat_id, bot=bot)
            return
        logger.info(f"Tentativa para depix_id={depix_id} chat_id={chat_id} (loop infinito)")
        await asyncio.sleep(30)  # Aguarda 30 segundos antes da próxima tentativa
