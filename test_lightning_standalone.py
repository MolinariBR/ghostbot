#!/usr/bin/env python3
"""
Teste do Lightning Address sem dependência da base de dados
"""
import requests
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lightning_standalone():
    """
    Testa o endpoint sem depender da base de dados
    """
    logger.info("🧪 TESTANDO LIGHTNING ADDRESS STANDALONE")
    
    url = "https://useghost.squareweb.app/api/process_lightning_address.php"
    
    # Dados com amount_sats incluído
    data = {
        'chat_id': '123456789',
        'user_input': 'test@getalby.com',
        'amount_sats': 1000
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'GhostBot/1.0'
    }
    
    try:
        logger.info(f"URL: {url}")
        logger.info(f"Data: {json.dumps(data, indent=2)}")
        logger.info("📡 Enviando requisição...")
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        
        response_text = response.text
        logger.info(f"Response Text: {response_text}")
        
        # Tentar lidar com resposta JSON concatenada
        if '}{' in response_text:
            logger.warning("⚠️ Resposta contém múltiplos JSONs concatenados")
            # Pegar o último JSON (que deve ser o nosso)
            parts = response_text.split('}{')
            if len(parts) >= 2:
                last_json = '{' + parts[-1]
                logger.info(f"Último JSON: {last_json}")
                
                try:
                    result = json.loads(last_json)
                    logger.info(f"✅ JSON decodificado: {json.dumps(result, indent=2)}")
                    
                    if result.get('success'):
                        logger.info("🎉 SUCESSO! Lightning Address processado sem base de dados!")
                        return True
                    else:
                        logger.error(f"❌ Erro: {result.get('message')}")
                        return False
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Erro ao decodificar JSON: {e}")
        
        # Tentar decodificar normalmente
        try:
            result = response.json()
            logger.info(f"✅ JSON Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                logger.info("🎉 SUCESSO! Lightning Address processado sem base de dados!")
                return True
            else:
                logger.error(f"❌ Erro: {result.get('message')}")
                return False
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao decodificar JSON: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro na requisição: {e}")
        return False

def test_bolt11_standalone():
    """
    Testa BOLT11 standalone
    """
    logger.info("🧪 TESTANDO BOLT11 STANDALONE")
    
    url = "https://useghost.squareweb.app/api/process_lightning_address.php"
    
    # BOLT11 de exemplo (pode estar expirado, mas serve para teste)
    bolt11_example = "lnbc1500n1pjg7mqpp5w4k8zrppq5xrqsqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
    
    data = {
        'chat_id': '123456789',
        'user_input': bolt11_example,
        'amount_sats': 1000
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'GhostBot/1.0'
    }
    
    try:
        logger.info(f"URL: {url}")
        logger.info(f"Data: {json.dumps(data, indent=2)}")
        logger.info("📡 Enviando requisição...")
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Text: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 TESTANDO LIGHTNING SEM BASE DE DADOS")
    logger.info("=" * 60)
    
    # Teste 1: Lightning Address
    success1 = test_lightning_standalone()
    logger.info(f"Resultado Lightning Address: {'✅ Sucesso' if success1 else '❌ Falha'}")
    
    print()
    
    # Teste 2: BOLT11 (comentado por enquanto)
    # success2 = test_bolt11_standalone()
    # logger.info(f"Resultado BOLT11: {'✅ Sucesso' if success2 else '❌ Falha'}")
    
    logger.info("=" * 60)
    logger.info("🏁 TESTES CONCLUÍDOS")
