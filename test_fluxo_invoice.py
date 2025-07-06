import asyncio
from handlers.fluxo_envio_invoice import fluxo_envio_invoice

# Parâmetros de teste
DEPIX_ID = "0197e06528ab7df986bf7c7f7cc1cb1a"
CHAT_ID = 7910260237  # Substitua pelo seu chat_id de teste se necessário

async def main():
    print(f"Testando fluxo_envio_invoice para depix_id={DEPIX_ID} chat_id={CHAT_ID}")
    await fluxo_envio_invoice(depix_id=DEPIX_ID, chat_id=CHAT_ID, is_lightning=True, bot=None)
    print("Teste finalizado.")

if __name__ == "__main__":
    asyncio.run(main())
