import os
import sys
from dotenv import load_dotenv
from api.depix import pix_api

def main():
    # Carrega variáveis de ambiente do arquivo .env se existir
    load_dotenv()
    
    try:
        # Testa a criação de um pagamento PIX
        valor_centavos = 1000  # R$ 10,00 em centavos
        chave_pix = "teste@exemplo.com"  # Chave PIX de teste
        
        print(f"Criando pagamento PIX de R${valor_centavos/100:.2f} para a chave: {chave_pix}")
        
        # Cria o pagamento
        resultado = pix_api.criar_pagamento(valor_centavos, chave_pix)
        
        # Exibe os resultados
        print("\nPagamento criado com sucesso!")
        print(f"ID da transação: {resultado['transaction_id']}")
        print(f"URL do QR Code: {resultado['qr_image_url']}")
        print(f"Código PIX (copia e cola):\n{resultado['qr_copy_paste']}")
        
    except Exception as e:
        print(f"\nErro ao criar pagamento PIX: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
