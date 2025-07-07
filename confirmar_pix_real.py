#!/usr/bin/env python3
"""
Simular confirmação PIX para depósitos Lightning reais existentes
Usando os depix_ids de PIX já pagos pelo usuário (R$ 10,00 cada)
"""

import requests
import time
import json

# Usar 2 depix_ids reais para teste (R$ 10,00 cada = ~1667 sats cada = 3334 sats total)
DEPIX_IDS_REAIS = [
    "teste_1751898619",  # Depósito real de R$ 10,00 no banco local
    "teste_1751898574",  # Segundo depósito real de R$ 10,00 no banco local
]

def simular_pix_confirmado(depix_id):
    """Simula confirmação PIX para um depósito Lightning real existente"""
    
    timestamp = int(time.time())
    
    # Tentar direto via SQLite se a API não funcionar
    try:
        import sqlite3
        conn = sqlite3.connect('../ghostbackend/data/deposit.db')
        cursor = conn.cursor()
        
        # Atualizar status e blockchainTxID
        blockchain_txid = f"pix_confirmado_{timestamp}_{depix_id[-6:]}"
        
        cursor.execute("""
            UPDATE deposit 
            SET status = 'confirmed', blockchainTxID = ?
            WHERE depix_id = ?
        """, (blockchain_txid, depix_id))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ PIX confirmado via SQLite: {depix_id}")
            print(f"   🔗 TxID: {blockchain_txid}")
            return True
        else:
            print(f"❌ Depósito {depix_id} não encontrado no banco")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao confirmar PIX {depix_id}: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    print("🚀 SIMULANDO CONFIRMAÇÃO PIX PARA DEPÓSITO LIGHTNING REAL")
    print("=" * 65)
    print("📋 Usando 2 depix_ids de PIX já pagos (R$ 10,00 cada)")
    print("💰 Valor total: R$ 20,00 = ~3334 sats (disponível: 3368 sats)")
    print()
    
    depositos_confirmados = []
    
    for i, depix_id in enumerate(DEPIX_IDS_REAIS, 1):
        print(f"🔹 Confirmando PIX {i}/{len(DEPIX_IDS_REAIS)} - {depix_id}...")
        
        if simular_pix_confirmado(depix_id):
            depositos_confirmados.append(depix_id)
            time.sleep(1)  # Aguardar entre operações
        
        print()
    
    print(f"🎉 RESUMO: {len(depositos_confirmados)}/{len(DEPIX_IDS_REAIS)} PIX confirmados")
    
    if depositos_confirmados:
        print()
        print("🚀 PRÓXIMOS PASSOS:")
        print("1. Os PIX foram confirmados para depósitos Lightning reais")
        print("2. Execute o cron Lightning para detectá-los:")
        print("   curl 'https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025'")
        print("3. O bot deve solicitar invoice Lightning no Telegram")
        print()
        print("💡 VALORES REAIS:")
        sats_por_deposito = int(10.0 * 166.67)  # R$ 10,00
        total_sats = sats_por_deposito * len(depositos_confirmados)
        print(f"   • Cada PIX: R$ 10,00 = ~{sats_por_deposito} sats")
        print(f"   • Total: R$ {len(depositos_confirmados)*10:.0f},00 = ~{total_sats} sats")
        print(f"   📊 Saldo necessário: {total_sats} sats (disponível: 3368 sats) ✅")

if __name__ == "__main__":
    main()
