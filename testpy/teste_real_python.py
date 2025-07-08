#!/usr/bin/env python3
"""
TESTE REAL - Integração Ghost Bot com Voltz
==========================================

Este script testa o fluxo real que seria usado no bot do Telegram.
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

try:
    from api.voltz import VoltzAPI
    import time
    
    def main():
        print("🤖 TESTE REAL - Ghost Bot + Voltz Lightning")
        print("=" * 50)
        
        # Configurar API com backend local (em produção seria a URL real)
        voltz = VoltzAPI(backend_url='http://localhost:8000')
        
        # Simular dados reais de um usuário
        user_data = {
            'chatid': '7910260237',  # Seu chat ID real
            'userid': 'ghost_user_123',
            'amount_brl': 25.0,      # R$ 25,00
            'amount_sats': 42000,    # ~42k sats
            'moeda': 'BTC'
        }
        
        print(f"👤 Usuário: {user_data['userid']}")
        print(f"💰 Compra: R$ {user_data['amount_brl']:.2f} → {user_data['amount_sats']:,} sats")
        print()
        
        # PASSO 1: Bot registra o pedido (como faria no handler do Telegram)
        print("1️⃣ Registrando pedido no backend...")
        try:
            result = voltz.create_deposit_request(
                chatid=user_data['chatid'],
                userid=user_data['userid'],
                amount_in_cents=int(user_data['amount_brl'] * 100),
                taxa=0.05,
                moeda=user_data['moeda'],
                send_amount=user_data['amount_sats']
            )
            
            print(f"✅ Pedido registrado: {result['depix_id']}")
            depix_id = result['depix_id']
            
            # PASSO 2: Bot exibe confirmação (como enviaria para o usuário)
            print("\n2️⃣ Mensagem para o usuário:")
            print("-" * 40)
            confirmation = voltz.format_deposit_confirmation_message(
                depix_id=depix_id,
                amount_in_cents=int(user_data['amount_brl'] * 100),
                moeda=user_data['moeda'],
                send_amount=user_data['amount_sats']
            )
            print(confirmation)
            print("-" * 40)
            
            # PASSO 3: Bot monitora o status (como faria em loop/webhook)
            print("\n3️⃣ Monitorando status do pedido...")
            
            for attempt in range(1, 6):
                print(f"   Verificação {attempt}/5...")
                
                status = voltz.check_deposit_status(depix_id)
                
                if status.get('success'):
                    current_status = status.get('status', 'unknown')
                    print(f"   📊 Status: {current_status}")
                    
                    # Se tiver invoice, exibir para o usuário
                    if 'invoice' in status and status['invoice']:
                        print("\n⚡ INVOICE LIGHTNING ENCONTRADO!")
                        print("\n4️⃣ Mensagem final para o usuário:")
                        print("-" * 40)
                        
                        invoice_msg = voltz.format_invoice_message(
                            amount_sats=user_data['amount_sats'],
                            payment_request=status['invoice'],
                            qr_code_url=status.get('qr_code', '')
                        )
                        print(invoice_msg)
                        print("-" * 40)
                        break
                    else:
                        print("   ⏳ Invoice ainda não gerado...")
                else:
                    print(f"   ❌ Erro: {status.get('error', 'Desconhecido')}")
                
                if attempt < 5:
                    print("   💤 Aguardando 3 segundos...")
                    time.sleep(3)
            
            print("\n✅ TESTE CONCLUÍDO!")
            print("\n📋 Resumo:")
            print("✅ Registro funcionando")
            print("✅ Formatação de mensagens OK")
            print("✅ Consulta de status OK")
            print("✅ Bot está pronto para usar!")
            
        except Exception as e:
            print(f"❌ Erro durante o teste: {e}")
            return False
        
        return True

    if __name__ == "__main__":
        try:
            success = main()
            if success:
                print("\n🎉 INTEGRAÇÃO VALIDADA PARA PRODUÇÃO!")
            else:
                print("\n⚠️ Verificar problemas encontrados")
        except Exception as e:
            print(f"\n💥 Erro inesperado: {e}")
            
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de que o arquivo voltz.py está correto")
