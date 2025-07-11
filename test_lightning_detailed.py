#!/usr/bin/env python3
"""
Teste detalhado do Lightning Address - Captura logs completos
"""
import requests
import json
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lightning_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_lightning_address_detailed(lightning_address, amount_sats=1000):
    """
    Teste detalhado do Lightning Address com logs completos
    """
    logger.info(f"🧪 INICIANDO TESTE DETALHADO")
    logger.info(f"Lightning Address: {lightning_address}")
    logger.info(f"Amount: {amount_sats} sats")
    
    # 1. Testar conectividade básica
    logger.info("1️⃣ Testando conectividade básica...")
    try:
        response = requests.get("https://useghost.squareweb.app/api/test_connection.php", timeout=10)
        logger.info(f"Status conectividade: {response.status_code}")
        if response.status_code == 200:
            logger.info(f"Resposta: {response.text}")
    except Exception as e:
        logger.error(f"Erro conectividade: {e}")
    
    # 2. Testar endpoint Lightning Address
    logger.info("2️⃣ Testando endpoint Lightning Address...")
    url = "https://useghost.squareweb.app/api/process_lightning_address.php"
    
    data = {
        'lightning_address': lightning_address,
        'amount_sats': amount_sats,
        'user_id': 123456789,  # ID de teste
        'test_mode': True
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'GhostBot/1.0'
    }
    
    logger.info(f"URL: {url}")
    logger.info(f"Data: {json.dumps(data, indent=2)}")
    logger.info(f"Headers: {json.dumps(headers, indent=2)}")
    
    try:
        logger.info("📡 Enviando requisição...")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        logger.info(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                logger.info(f"JSON Response: {json.dumps(json_response, indent=2)}")
                
                if json_response.get('status') == 'success':
                    logger.info("✅ Sucesso na resposta!")
                    return True
                else:
                    logger.error(f"❌ Erro na resposta: {json_response.get('message', 'Sem mensagem')}")
                    return False
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro ao decodificar JSON: {e}")
                return False
        else:
            logger.error(f"❌ Status code não é 200: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout na requisição")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        return False

def test_voltz_balance():
    """
    Testar saldo do Voltz
    """
    logger.info("3️⃣ Testando saldo Voltz...")
    try:
        response = requests.get("https://useghost.squareweb.app/test_voltz_balance.php", timeout=10)
        logger.info(f"Status saldo: {response.status_code}")
        logger.info(f"Resposta saldo: {response.text}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao testar saldo: {e}")
        return False

def test_lightning_resolver():
    """
    Testar resolver Lightning Address
    """
    logger.info("4️⃣ Testando resolver Lightning Address...")
    test_address = "test@getalby.com"
    
    try:
        # Testar resolução direta
        parts = test_address.split('@')
        if len(parts) == 2:
            domain = parts[1]
            username = parts[0]
            
            wellknown_url = f"https://{domain}/.well-known/lnurlp/{username}"
            logger.info(f"URL bem-conhecida: {wellknown_url}")
            
            response = requests.get(wellknown_url, timeout=10)
            logger.info(f"Status resolver: {response.status_code}")
            logger.info(f"Resposta resolver: {response.text}")
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    logger.info(f"JSON resolver: {json.dumps(json_data, indent=2)}")
                    return True
                except:
                    logger.error("❌ Erro ao decodificar JSON do resolver")
                    return False
        
        return False
        
    except Exception as e:
        logger.error(f"Erro ao testar resolver: {e}")
        return False

def main():
    """
    Função principal de teste
    """
    logger.info("🚀 INICIANDO DIAGNÓSTICO COMPLETO")
    logger.info("=" * 60)
    
    # Lista de Lightning Addresses para testar
    test_addresses = [
        "test@getalby.com",
        "satoshi@ln.tips",
        "bitcoin@ln.tips"
    ]
    
    # Testar componentes individuais
    voltz_ok = test_voltz_balance()
    resolver_ok = test_lightning_resolver()
    
    logger.info(f"Voltz OK: {voltz_ok}")
    logger.info(f"Resolver OK: {resolver_ok}")
    
    # Testar cada Lightning Address
    for address in test_addresses:
        logger.info("=" * 60)
        logger.info(f"🧪 Testando: {address}")
        
        success = test_lightning_address_detailed(address, 1000)
        
        logger.info(f"Resultado para {address}: {'✅ Sucesso' if success else '❌ Falha'}")
        
        time.sleep(2)  # Aguardar entre testes
    
    logger.info("=" * 60)
    logger.info("🏁 DIAGNÓSTICO COMPLETO FINALIZADO")
    logger.info("Verifique o arquivo lightning_debug.log para detalhes completos")

if __name__ == "__main__":
    main()
