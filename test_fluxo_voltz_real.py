#!/usr/bin/env python3
"""
Teste Real de Envio Voltz - GhostBot
Consulta saldo, resolve Lightning Address, envia sats e verifica status do pagamento usando o código de produção.
"""
import logging
import time
from api.bot_voltz import voltz_api, VoltzAPIError

LIGHTNING_ADDRESS = "bouncyflight79@walletofsatoshi.com"
VALOR_SATS = 1000  # valor real a enviar

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("test_fluxo_voltz_real")

def main():
    logger.info("==== TESTE REAL VOLTZ ====")
    try:
        # 1. Consulta saldo real
        saldo = voltz_api.get_balance()
        logger.info(f"Saldo Voltz: {saldo.get('balance', 0)} sats")
        if saldo.get('balance', 0) < VALOR_SATS:
            logger.error(f"Saldo insuficiente para enviar {VALOR_SATS} sats!")
            return
        # 2. Resolve Lightning Address para invoice (se necessário)
        logger.info(f"Resolvendo Lightning Address: {LIGHTNING_ADDRESS}")
        decoded = voltz_api.decode_invoice(LIGHTNING_ADDRESS)
        invoice = decoded.get('pr') or decoded.get('payment_request') or LIGHTNING_ADDRESS
        logger.info(f"Invoice BOLT11: {invoice[:40]}...")
        # 3. Envia os sats
        logger.info(f"Enviando {VALOR_SATS} sats para {LIGHTNING_ADDRESS}...")
        result = voltz_api.pay_invoice(invoice)
        payment_hash = result.get('payment_hash')
        logger.info(f"Resultado do envio: {result}")
        if not payment_hash:
            logger.error("Não foi possível obter o payment_hash do envio!")
            return
        # 4. Verifica status do pagamento
        logger.info(f"Verificando status do pagamento: {payment_hash}")
        for i in range(10):
            status = voltz_api.check_payment(payment_hash)
            logger.info(f"Status tentativa {i+1}: {status}")
            if status.get('paid'):
                logger.info("Pagamento confirmado!")
                break
            time.sleep(3)
        else:
            logger.warning("Pagamento não confirmado após 10 tentativas.")
    except VoltzAPIError as e:
        logger.error(f"Erro na API Voltz: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    logger.info("==== FIM DO TESTE REAL VOLTZ ====")

if __name__ == "__main__":
    main() 