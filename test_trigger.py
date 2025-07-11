#!/usr/bin/env python3
"""
Script para testar o gatilho ADDRESS_REQUESTED
"""
import sys
import os
sys.path.append('/home/mau/bot/ghost')

def test_trigger():
    try:
        from trigger.sistema_gatilhos import trigger_system, TriggerEvent
        print('✅ Imports OK')
        
        # Testar gatilho direto
        result = trigger_system.trigger_event(
            TriggerEvent.ADDRESS_REQUESTED,
            '7910260237',
            {
                'depix_id': '0197f6f3c6527dfe9d7ff3bdc3954e93',
                'blockchain_txid': 'fabadf97668ed1e6bc943fb41eeef5bf713dbd00a66a25943f1a1cb2a09b89de',
                'timestamp': '2025-07-10T22:00:00'
            }
        )
        print(f'✅ Gatilho disparado: {result}')
        return True
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_trigger()
