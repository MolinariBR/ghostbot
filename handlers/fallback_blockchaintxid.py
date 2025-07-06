"""
Fallback automático para buscar blockchainTxID de depósitos on-chain (DePix)
"""
import asyncio
import logging
import requests
import os
from datetime import datetime
from typing import List, Dict

# Configuração de logging
logger = logging.getLogger("handlers.fallback_blockchaintxid")
logging.basicConfig(level=logging.INFO)

# Configurações
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "https://useghost.squareweb.app/api/deposit_pendentes.php")
DEPIX_API_URL = os.getenv("DEPIX_API_URL", "https://depix.eulen.app/api/deposit-status")
DEPIX_API_TOKEN = os.getenv("DEPIX_API_TOKEN", "SUA_API_KEY_AQUI")  # Troque para variável de ambiente real
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://useghost.squareweb.app/api/webhook.php")

CHECK_INTERVAL = int(os.getenv("FALLBACK_BLOCKCHAINTXID_INTERVAL", "60"))  # segundos


def get_pending_deposits() -> List[Dict]:
    """Busca depósitos com depix_id mas sem blockchainTxID via API do backend"""
    try:
        resp = requests.get(BACKEND_API_URL, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("pendentes", [])
        else:
            logger.warning(f"Backend API HTTP {resp.status_code}")
    except Exception as e:
        logger.error(f"Erro ao consultar backend pendentes: {e}")
    return []


def fetch_blockchaintxid_from_depix(depix_id: str) -> str:
    """Consulta a API DePix para buscar o blockchainTxID"""
    headers = {
        "Authorization": f"Bearer {DEPIX_API_TOKEN}"
    }
    params = {"id": depix_id}
    try:
        resp = requests.get(DEPIX_API_URL, headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            txid = data.get("response", {}).get("blockchainTxID")
            logger.info(f"Consulta DePix depix_id={depix_id} txid={txid}")
            return txid
        else:
            logger.warning(f"DePix API HTTP {resp.status_code} depix_id={depix_id}")
    except Exception as e:
        logger.error(f"Erro ao consultar DePix depix_id={depix_id}: {e}")
    return None


def send_blockchaintxid_to_webhook(depix_id: str, txid: str):
    """Envia o blockchainTxID para o webhook do backend com Authorization Bearer"""
    payload = {"id": depix_id, "blockchainTxID": txid}
    headers = {
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0"
    }
    try:
        resp = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        logger.info(f"Webhook depix_id={depix_id} txid={txid} HTTP={resp.status_code}")
    except Exception as e:
        logger.error(f"Erro ao enviar para webhook depix_id={depix_id}: {e}")


async def fallback_blockchaintxid_loop():
    logger.info("Iniciando fallback_blockchaintxid...")
    while True:
        pendentes = get_pending_deposits()
        logger.info(f"{len(pendentes)} depósitos pendentes para buscar blockchainTxID")
        for dep in pendentes:
            depix_id = dep["depix_id"]
            txid = fetch_blockchaintxid_from_depix(depix_id)
            if txid:
                send_blockchaintxid_to_webhook(depix_id, txid)
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(fallback_blockchaintxid_loop())
