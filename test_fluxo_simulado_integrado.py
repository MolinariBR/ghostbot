#!/usr/bin/env python3
"""
Teste Simulado Integrado - Ghost P2P Bot
Fluxo completo: APIs reais, registro real, simulação do pagamento PIX, consulta depix_id, saldo Voltz real, limites, etc.
"""
import requests
import time
import random
import string
import logging

# Configurações
BASE_URL = "https://useghost.squareweb.app/api"
VOLTZ_API = "https://useghost.squareweb.app/api/api_voltz.php"
DEPOSIT_API = f"{BASE_URL}/deposit.php"
DEPIX_CREATE_API = f"{BASE_URL}/depix/create_payment.php"

CHAT_ID = "999999999"  # Chat de teste
LIGHTNING_ADDRESS = "bouncyflight79@walletofsatoshi.com"

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("test_simulado_integrado")

def gerar_depix_id():
    return "simu_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))

def criar_pedido_real(valor, moeda="btc", rede="lightning"):
    """Cria um pedido real usando o endpoint correto do backend (api_cotacao.php)"""
    url = f"{BASE_URL}/api_cotacao.php"
    params = {
        "moeda": moeda,
        "rede": rede,
        "valor": valor,
        "valor_brl": valor,
        "chatid": CHAT_ID,
        "metodo": "pix",
        "action": "registrar",
        "vs": "brl",
        "compras": "1"
    }
    resp = requests.get(url, params=params)
    print(f"[DEBUG] Resposta bruta registrar pedido ({resp.status_code}): {resp.text}")
    data = resp.json()
    logger.info(f"Pedido registrado: {data}")
    return data.get("gtxid")

def consultar_validador(valor, moeda="btc", rede="lightning"):
    """Consulta o validador real do backend para obter cotação, comissão, limites, parceiro, etc."""
    url = f"{BASE_URL}/api_cotacao.php"
    params = {
        "moeda": moeda,
        "vs": "brl",
        "valor": valor,
        "chatid": CHAT_ID,
        "compras": 1,
        "metodo": "pix"
    }
    resp = requests.get(url, params=params)
    print(f"[DEBUG] Resposta bruta validador ({resp.status_code}): {resp.text}")
    data = resp.json()
    logger.info(f"Validador: {data}")
    return data

def registrar_deposito(valor, depix_id, blockchainTxID=None, status="pending", send=100, taxa=0.0):
    """Registra o depósito no banco via endpoint real"""
    payload = {
        "chatid": CHAT_ID,
        "moeda": "btc",
        "rede": "lightning",
        "amount_in_cents": int(valor*100),
        "taxa": taxa,
        "address": LIGHTNING_ADDRESS,
        "forma_pagamento": "pix",
        "send": send,
        "user_id": CHAT_ID,
        "depix_id": depix_id,
        "status": status,
        "blockchainTxID": blockchainTxID,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    resp = requests.post(DEPOSIT_API, json=payload)
    logger.info(f"Registro de depósito: {resp.text}")
    return resp.ok

def simular_pagamento_pix(valor):
    """Simula o pagamento PIX: cria depix_id e insere blockchainTxID"""
    depix_id = gerar_depix_id()
    blockchainTxID = "btxid_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    registrar_deposito(valor, depix_id, status="paid", blockchainTxID=blockchainTxID, send=100)
    return depix_id, blockchainTxID

def consultar_deposito(depix_id):
    """Consulta o depósito pelo depix_id"""
    params = {"action": "get", "depix_id": depix_id}
    resp = requests.get(DEPOSIT_API, params=params)
    logger.info(f"Consulta depósito: {resp.text}")
    return resp.json()

def consultar_saldo_voltz():
    """Consulta o saldo real da Voltz"""
    resp = requests.get(f"{VOLTZ_API}?method=GET&endpoint=balance")
    data = resp.json()
    logger.info(f"Saldo Voltz: {data}")
    return data.get("data", {}).get("balance", 0)

def fluxo_completo(valor):
    logger.info(f"Iniciando fluxo completo para valor R$ {valor:.2f}")
    # 1. Consulta validador
    validador = consultar_validador(valor)
    assert validador.get("success"), f"Validador falhou: {validador}"
    resumo = validador.get("resumo") or validador
    logger.info(f"Resumo da compra: {resumo}")
    # 2. Cria pedido real
    gtxid = criar_pedido_real(valor)
    assert gtxid, "Falha ao criar pedido real"
    # 3. Simula pagamento PIX
    depix_id, blockchainTxID = simular_pagamento_pix(valor)
    # 4. Consulta depósito para buscar blockchainTxID
    deposito = consultar_deposito(depix_id)
    assert deposito.get("blockchainTxID") == blockchainTxID, "blockchainTxID não encontrado"
    logger.info(f"blockchainTxID encontrado: {blockchainTxID}")
    # 5. Consulta saldo Voltz real
    saldo = consultar_saldo_voltz()
    logger.info(f"Saldo Voltz: {saldo} sats")
    # 6. Simula envio dos sats (apenas loga, não envia de verdade)
    sats = 100
    if saldo < sats:
        logger.warning(f"Saldo insuficiente para enviar {sats} sats")
    else:
        logger.info(f"Simulando envio de {sats} sats para {LIGHTNING_ADDRESS}")
    logger.info("Fluxo completo simulado com sucesso!")

def main():
    logger.info("==== TESTE SIMULADO INTEGRADO GHOST P2P ====")
    logger.info("Executando fluxo completo apenas para valor R$ 10,00...")
    fluxo_completo(10.0)
    logger.info("==== FIM DO TESTE ====")

if __name__ == "__main__":
    main() 