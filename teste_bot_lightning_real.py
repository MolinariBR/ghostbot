#!/usr/bin/env python3
"""
Teste completo: Cria um depósito Lightning com PIX confirmado para testar o bot
"""

import json
import requests
import time
import sqlite3

def criar_teste_lightning_real():
    """Cria um depósito Lightning com PIX já confirmado diretamente no banco"""
    
    print("⚡ TESTE FLUXO LIGHTNING REAL")
    print("=" * 50)
    
    # Dados do teste
    chat_id = "7910260237"  # Chat ID real existente
    depix_id = f"LN_TESTE_REAL_{int(time.time())}"
    blockchain_txid = f"pix_confirmado_{int(time.time())}"
    
    print(f"📦 Chat ID: {chat_id}")
    print(f"🆔 Depix ID: {depix_id}")
    print(f"🔗 Blockchain TxID: {blockchain_txid}")
    
    # Conecta diretamente ao banco para criar um registro realista
    try:
        # Primeiro via API
        payload = {
            "chatid": chat_id,
            "moeda": "BTC", 
            "rede": "lightning",
            "amount_in_cents": 10000,  # R$ 100,00
            "taxa": 5.0,
            "address": "aguardando_lightning_address",
            "forma_pagamento": "PIX",
            "send": 15000,  # 15.000 sats
            "user_id": int(chat_id),
            "depix_id": depix_id,
            "status": "pending",
            "comprovante": "Lightning Invoice"
        }
        
        print("\n📤 PASSO 1: Criando depósito via API...")
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "https://useghost.squareweb.app/rest/deposit.php",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get('success'):
                deposit_id = resp_json.get('id')
                print(f"✅ Depósito criado via API! ID: {deposit_id}")
                
                # PASSO 2: Atualizar diretamente no banco local para simular PIX confirmado
                print("\n📤 PASSO 2: Simulando PIX confirmado (atualizando banco local)...")
                
                try:
                    # Conecta ao banco local para atualizar o registro
                    db_path = "/home/mau/bot/ghostbackend/data/deposit.db"
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Atualiza o registro com blockchainTxID e status
                    cursor.execute("""
                        UPDATE deposit 
                        SET blockchainTxID = ?, status = ?
                        WHERE id = ?
                    """, (blockchain_txid, "awaiting_client_invoice", deposit_id))
                    
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        print(f"✅ Registro atualizado no banco local!")
                        print(f"   • Status: awaiting_client_invoice")
                        print(f"   • Blockchain TxID: {blockchain_txid}")
                        
                        print(f"\n🎯 TESTE MANUAL NO TELEGRAM:")
                        print(f"   • Envie uma mensagem para o bot pelo chat ID: {chat_id}")
                        print(f"   • O bot deveria detectar o depósito Lightning pendente")
                        print(f"   • E solicitar o Lightning Address ou Invoice")
                        print(f"   • Depix ID: {depix_id}")
                        print(f"   • Valor: 15.000 sats (R$ 100,00)")
                        
                        return True
                        
                    else:
                        print("❌ Falha ao atualizar registro no banco")
                        return False
                        
                    conn.close()
                    
                except Exception as e:
                    print(f"❌ Erro ao atualizar banco local: {e}")
                    return False
                
            else:
                print(f"❌ Erro na API: {resp_json}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False

if __name__ == "__main__":
    criar_teste_lightning_real()
