#!/usr/bin/env python3
"""
Teste simplificado da integração Voltz
Testa diretamente os métodos do VoltzAPI
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

from api.voltz import VoltzAPI
import time
import random

def test_simple():
    print("🧪 Teste Simplificado da Integração Voltz")
    print("=" * 50)
    
    # Configurar API com backend local
    voltz = VoltzAPI(backend_url='http://localhost:8000')
    
    try:
        print("1. 📝 Testando criação de depósito...")
        
        # Dados de teste
        chatid = "test_123456"
        userid = "test_user_789"
        amount_in_cents = 2500  # R$ 25,00
        taxa = 0.05
        moeda = "BTC"
        send_amount = 45000  # 45k sats
        
        result = voltz.create_deposit_request(
            chatid=chatid,
            userid=userid,
            amount_in_cents=amount_in_cents,
            taxa=taxa,
            moeda=moeda,
            send_amount=send_amount
        )
        
        print(f"✅ Resultado: {result}")
        
        if 'depix_id' in result:
            depix_id = result['depix_id']
            print(f"🆔 Depix ID criado: {depix_id}")
            
            # Teste de formatação de mensagem
            print("\n2. 💬 Testando formatação de mensagens...")
            
            confirmation_msg = voltz.format_deposit_confirmation_message(
                depix_id=depix_id,
                amount_in_cents=amount_in_cents,
                moeda=moeda,
                send_amount=send_amount
            )
            
            print("📱 Mensagem de confirmação:")
            print("-" * 40)
            print(confirmation_msg)
            print("-" * 40)
            
            # Teste de verificação de status
            print("\n3. 🔍 Testando verificação de status...")
            
            for i in range(3):
                print(f"Tentativa {i+1}/3...")
                status = voltz.check_deposit_status(depix_id)
                print(f"Status: {status}")
                
                if status.get('success') and status.get('invoice'):
                    print("⚡ Invoice encontrado!")
                    invoice_msg = voltz.format_invoice_message(
                        amount_sats=send_amount,
                        payment_request=status['invoice'],
                        qr_code_url=status.get('qr_code', '')
                    )
                    print("📱 Mensagem do invoice:")
                    print("-" * 40)
                    print(invoice_msg)
                    print("-" * 40)
                    break
                
                time.sleep(2)
            
            print("\n✅ Teste concluído com sucesso!")
            
        else:
            print("❌ Falha na criação do depósito")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()
