import asyncio
import logging
import sqlite3
from typing import Dict, Optional

logger = logging.getLogger("handlers.fluxo_envio_invoice")

CAMPOS_OBRIGATORIOS = [
    "blockchainTxID", "chat_id", "depix_id", "data", "valor", "taxa", "moeda"
]

DB_PATH = "/home/mau/bot/ghostbackend/data/deposit.db"

def get_deposit_row(depix_id: str) -> Optional[Dict]:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM deposit WHERE depix_id = ? LIMIT 1"
        cursor = conn.execute(query, (depix_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception as e:
        logger.error(f"Erro ao buscar depósito depix_id={depix_id}: {e}")
    return None

async def buscar_dados_deposito(depix_id: str) -> Optional[Dict]:
    return get_deposit_row(depix_id)

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
        await asyncio.sleep(3)
    # Se não conseguiu, envia mensagem de atendimento manual
    logger.warning(f"Falha após 5 tentativas para depix_id={depix_id} chat_id={chat_id}. Encaminhar para suporte.")
    if bot:
        await bot.send_message(
            chat_id=chat_id,
            text="Não foi possível processar automaticamente seu pagamento. Por favor, entre em contato com o suporte: @GhosttP2P"
        )
