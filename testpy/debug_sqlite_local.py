#!/usr/bin/env python3
"""
Debug local do fluxo Lightning - consulta direta ao SQLite
Verifica o depósito no banco local e simula o processamento do cron
"""
import sqlite3
import json
import sys
from datetime import datetime

depix_id = "0197ea6c80bc7dfc81b1e02fe8d06954"
chat_id = "7910260237"
db_path = "/home/mau/bot/ghostbackend/data/deposit.db"

def format_timestamp(ts):
    """Formata timestamp para leitura humana"""
    if ts:
        try:
            return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return ts
    return "N/A"

def main():
    print("\n🔍 DEBUG LOCAL DO FLUXO LIGHTNING - CONSULTA DIRETA SQLite")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        cursor = conn.cursor()
        
        print(f"✅ Conectado ao banco: {db_path}")
        print(f"🎯 Procurando depósito: {depix_id}")
        print(f"💬 Chat ID esperado: {chat_id}")
        
        # 1. Consultar o depósito específico
        print(f"\n1️⃣ CONSULTANDO DEPÓSITO ESPECÍFICO")
        print("-" * 50)
        
        cursor.execute("""
            SELECT * FROM deposit 
            WHERE depix_id = ?
        """, (depix_id,))
        
        deposito = cursor.fetchone()
        
        if deposito:
            print("✅ Depósito encontrado!")
            print(f"   📝 depix_id: {deposito['depix_id']}")
            print(f"   💰 valor: R$ {deposito['amount_in_cents']/100:.2f}")
            print(f"   📊 status: {deposito['status']}")
            print(f"   🔗 blockchainTxID: {deposito['blockchainTxID']}")
            print(f"   💬 chat_id: {deposito['chatid']}")
            print(f"   📅 created_at: {format_timestamp(deposito['created_at'])}")
            print(f"   � notified: {deposito['notified']}")
            print(f"   🎯 depix_id: {deposito['depix_id']}")
            print(f"   📮 address: {deposito['address']}")
            print(f"   💸 send: {deposito['send']}")
            print(f"   💱 taxa: {deposito['taxa']}")
            print(f"   🪙 moeda: {deposito['moeda']}")
            print(f"   🌐 rede: {deposito['rede']}")
            
            # Verificações críticas
            critical_checks = []
            
            if not deposito['blockchainTxID']:
                critical_checks.append("❌ blockchainTxID está vazio - cron não processará")
            else:
                critical_checks.append("✅ blockchainTxID presente")
                
            if not deposito['chatid']:
                critical_checks.append("❌ chat_id está vazio - bot não saberá para quem enviar")
            else:
                critical_checks.append(f"✅ chat_id presente: {deposito['chatid']}")
                
            if deposito['status'] != 'awaiting_client_invoice':
                critical_checks.append(f"⚠️  status é '{deposito['status']}' - verificar se cron processará")
            else:
                critical_checks.append("✅ status correto para processamento")
                
            print(f"\n🔍 VERIFICAÇÕES CRÍTICAS:")
            for check in critical_checks:
                print(f"   {check}")
                
        else:
            print(f"❌ Depósito {depix_id} não encontrado no banco!")
            return
            
        # 2. Simular consulta do cron
        print(f"\n2️⃣ SIMULANDO CONSULTA DO CRON")
        print("-" * 50)
        
        cursor.execute("""
            SELECT depix_id, amount_in_cents, chatid, blockchainTxID, status, created_at
            FROM deposit 
            WHERE blockchainTxID IS NOT NULL 
            AND blockchainTxID != ''
            AND chatid = ?
            ORDER BY created_at DESC
        """, (chat_id,))
        
        depositos_cron = cursor.fetchall()
        
        print(f"🔍 Consulta do cron encontrou {len(depositos_cron)} depósito(s) para chat_id {chat_id}")
        
        if depositos_cron:
            print("📋 Depósitos que o cron processaria:")
            for i, dep in enumerate(depositos_cron, 1):
                valor_real = dep['amount_in_cents']/100 if dep['amount_in_cents'] else 0
                print(f"   {i}. {dep['depix_id']} - R$ {valor_real:.2f} - {dep['status']}")
                if dep['depix_id'] == depix_id:
                    print(f"      ✅ Este é o nosso depósito de teste!")
        else:
            print("⚠️  Nenhum depósito seria processado pelo cron!")
            
        # 3. Verificar outros depósitos similares
        print(f"\n3️⃣ VERIFICANDO OUTROS DEPÓSITOS PARA CONTEXTO")
        print("-" * 50)
        
        cursor.execute("""
            SELECT depix_id, amount_in_cents, status, chatid, blockchainTxID, created_at
            FROM deposit 
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        todos_depositos = cursor.fetchall()
        
        print("📋 Últimos 10 depósitos no banco:")
        for dep in todos_depositos:
            status_icon = "✅" if dep['blockchainTxID'] else "❌"
            chat_info = f"chat:{dep['chatid']}" if dep['chatid'] else "sem_chat"
            valor_real = dep['amount_in_cents']/100 if dep['amount_in_cents'] else 0
            print(f"   {status_icon} {dep['depix_id']} - R$ {valor_real:.2f} - {dep['status']} - {chat_info}")
            
        # 4. Diagnóstico final
        print(f"\n4️⃣ DIAGNÓSTICO E PRÓXIMOS PASSOS")
        print("-" * 50)
        
        if deposito:
            if deposito['blockchainTxID'] and deposito['chatid']:
                print("✅ DEPÓSITO ESTÁ PRONTO PARA PROCESSAMENTO!")
                print("📋 O que deveria acontecer:")
                print("   1. Cron roda e encontra este depósito")
                print("   2. Notifier é chamado para este chat_id")
                print("   3. Bot envia mensagem solicitando endereço Lightning")
                print("")
                print("🔧 Para forçar o processamento:")
                print(f"   - Acesse: https://useghost.squareweb.app/api/lightning_notifier.php?chat_id={chat_id}")
                print("   - Ou rode o cron manualmente quando o servidor voltar")
                
            else:
                print("❌ DEPÓSITO NÃO ESTÁ PRONTO!")
                missing = []
                if not deposito['blockchainTxID']:
                    missing.append("blockchainTxID")
                if not deposito['chatid']:
                    missing.append("chatid")
                print(f"   Campos faltando: {', '.join(missing)}")
                
        # 5. Criar comando SQL para atualizar se necessário
        if deposito and (not deposito['blockchainTxID'] or not deposito['chatid']):
            print(f"\n5️⃣ COMANDOS PARA CORREÇÃO")
            print("-" * 50)
            
            if not deposito['blockchainTxID']:
                print("📝 Para preencher blockchainTxID:")
                print(f"   UPDATE deposit SET blockchainTxID = 'manual_test_{int(datetime.now().timestamp())}' WHERE depix_id = '{depix_id}';")
                
            if not deposito['chatid']:
                print("📝 Para preencher chatid:")
                print(f"   UPDATE deposit SET chatid = '{chat_id}' WHERE depix_id = '{depix_id}';")
                
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Erro no SQLite: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
