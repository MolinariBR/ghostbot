"""
Script de teste para a integração com a API PIX.

Este script testa a funcionalidade básica da API PIX, incluindo a criação de pagamentos
e verificação de status. Ele usa as configurações definidas em tokens.py.
"""
import sys
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from api.depix import pix_api, PixAPIError

# Configurações
DB_PATH = Path(__file__).parent / 'database' / 'deposit.db'

def configurar_logging():
    """Configura o logging para exibir mensagens no console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

def salvar_transacao_pix(user_id: int, transaction_data: dict) -> bool:
    """
    Salva os dados da transação PIX no banco de dados.
    
    Args:
        user_id: ID do usuário no Telegram
        transaction_data: Dados da transação retornados pela API PIX
        
    Returns:
        bool: True se a transação foi salva com sucesso, False caso contrário
    """
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            
            # Dados de exemplo para teste
            # Em um cenário real, esses valores viriam do fluxo de compra
            dados_teste = {
                'user_id': user_id,
                'amount_brl': transaction_data.get('amount_brl', 10.0),  # Valor em reais
                'amount_crypto': 0.001,  # Valor em criptomoeda (exemplo)
                'crypto_currency': 'BTC',  # Moeda de exemplo
                'crypto_address': 'bc1qexampleaddress',  # Endereço de exemplo
                'qr_image_url': transaction_data.get('qr_image_url', ''),
                'qr_copy_paste': transaction_data.get('qr_copy_paste', ''),
                'status': 'pending'
            }
            
            cursor.execute("""
                INSERT INTO pix_transactions (
                    user_id, transaction_id, amount_brl, amount_crypto,
                    crypto_currency, crypto_address, qr_image_url, qr_copy_paste, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados_teste['user_id'],
                transaction_data.get('transaction_id', ''),
                dados_teste['amount_brl'],
                dados_teste['amount_crypto'],
                dados_teste['crypto_currency'],
                dados_teste['crypto_address'],
                dados_teste['qr_image_url'],
                dados_teste['qr_copy_paste'],
                dados_teste['status']
            ))
            
            conn.commit()
            return True
            
    except sqlite3.Error as e:
        print(f"Erro ao salvar transação no banco de dados: {e}")
        return False

def testar_criacao_pagamento():
    """Testa a criação de um pagamento PIX."""
    try:
        # Dados de teste
        chat_id = 123456789  # ID do chat do Telegram para teste
        valor_centavos = 1000  # R$ 10,00 em centavos
        
        print(f"\n🔹 Testando criação de pagamento PIX de R${valor_centavos/100:.2f}")
        print(f"👤 Chat ID: {chat_id}")
        
        # Cria o pagamento
        print("\n🔄 Criando pagamento...")
        resultado = pix_api.criar_pagamento(valor_centavos)
        
        # Adiciona o valor em reais ao resultado para exibição
        resultado['amount_brl'] = valor_centavos / 100
        
        # Salva a transação no banco de dados
        print("\n💾 Salvando transação no banco de dados...")
        if salvar_transacao_pix(chat_id, resultado):
            print("✅ Transação salva com sucesso no banco de dados")
        else:
            print("⚠️  Não foi possível salvar a transação no banco de dados")
        
        # Exibe os resultados
        print("\n✅ Pagamento criado com sucesso!")
        print(f"📋 ID da transação: {resultado.get('transaction_id', 'N/A')}")
        print(f"💰 Valor: R$ {resultado['amount_brl']:.2f}")
        
        if 'qr_image_url' in resultado:
            print(f"🖼️  URL do QR Code: {resultado['qr_image_url']}")
        
        # Usa qr_code_text se existir, senão usa qr_copy_paste
        qr_code = resultado.get('qr_code_text', resultado.get('qr_copy_paste', ''))
        if qr_code:
            print(f"📋 Código PIX (copia e cola):\n{qr_code}")
        
        return True
        
    except PixAPIError as e:
        print(f"\n❌ Erro na API PIX: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal do script de teste."""
    print("\n🔍 Iniciando testes da integração com a API PIX...")
    
    # Configura o logging
    configurar_logging()
    
    # Executa os testes
    sucesso = testar_criacao_pagamento()
    
    # Exibe o resultado final
    if sucesso:
        print("\n✨ Todos os testes foram concluídos com sucesso!")
    else:
        print("\n❌ Alguns testes falharam. Verifique as mensagens de erro acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
