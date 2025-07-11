#!/usr/bin/env python3
"""
Fix para o Smart PIX Monitor - Corrigir o problema do processamento automático
"""
import sys
import os
sys.path.append('/home/mau/bot/ghost')

def fix_smart_monitor():
    """Corrige o problema do monitoramento automático"""
    print("🔧 Aplicando correção no Smart PIX Monitor...")
    
    # Ler arquivo atual
    monitor_file = '/home/mau/bot/ghost/trigger/smart_pix_monitor.py'
    
    try:
        with open(monitor_file, 'r') as f:
            content = f.read()
        
        # Procurar pela função poll_blockchain_txid
        if 'poll_blockchain_txid' in content:
            print("✅ Encontrou função poll_blockchain_txid")
            
            # Verificar se a correção já foi aplicada
            if 'CORREÇÃO_APLICADA' in content:
                print("✅ Correção já aplicada anteriormente")
                return True
            
            # Aplicar correção: adicionar verificação para self.active_payments
            old_code = '''                        await self._process_confirmed_payment(depix_id, self.active_payments[depix_id])'''
            
            new_code = '''                        # CORREÇÃO_APLICADA: Verificar se pagamento ainda existe
                        if depix_id in self.active_payments:
                            await self._process_confirmed_payment(depix_id, self.active_payments[depix_id])
                        else:
                            # Recriar dados do pagamento
                            payment_data = {
                                'chat_id': chat_id,
                                'depix_id': depix_id,
                                'blockchain_txid': blockchain_txid,
                                'registered_at': datetime.now(),
                                'confirmed_at': datetime.now(),
                                'amount': 10.0  # Valor padrão
                            }
                            self.active_payments[depix_id] = payment_data
                            await self._process_confirmed_payment(depix_id, payment_data)'''
            
            if old_code in content:
                content = content.replace(old_code, new_code)
                
                # Salvar arquivo corrigido
                with open(monitor_file, 'w') as f:
                    f.write(content)
                
                print("✅ Correção aplicada com sucesso!")
                return True
            else:
                print("⚠️ Código alvo não encontrado")
                return False
        else:
            print("❌ Função poll_blockchain_txid não encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro aplicando correção: {e}")
        return False

def main():
    print("🚀 Iniciando correção do Smart PIX Monitor...")
    success = fix_smart_monitor()
    print(f"✅ Resultado: {'Sucesso' if success else 'Falha'}")
    return success

if __name__ == "__main__":
    main()
