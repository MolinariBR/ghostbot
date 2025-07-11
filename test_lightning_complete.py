#!/usr/bin/env python3
"""
Teste completo do fluxo Lightning Address com dados reais
Usuário: 7910260237
Lightning Address: bouncyflight79@walletofsatoshi.com
Depix ID: 0197f7083e627dfe8532dfb32d576171
"""
import requests
import json
import logging
import sqlite3
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lightning_test_complete.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_test_deposit():
    """Cria um depósito Lightning na base de dados para o teste"""
    try:
        db_path = "/home/mau/bot/ghostbackend/data/deposit.db"
        
        if not os.path.exists(db_path):
            logger.error(f"Base de dados não encontrada: {db_path}")
            return False
        
        logger.info("🔧 Configurando depósito de teste...")
        
        # Conectar à base de dados
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se o depósito já existe
        cursor.execute("SELECT id FROM deposit WHERE depix_id = ?", ('0197f7083e627dfe8532dfb32d576171',))
        existing = cursor.fetchone()
        
        if existing:
            logger.info("✅ Depósito já existe na base de dados")
        else:
            # Inserir o depósito
            insert_query = """
            INSERT INTO deposit (
                chatid, 
                amount_in_cents, 
                taxa, 
                moeda, 
                rede, 
                address, 
                send, 
                status, 
                depix_id,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                '7910260237',  # chat_id do usuário
                150000,        # R$ 1500,00 em centavos
                0.05,          # Taxa de 5%
                'BTC',         # Moeda
                '⚡ Lightning', # Rede
                'test_address', # Endereço placeholder
                1500,          # Valor em sats
                'confirmado',  # Status
                '0197f7083e627dfe8532dfb32d576171',  # depix_id
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            cursor.execute(insert_query, values)
            conn.commit()
            logger.info("✅ Depósito inserido com sucesso")
        
        # Verificar se foi inserido
        cursor.execute("""
            SELECT chatid, depix_id, rede, status, send, blockchainTxID 
            FROM deposit 
            WHERE depix_id = ?
        """, ('0197f7083e627dfe8532dfb32d576171',))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            logger.info(f"📋 Depósito encontrado:")
            logger.info(f"   Chat ID: {result[0]}")
            logger.info(f"   Depix ID: {result[1]}")
            logger.info(f"   Rede: {result[2]}")
            logger.info(f"   Status: {result[3]}")
            logger.info(f"   Valor: {result[4]} sats")
            logger.info(f"   BlockchainTxID: {result[5] or 'NULL'}")
            return True
        else:
            logger.error("❌ Falha ao verificar depósito")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro configurando depósito: {e}")
        return False

def test_lightning_endpoint():
    """Testa o endpoint Lightning Address com dados reais"""
    try:
        logger.info("🧪 TESTANDO ENDPOINT LIGHTNING ADDRESS")
        logger.info("=" * 60)
        
        url = "https://useghost.squareweb.app/api/process_lightning_address.php"
        
        # Dados do teste
        data = {
            'chat_id': '7910260237',
            'user_input': 'bouncyflight79@walletofsatoshi.com'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'GhostBot/1.0'
        }
        
        logger.info(f"🎯 URL: {url}")
        logger.info(f"📋 Chat ID: {data['chat_id']}")
        logger.info(f"⚡ Lightning Address: {data['user_input']}")
        
        logger.info("📡 Enviando requisição...")
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        logger.info(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_text = response.text
            logger.info(f"📝 Response Length: {len(response_text)} characters")
            
            # Verificar se há múltiplos JSONs concatenados
            if '}{' in response_text:
                logger.warning("⚠️ Resposta contém múltiplos JSONs concatenados")
                
                # Tentar extrair o JSON correto
                parts = response_text.split('}{')
                if len(parts) >= 2:
                    # Pegar o último JSON
                    last_json = '{' + parts[-1]
                    logger.info(f"🔍 Último JSON: {last_json}")
                    
                    try:
                        result = json.loads(last_json)
                        logger.info("✅ JSON decodificado com sucesso!")
                        logger.info(f"📋 Resultado: {json.dumps(result, indent=2)}")
                        
                        if result.get('success'):
                            logger.info("🎉 SUCESSO! Lightning Address processado!")
                            return True
                        else:
                            logger.warning(f"⚠️ Falha no processamento: {result.get('message', 'Erro desconhecido')}")
                            return False
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Erro decodificando JSON: {e}")
            
            # Tentar decodificar normalmente
            try:
                result = response.json()
                logger.info("✅ JSON decodificado normalmente!")
                logger.info(f"📋 Resultado: {json.dumps(result, indent=2)}")
                
                if result.get('success'):
                    logger.info("🎉 SUCESSO! Lightning Address processado!")
                    return True
                else:
                    logger.warning(f"⚠️ Falha no processamento: {result.get('message', 'Erro desconhecido')}")
                    return False
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro decodificando JSON: {e}")
                logger.info(f"📝 Raw response: {response_text[:500]}...")
                return False
        else:
            logger.error(f"❌ Erro HTTP: {response.status_code}")
            logger.info(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        return False

def verify_payment_result():
    """Verifica se o pagamento foi processado na base de dados"""
    try:
        logger.info("🔍 VERIFICANDO RESULTADO DO PAGAMENTO")
        logger.info("=" * 60)
        
        db_path = "/home/mau/bot/ghostbackend/data/deposit.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se o blockchainTxID foi preenchido
        cursor.execute("""
            SELECT chatid, depix_id, rede, status, send, blockchainTxID, created_at 
            FROM deposit 
            WHERE depix_id = ?
        """, ('0197f7083e627dfe8532dfb32d576171',))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            logger.info(f"📋 Estado final do depósito:")
            logger.info(f"   Chat ID: {result[0]}")
            logger.info(f"   Depix ID: {result[1]}")
            logger.info(f"   Rede: {result[2]}")
            logger.info(f"   Status: {result[3]}")
            logger.info(f"   Valor: {result[4]} sats")
            logger.info(f"   BlockchainTxID: {result[5] or 'NULL'}")
            logger.info(f"   Data: {result[6]}")
            
            if result[5]:  # blockchainTxID preenchido
                logger.info("✅ Pagamento processado com sucesso!")
                return True
            else:
                logger.info("⏳ Pagamento ainda em processamento...")
                return False
        else:
            logger.error("❌ Depósito não encontrado")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro verificando resultado: {e}")
        return False

def main():
    """Função principal do teste"""
    logger.info("🚀 INICIANDO TESTE COMPLETO DO LIGHTNING ADDRESS")
    logger.info("=" * 80)
    logger.info(f"👤 Usuário: 7910260237")
    logger.info(f"⚡ Lightning Address: bouncyflight79@walletofsatoshi.com")
    logger.info(f"🆔 Depix ID: 0197f7083e627dfe8532dfb32d576171")
    logger.info("=" * 80)
    
    # Passo 1: Configurar depósito
    if not setup_test_deposit():
        logger.error("❌ Falha na configuração do depósito. Abortando teste.")
        return False
    
    # Passo 2: Testar endpoint
    if not test_lightning_endpoint():
        logger.error("❌ Falha no teste do endpoint. Verificando estado...")
        verify_payment_result()
        return False
    
    # Passo 3: Verificar resultado
    if verify_payment_result():
        logger.info("🎉 TESTE COMPLETO REALIZADO COM SUCESSO!")
        return True
    else:
        logger.info("⏳ Teste executado, mas pagamento ainda em processamento...")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 80)
    if success:
        print("🎉 RESULTADO: SUCESSO COMPLETO!")
    else:
        print("⚠️ RESULTADO: SUCESSO PARCIAL - Verifique logs para detalhes")
    print("=" * 80)
