#!/usr/bin/env python3
"""
Criar depósitos Lightning para teste no banco local
Usa dados simulados baseados nos depix_ids reais para testar o fluxo
"""

import sqlite3
import time
import json

# Dados simulados baseados nos depix_ids reais
DEPOSITOS_TESTE = [
    {
        "depix_id_base": "0197e0ed06537df9820a28f5a5380a3b",
        "valor_cents": 1000,  # R$ 10,00
        "chatid": "7910260237"
    },
    {
        "depix_id_base": "0197e10b5b8f7df9a6bf9430188534e4", 
        "valor_cents": 500,   # R$ 5,00
        "chatid": "7910260237"
    },
    {
        "depix_id_base": "0197e12300eb7df9808ca5d7719ea40e",
        "valor_cents": 1500,  # R$ 15,00
        "chatid": "7910260237"
    }
]

def conectar_banco():
    """Conecta ao banco SQLite local"""
    try:
        conn = sqlite3.connect('/home/mau/bot/ghostbackend/data/admin.db')
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar banco: {e}")
        return None

def criar_deposito_local(dados_teste):
    """Cria depósito Lightning no banco local"""
    
    timestamp = int(time.time())
    depix_id_teste = f"teste_ln_{timestamp}_{dados_teste['depix_id_base'][-6:]}"
    blockchain_txid = f"teste_txid_{timestamp}"
    
    deposito = {
        'depix_id': depix_id_teste,
        'chatid': dados_teste['chatid'],
        'amount_in_cents': dados_teste['valor_cents'],
        'taxa': '0.005',  # 0.5%
        'moeda': 'BTC',
        'rede': 'lightning',
        'address': 'voltz@mail.com',
        'forma_pagamento': 'PIX',
        'send': str(dados_teste['valor_cents']),
        'status': 'confirmed',  # Simular PIX já confirmado
        'blockchainTxID': blockchain_txid,
        'comprovante': '',  # Vazio para que o cron processe
        'user_id': dados_teste['chatid'],
        'observacoes': f"Teste Lightning baseado em {dados_teste['depix_id_base']}"
    }
    
    return deposito, depix_id_teste

def inserir_deposito_banco(conn, deposito):
    """Insere depósito no banco SQLite"""
    try:
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO deposit (
            depix_id, chatid, amount_in_cents, taxa, moeda, rede, address,
            forma_pagamento, send, status, blockchainTxID, comprovante, 
            user_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """
        
        valores = (
            deposito['depix_id'],
            deposito['chatid'], 
            deposito['amount_in_cents'],
            deposito['taxa'],
            deposito['moeda'],
            deposito['rede'],
            deposito['address'],
            deposito['forma_pagamento'],
            deposito['send'],
            deposito['status'],
            deposito['blockchainTxID'],
            deposito['comprovante'],
            deposito['user_id']
        )
        
        cursor.execute(sql, valores)
        conn.commit()
        
        print(f"✅ Depósito {deposito['depix_id']} inserido no banco local")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir {deposito['depix_id']}: {e}")
        return False

def main():
    print("🧪 CRIANDO DEPÓSITOS LIGHTNING NO BANCO LOCAL")
    print("=" * 55)
    
    conn = conectar_banco()
    if not conn:
        print("❌ Não foi possível conectar ao banco")
        return
    
    depositos_criados = []
    
    for dados_teste in DEPOSITOS_TESTE:
        print(f"\n🔍 Criando depósito baseado em {dados_teste['depix_id_base'][-6:]}...")
        
        # Criar dados do depósito
        deposito, depix_id_teste = criar_deposito_local(dados_teste)
        
        # Inserir no banco
        if inserir_deposito_banco(conn, deposito):
            depositos_criados.append({
                'depix_id': depix_id_teste,
                'valor': dados_teste['valor_cents']/100,
                'blockchainTxID': deposito['blockchainTxID'],
                'chatid': deposito['chatid']
            })
        
        time.sleep(1)
    
    conn.close()
    
    print(f"\n🎉 RESUMO - {len(depositos_criados)} depósitos criados:")
    print("=" * 55)
    
    for dep in depositos_criados:
        print(f"✅ {dep['depix_id']}")
        print(f"   💰 R$ {dep['valor']:.2f}")
        print(f"   🔗 {dep['blockchainTxID']}")
        print(f"   💬 Chat: {dep['chatid']}")
        print()
    
    if depositos_criados:
        print("🚀 PRÓXIMOS PASSOS:")
        print("1. Execute o endpoint cron Lightning para detectar os depósitos")
        print("2. O bot deve solicitar invoice Lightning via Telegram")
        print("3. Teste enviando um invoice Lightning no chat")
        print(f"\n🔗 Teste o cron: curl 'https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025'")

if __name__ == "__main__":
    main()
