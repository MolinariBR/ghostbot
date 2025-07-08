#!/usr/bin/env python3
"""
Teste completo do fluxo Lightning com logging detalhado
Registra todas as operações em fluxo.log para análise
"""
import requests
import json
import time
import logging
from datetime import datetime
import traceback

# Configurar logging detalhado
def setup_logging():
    """Configura logging detalhado para arquivo e console"""
    # Remover handlers existentes
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configurar formato detalhado
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo
    file_handler = logging.FileHandler('fluxo.log', mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Configurar logger root
    logging.root.setLevel(logging.DEBUG)
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)
    
    return logging.getLogger(__name__)

# Dados do teste
depix_id = "0197eae225117dfc85fe31ea03c518a4"
chat_id = "7910260237"
real_address = "bouncyflight79@walletofsatoshi.com"

def log_request(method, url, data=None, headers=None, response=None, error=None):
    """Log detalhado de requisições HTTP"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"🌐 HTTP {method.upper()} Request")
    logger.info(f"   URL: {url}")
    
    if headers:
        logger.debug(f"   Headers: {json.dumps(headers, indent=2)}")
    
    if data:
        logger.debug(f"   Data: {json.dumps(data, indent=2)}")
    
    if response:
        logger.info(f"   Response Status: {response.status_code}")
        logger.debug(f"   Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            logger.debug(f"   Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            logger.debug(f"   Response Text: {response.text[:500]}...")
    
    if error:
        logger.error(f"   Error: {error}")
        logger.debug(f"   Traceback: {traceback.format_exc()}")

def test_complete_lightning_flow():
    """Teste completo do fluxo Lightning com logging detalhado"""
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("🚀 INICIANDO TESTE COMPLETO DO FLUXO LIGHTNING")
    logger.info("=" * 80)
    logger.info(f"🎯 Depix ID: {depix_id}")
    logger.info(f"💬 Chat ID: {chat_id}")
    logger.info(f"📮 Endereço Lightning: {real_address}")
    logger.info(f"💰 Valor: R$ 5,00 (806 sats)")
    logger.info(f"⏰ Iniciado em: {datetime.now().isoformat()}")
    
    results = {
        "inicio": datetime.now().isoformat(),
        "etapas": {},
        "erros": [],
        "sucessos": []
    }
    
    # 1. Verificar status do depósito
    logger.info("\n" + "=" * 60)
    logger.info("1️⃣ VERIFICANDO STATUS DO DEPÓSITO")
    logger.info("=" * 60)
    
    try:
        url_check = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
        logger.info(f"🔍 Consultando depósito: {depix_id}")
        
        start_time = time.time()
        resp = requests.get(url_check, timeout=15)
        end_time = time.time()
        
        log_request("GET", url_check, response=resp)
        logger.info(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('deposits'):
                deposit = data['deposits'][0]
                logger.info(f"✅ Depósito encontrado")
                logger.info(f"   Status: {deposit.get('status')}")
                logger.info(f"   BlockchainTxID: {deposit.get('blockchainTxID')}")
                logger.info(f"   Chat ID: {deposit.get('chatid')}")
                logger.info(f"   Valor: R$ {deposit.get('amount_in_cents', 0)/100:.2f}")
                
                results["etapas"]["consulta_deposito"] = {
                    "sucesso": True,
                    "status": deposit.get('status'),
                    "blockchain_txid": deposit.get('blockchainTxID'),
                    "tempo_resposta": end_time - start_time
                }
                results["sucessos"].append("Consulta de depósito")
            else:
                logger.warning("⚠️  Depósito não encontrado na resposta")
                results["erros"].append("Depósito não encontrado")
        else:
            logger.error(f"❌ Erro HTTP {resp.status_code}")
            results["erros"].append(f"HTTP {resp.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Erro na consulta do depósito: {e}")
        log_request("GET", url_check, error=e)
        results["erros"].append(f"Consulta depósito: {e}")
    
    # 2. Simular confirmação PIX
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣ SIMULANDO CONFIRMAÇÃO PIX")
    logger.info("=" * 60)
    
    webhook_data = {
        "event": "payment_confirmed",
        "transaction_id": depix_id,
        "status": "confirmed",
        "amount": 500,
        "currency": "BRL",
        "payment_method": "PIX",
        "confirmed_at": int(time.time()),
        "blockchain_txid": f"pix_confirmed_{int(time.time())}"
    }
    
    logger.info("📤 Dados do webhook PIX:")
    logger.info(json.dumps(webhook_data, indent=2))
    
    try:
        webhook_url = "https://useghost.squareweb.app/depix/webhook.php"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PixWebhook/1.0'
        }
        
        logger.info(f"📡 Enviando webhook para: {webhook_url}")
        start_time = time.time()
        resp_webhook = requests.post(webhook_url, json=webhook_data, headers=headers, timeout=20)
        end_time = time.time()
        
        log_request("POST", webhook_url, data=webhook_data, headers=headers, response=resp_webhook)
        logger.info(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
        
        if resp_webhook.status_code == 200:
            logger.info("✅ Webhook PIX enviado com sucesso")
            results["etapas"]["webhook_pix"] = {
                "sucesso": True,
                "tempo_resposta": end_time - start_time
            }
            results["sucessos"].append("Webhook PIX")
        else:
            logger.error(f"❌ Erro no webhook: {resp_webhook.status_code}")
            results["erros"].append(f"Webhook PIX: HTTP {resp_webhook.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook PIX: {e}")
        log_request("POST", webhook_url, data=webhook_data, headers=headers, error=e)
        results["erros"].append(f"Webhook PIX: {e}")
    
    # 3. Aguardar processamento
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣ AGUARDANDO PROCESSAMENTO")
    logger.info("=" * 60)
    
    logger.info("⏳ Aguardando 5 segundos para processamento...")
    time.sleep(5)
    
    # 4. Testar cron Lightning
    logger.info("\n" + "=" * 60)
    logger.info("4️⃣ TESTANDO CRON LIGHTNING")
    logger.info("=" * 60)
    
    try:
        cron_url = f"https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php?chat_id={chat_id}"
        logger.info(f"🔄 Executando cron: {cron_url}")
        
        start_time = time.time()
        resp_cron = requests.get(cron_url, timeout=20)
        end_time = time.time()
        
        log_request("GET", cron_url, response=resp_cron)
        logger.info(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
        
        if resp_cron.status_code == 200:
            logger.info("✅ Cron Lightning respondeu")
            try:
                cron_data = resp_cron.json()
                results_count = len(cron_data.get('results', []))
                logger.info(f"📊 Depósitos encontrados: {results_count}")
                
                for i, result in enumerate(cron_data.get('results', [])):
                    logger.info(f"   Depósito {i+1}: {result.get('depix_id')} - {result.get('status')}")
                    if result.get('depix_id') == depix_id:
                        logger.info(f"   ✅ Nosso depósito encontrado!")
                
                results["etapas"]["cron_lightning"] = {
                    "sucesso": True,
                    "depositos_encontrados": results_count,
                    "tempo_resposta": end_time - start_time
                }
                results["sucessos"].append("Cron Lightning")
                
            except Exception as e:
                logger.warning(f"⚠️  Erro ao processar JSON do cron: {e}")
                logger.info(f"Resposta bruta: {resp_cron.text[:200]}...")
                
        else:
            logger.error(f"❌ Erro no cron: {resp_cron.status_code}")
            results["erros"].append(f"Cron Lightning: HTTP {resp_cron.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Erro no cron Lightning: {e}")
        log_request("GET", cron_url, error=e)
        results["erros"].append(f"Cron Lightning: {e}")
    
    # 5. Testar notifier
    logger.info("\n" + "=" * 60)
    logger.info("5️⃣ TESTANDO NOTIFIER LIGHTNING")
    logger.info("=" * 60)
    
    try:
        notifier_url = f"https://useghost.squareweb.app/api/lightning_notifier.php?chat_id={chat_id}"
        logger.info(f"📢 Executando notifier: {notifier_url}")
        
        start_time = time.time()
        resp_notifier = requests.get(notifier_url, timeout=15)
        end_time = time.time()
        
        log_request("GET", notifier_url, response=resp_notifier)
        logger.info(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
        
        if resp_notifier.status_code == 200:
            logger.info("✅ Notifier Lightning respondeu")
            try:
                notifier_data = resp_notifier.json()
                notified_count = notifier_data.get('notified', 0)
                logger.info(f"📊 Notificações enviadas: {notified_count}")
                
                results["etapas"]["notifier_lightning"] = {
                    "sucesso": True,
                    "notificacoes_enviadas": notified_count,
                    "tempo_resposta": end_time - start_time
                }
                results["sucessos"].append("Notifier Lightning")
                
            except Exception as e:
                logger.warning(f"⚠️  Erro ao processar JSON do notifier: {e}")
                
        else:
            logger.error(f"❌ Erro no notifier: {resp_notifier.status_code}")
            results["erros"].append(f"Notifier Lightning: HTTP {resp_notifier.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Erro no notifier Lightning: {e}")
        log_request("GET", notifier_url, error=e)
        results["erros"].append(f"Notifier Lightning: {e}")
    
    # 6. Simular processamento de endereço Lightning
    logger.info("\n" + "=" * 60)
    logger.info("6️⃣ SIMULANDO PROCESSAMENTO DE ENDEREÇO LIGHTNING")
    logger.info("=" * 60)
    
    try:
        save_address_url = "https://useghost.squareweb.app/api/save_lightning_address.php"
        address_data = {
            "depix_id": depix_id,
            "lightning_address": real_address,
            "address_type": "lightning_address"
        }
        
        logger.info(f"📮 Salvando endereço Lightning: {real_address}")
        logger.info(f"🎯 Para depósito: {depix_id}")
        
        headers = {'Content-Type': 'application/json'}
        start_time = time.time()
        resp_save = requests.post(save_address_url, json=address_data, headers=headers, timeout=15)
        end_time = time.time()
        
        log_request("POST", save_address_url, data=address_data, headers=headers, response=resp_save)
        logger.info(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
        
        if resp_save.status_code == 200:
            logger.info("✅ Endereço Lightning salvo")
            results["etapas"]["save_address"] = {
                "sucesso": True,
                "endereco": real_address,
                "tempo_resposta": end_time - start_time
            }
            results["sucessos"].append("Salvar endereço Lightning")
        else:
            logger.error(f"❌ Erro ao salvar endereço: {resp_save.status_code}")
            results["erros"].append(f"Salvar endereço: HTTP {resp_save.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao salvar endereço Lightning: {e}")
        log_request("POST", save_address_url, data=address_data, headers=headers, error=e)
        results["erros"].append(f"Salvar endereço: {e}")
    
    # 7. Verificação final
    logger.info("\n" + "=" * 60)
    logger.info("7️⃣ VERIFICAÇÃO FINAL DO STATUS")
    logger.info("=" * 60)
    
    try:
        logger.info("⏳ Aguardando 3 segundos...")
        time.sleep(3)
        
        start_time = time.time()
        resp_final = requests.get(url_check, timeout=15)
        end_time = time.time()
        
        log_request("GET", url_check, response=resp_final)
        
        if resp_final.status_code == 200:
            data_final = resp_final.json()
            if data_final.get('deposits'):
                deposit_final = data_final['deposits'][0]
                logger.info("✅ Status final do depósito:")
                logger.info(f"   Status: {deposit_final.get('status')}")
                logger.info(f"   BlockchainTxID: {deposit_final.get('blockchainTxID')}")
                logger.info(f"   Lightning Address: {deposit_final.get('lightning_address', 'N/A')}")
                logger.info(f"   Notified: {deposit_final.get('notified', 'N/A')}")
                
                results["etapas"]["verificacao_final"] = {
                    "sucesso": True,
                    "status_final": deposit_final.get('status'),
                    "lightning_address": deposit_final.get('lightning_address'),
                    "tempo_resposta": end_time - start_time
                }
                results["sucessos"].append("Verificação final")
            else:
                logger.warning("⚠️  Depósito não encontrado na verificação final")
                
    except Exception as e:
        logger.error(f"❌ Erro na verificação final: {e}")
        results["erros"].append(f"Verificação final: {e}")
    
    # 8. Resumo final
    results["fim"] = datetime.now().isoformat()
    results["duracao_total"] = (datetime.fromisoformat(results["fim"]) - 
                               datetime.fromisoformat(results["inicio"])).total_seconds()
    
    logger.info("\n" + "=" * 80)
    logger.info("📊 RESUMO FINAL DO TESTE")
    logger.info("=" * 80)
    logger.info(f"⏰ Duração total: {results['duracao_total']:.2f}s")
    logger.info(f"✅ Sucessos: {len(results['sucessos'])}")
    logger.info(f"❌ Erros: {len(results['erros'])}")
    
    for sucesso in results["sucessos"]:
        logger.info(f"   ✅ {sucesso}")
    
    for erro in results["erros"]:
        logger.info(f"   ❌ {erro}")
    
    logger.info("\n📋 Etapas executadas:")
    for etapa, dados in results["etapas"].items():
        status = "✅" if dados.get("sucesso") else "❌"
        tempo = dados.get("tempo_resposta", 0)
        logger.info(f"   {status} {etapa}: {tempo:.2f}s")
    
    # Salvar resumo detalhado
    logger.info(f"\n💾 Resumo completo salvo em fluxo.log")
    logger.info(f"📊 Total de linhas de log: aproximadamente {len(results)*10}")
    
    return results

def main():
    """Função principal"""
    logger = setup_logging()
    
    logger.info("🔧 Sistema de logging configurado")
    logger.info("📝 Logs serão salvos em: fluxo.log")
    logger.info("📊 Nível de debug: DETALHADO")
    
    try:
        results = test_complete_lightning_flow()
        
        if len(results["erros"]) == 0:
            logger.info("\n🎉 TESTE CONCLUÍDO COM SUCESSO TOTAL!")
        elif len(results["sucessos"]) > len(results["erros"]):
            logger.info("\n⚠️  TESTE CONCLUÍDO COM SUCESSOS PARCIAIS")
        else:
            logger.info("\n❌ TESTE CONCLUÍDO COM MÚLTIPLOS ERROS")
        
        logger.info(f"\n📁 Verifique o arquivo fluxo.log para detalhes completos")
        
    except Exception as e:
        logger.error(f"❌ Erro crítico no teste: {e}")
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main()
