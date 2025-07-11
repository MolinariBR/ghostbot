#!/usr/bin/env python3
"""
Teste do Lightning Address com parâmetros corretos
"""
import requests
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lightning_with_correct_params():
    """
    Testa o endpoint com os parâmetros corretos
    """
    logger.info("🧪 TESTANDO LIGHTNING ADDRESS COM PARÂMETROS CORRETOS")
    
    url = "https://useghost.squareweb.app/api/process_lightning_address.php"
    
    # Dados corretos conforme o endpoint espera
    data = {
        'chat_id': '7910260237',  # Usuário real
        'user_input': 'bouncyflight79@walletofsatoshi.com'  # Lightning Address real
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
        
        # Tentar extrair o JSON correto da resposta
        response_text = response.text
        logger.info(f"Response Text Length: {len(response_text)}")
        
        # Se há dois JSONs concatenados, vamos tentar pegar o segundo
        if '}{' in response_text:
            logger.warning("⚠️ Resposta contém múltiplos JSONs concatenados")
            parts = response_text.split('}{')
            if len(parts) >= 2:
                # Reconstituir o segundo JSON
                second_json = '{' + parts[-1]
                logger.info(f"Segundo JSON: {second_json}")
                
                try:
                    result = json.loads(second_json)
                    logger.info(f"✅ JSON decodificado com sucesso: {json.dumps(result, indent=2)}")
                    return result.get('success', False)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Erro ao decodificar segundo JSON: {e}")
        
        # Tentar decodificar normalmente
        try:
            result = response.json()
            logger.info(f"✅ JSON decodificado: {json.dumps(result, indent=2)}")
            return result.get('success', False)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao decodificar JSON: {e}")
            logger.info(f"Raw response: {response_text[:500]}...")
            
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro na requisição: {e}")
        return False

def test_multiple_addresses():
    """
    Testa múltiplos Lightning Addresses
    """
    logger.info("=" * 60)
    logger.info("🚀 TESTANDO MÚLTIPLOS LIGHTNING ADDRESSES")
    
    addresses = [
        'bouncyflight79@walletofsatoshi.com',
        'test@getalby.com',
        'satoshi@ln.tips'
    ]
    
    for address in addresses:
        logger.info("=" * 40)
        logger.info(f"🧪 Testando: {address}")
        
        success = test_lightning_with_correct_params()
        logger.info(f"Resultado: {'✅ Sucesso' if success else '❌ Falha'}")

if __name__ == "__main__":
    test_multiple_addresses()
