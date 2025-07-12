#!/usr/bin/env python3
"""
Script para simular o fluxo completo: registrar pagamento PIX e disparar gatilho
"""
import sys
import os
sys.path.append('/home/mau/bot/ghost')

def simulate_pix_flow():
    try:
        print("🚀 Iniciando simulação do fluxo PIX...")
        
        # Dados do PIX real do log
        depix_id = '0197f6f3c6527dfe9d7ff3bdc3954e93'
        chat_id = '7910260237'
        amount_brl = 10.0
        blockchain_txid = 'fabadf97668ed1e6bc943fb41eeef5bf713dbd00a66a25943f1a1cb2a09b89de'
        
        # 1. Registrar pagamento no monitor
        from trigger.smart_pix_monitor import register_pix_payment, smart_monitor
        print("📝 Registrando pagamento no monitor...")
        register_pix_payment(depix_id, chat_id, amount_brl)
        
        # 2. Simular detecção do blockchainTxID
        print("🔍 Simulando detecção do blockchainTxID...")
        
        # Adicionar diretamente aos active_payments
        from datetime import datetime
        smart_monitor.active_payments[depix_id] = {
            'chat_id': chat_id,
            'amount': amount_brl,
            'depix_id': depix_id,
            'registered_at': datetime.now(),
            'blockchain_txid': blockchain_txid,
            'confirmed_at': datetime.now()
        }
        
        print(f"✅ Pagamento registrado: {depix_id}")
        print(f"💰 Valor: R$ {amount_brl}")
        print(f"👤 Chat ID: {chat_id}")
        print(f"🔗 Blockchain TxID: {blockchain_txid}")
        
        # 3. Chamar processamento manual
        print("⚡ Processando pagamento confirmado...")
        import asyncio
        asyncio.run(smart_monitor._process_confirmed_payment(depix_id, smart_monitor.active_payments[depix_id]))
        
        print("✅ Simulação concluída!")
        return True
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    simulate_pix_flow()
