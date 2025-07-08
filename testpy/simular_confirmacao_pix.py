#!/usr/bin/env python3
"""
Simulador de confirmação PIX - dispara fluxo Lightning para depósito real
Simula webhook de confirmação do PIX para continuar o fluxo Lightning
Gera log detalhado em fluxo.log para análise completa do fluxo
"""
import requests
import json
import time
import logging
from datetime import datetime
import os

# Dados do depósito real criado
depix_id = "0197eae225117dfc85fe31ea03c518a4"
chat_id = "7910260237"

# Configurar logging detalhado
def setup_logging():
    """Configura logging detalhado para arquivo fluxo.log"""
    log_file = os.path.join(os.path.dirname(__file__), 'fluxo.log')
    
    # Configurar formatação detalhada
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configurar logger principal
    logger = logging.getLogger('fluxo_lightning')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_request_response(logger, step, url, method, data=None, headers=None, response=None, error=None):
    """Registra detalhes completos de request/response"""
    logger.info(f"🔗 {step} - {method} {url}")
    
    if headers:
        logger.debug(f"📤 Headers: {json.dumps(dict(headers), indent=2)}")
    
    if data:
        logger.debug(f"📤 Request Data: {json.dumps(data, indent=2)}")
    
    if response:
        logger.info(f"📊 Status: {response.status_code}")
        logger.debug(f"📥 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            logger.debug(f"📥 Response JSON: {json.dumps(response_data, indent=2)}")
        except:
            if response.text:
                logger.debug(f"📥 Response Text: {response.text}")
    
    if error:
        logger.error(f"❌ Error: {str(error)}")
        logger.debug(f"❌ Error Details: {type(error).__name__}: {str(error)}")

def check_deposit_status(logger, step_name):
    """Verifica status do depósito com logging detalhado"""
    logger.info(f"🔍 {step_name}")
    logger.info("-" * 50)
    
    url_check = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
    
    try:
        start_time = time.time()
        resp = requests.get(url_check, timeout=10)
        end_time = time.time()
        
        log_request_response(logger, step_name, url_check, "GET", response=resp)
        logger.debug(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('deposits'):
                deposit = data['deposits'][0]
                logger.info(f"📊 Status: {deposit.get('status')}")
                logger.info(f"🔗 BlockchainTxID: {deposit.get('blockchainTxID')}")
                logger.info(f"💬 Chat ID: {deposit.get('chatid')}")
                logger.info(f"💰 Valor: R$ {deposit.get('amount', 0)/100:.2f}")
                logger.info(f"🔔 Notified: {deposit.get('notified', 'N/A')}")
                logger.debug(f"📋 Dados completos: {json.dumps(deposit, indent=2)}")
                return deposit
            else:
                logger.warning("❌ Depósito não encontrado")
                return None
        else:
            logger.error(f"❌ Erro ao consultar: {resp.status_code}")
            return None
            
    except Exception as e:
        log_request_response(logger, step_name, url_check, "GET", error=e)
        return None

def main():
    """Executa simulação completa do fluxo Lightning com logging detalhado"""
    logger = setup_logging()
    
    logger.info("🚀 INICIANDO SIMULAÇÃO DE CONFIRMAÇÃO PIX PARA FLUXO LIGHTNING")
    logger.info("=" * 70)
    logger.info(f"📋 Depix ID: {depix_id}")
    logger.info(f"💬 Chat ID: {chat_id}")
    logger.info(f"� Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    try:
        # 1. Verificar status inicial
        logger.info("")
        deposit = check_deposit_status(logger, "ETAPA 1: Verificação Status Inicial")
        
        if not deposit:
            logger.error("❌ ERRO: Depósito não encontrado - abortando simulação")
            return
        
        # 2. Simular confirmação PIX (webhook do sistema bancário)
        logger.info("")
        logger.info("� ETAPA 2: Simulação de Webhook PIX (Confirmação)")
        logger.info("-" * 50)
        
        # Tentar múltiplas URLs de webhook
        webhook_urls = [
            "https://useghost.squareweb.app/depix/webhook.php",
            "https://useghost.squareweb.app/api/bot_deposit.php",
            "https://useghost.squareweb.app/api/confirm_deposit.php"
        ]
        
        webhook_data = {
            "event": "payment_confirmed",
            "transaction_id": depix_id,
            "depix_id": depix_id,
            "status": "confirmed",
            "amount": 500,  # R$ 5,00 em centavos
            "currency": "BRL",
            "payment_method": "PIX",
            "confirmed_at": int(time.time()),
            "blockchain_txid": f"pix_confirmed_{int(time.time())}"
        }
        
        webhook_success = False
        for webhook_url in webhook_urls:
            logger.info(f"🔗 Tentando webhook: {webhook_url}")
            
            start_time = time.time()
            try:
                webhook_response = requests.post(
                    webhook_url, 
                    json=webhook_data,
                    headers={'Content-Type': 'application/json', 'User-Agent': 'PixWebhook/1.0'},
                    timeout=15
                )
                end_time = time.time()
                
                log_request_response(logger, f"Webhook PIX ({webhook_url})", webhook_url, "POST", 
                                   data=webhook_data, response=webhook_response)
                logger.debug(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
                
                if webhook_response.status_code == 200:
                    logger.info("✅ Webhook PIX enviado com sucesso")
                    webhook_success = True
                    break
                else:
                    logger.warning(f"⚠️  Webhook PIX retornou status: {webhook_response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"⏰ TIMEOUT: Webhook PIX demorou mais de 15 segundos")
            except Exception as e:
                log_request_response(logger, f"Webhook PIX ({webhook_url})", webhook_url, "POST", 
                                   data=webhook_data, error=e)
        
        if not webhook_success:
            logger.warning("⚠️  Nenhum webhook teve sucesso - continuando com o fluxo")
        
        # 3. Aguardar processamento
        logger.info("")
        logger.info("⏳ ETAPA 3: Aguardando Processamento (5 segundos)")
        logger.info("-" * 50)
        time.sleep(5)
        
        # 4. Verificar status após confirmação
        logger.info("")
        deposit_after = check_deposit_status(logger, "ETAPA 4: Status Após Confirmação PIX")
        
        # 5. Simular cron Lightning (processamento do pagamento)
        logger.info("")
        logger.info("🔗 ETAPA 5: Simulação Cron Lightning (Processamento)")
        logger.info("-" * 50)
        
        cron_urls = [
            f"https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php?chat_id={chat_id}",
            "https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php"
        ]
        
        cron_success = False
        for cron_url in cron_urls:
            logger.info(f"🔗 Tentando cron: {cron_url}")
            
            start_time = time.time()
            try:
                cron_response = requests.get(cron_url, timeout=30)
                end_time = time.time()
                
                log_request_response(logger, f"Cron Lightning ({cron_url})", cron_url, "GET", response=cron_response)
                logger.debug(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
                
                if cron_response.status_code == 200:
                    logger.info("✅ Cron Lightning executado com sucesso")
                    try:
                        cron_data = cron_response.json()
                        if 'results' in cron_data:
                            results = cron_data.get('results', [])
                            logger.info(f"📊 Depósitos processados: {len(results)}")
                            
                            # Verificar se nosso depósito foi processado
                            for result in results:
                                if result.get('depix_id') == depix_id:
                                    logger.info(f"🎯 Nosso depósito {depix_id} foi encontrado e processado!")
                                    break
                        
                        if 'errors' in cron_data and cron_data['errors']:
                            logger.warning(f"⚠️  Erros encontrados: {len(cron_data.get('errors', []))}")
                            for error in cron_data.get('errors', []):
                                logger.warning(f"   • {error}")
                    except:
                        pass
                    cron_success = True
                    break
                else:
                    logger.warning(f"⚠️  Cron Lightning retornou status: {cron_response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"⏰ TIMEOUT: Cron Lightning demorou mais de 30 segundos")
            except Exception as e:
                log_request_response(logger, f"Cron Lightning ({cron_url})", cron_url, "GET", error=e)
        
        if not cron_success:
            logger.warning("⚠️  Nenhum cron teve sucesso - tentando notifier diretamente")
        
        # 6. Simular notifier Lightning
        logger.info("")
        logger.info("🔗 ETAPA 6: Simulação Notifier Lightning")
        logger.info("-" * 50)
        
        notifier_url = f"https://useghost.squareweb.app/api/lightning_notifier.php?chat_id={chat_id}"
        
        start_time = time.time()
        try:
            notifier_response = requests.get(notifier_url, timeout=15)
            end_time = time.time()
            
            log_request_response(logger, "Notifier Lightning", notifier_url, "GET", response=notifier_response)
            logger.debug(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
            
            if notifier_response.status_code == 200:
                logger.info("✅ Notifier Lightning executado com sucesso")
            else:
                logger.warning(f"⚠️  Notifier Lightning retornou status: {notifier_response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("⏰ TIMEOUT: Notifier Lightning demorou mais de 15 segundos")
        except Exception as e:
            log_request_response(logger, "Notifier Lightning", notifier_url, "GET", error=e)
        
        # 7. Aguardar processamento final
        logger.info("")
        logger.info("⏳ ETAPA 7: Aguardando Processamento Final (10 segundos)")
        logger.info("-" * 50)
        time.sleep(10)
        
        # 8. Verificar status final
        logger.info("")
        deposit_final = check_deposit_status(logger, "ETAPA 8: Status Final do Depósito")
        
        # 9. Análise dos resultados
        logger.info("")
        logger.info("📊 ANÁLISE DOS RESULTADOS")
        logger.info("=" * 70)
        
        if deposit_final:
            status_final = deposit_final.get('status', 'unknown')
            notified = deposit_final.get('notified', 'N/A')
            blockchain_txid = deposit_final.get('blockchainTxID')
            
            logger.info(f"� Status Final: {status_final}")
            logger.info(f"🔔 Notificado: {notified}")
            logger.info(f"🔗 BlockchainTxID: {blockchain_txid}")
            
            if status_final == 'LIGHTNING_PAID':
                logger.info("🎉 SUCESSO: Pagamento Lightning realizado com sucesso!")
            elif status_final == 'CONFIRMADO':
                logger.warning("⚠️  PIX confirmado mas Lightning ainda não processado")
            elif status_final == 'PENDING':
                logger.info("⏳ Status ainda pendente - depósito aguardando processamento")
            else:
                logger.warning(f"⚠️  Status inesperado: {status_final}")
                
            if notified == '1':
                logger.info("📢 Usuário foi notificado no Telegram")
            else:
                logger.warning("📢 Usuário ainda não foi notificado")
        else:
            logger.error("❌ ERRO: Não foi possível verificar status final")
        
        # 10. Instruções finais
        logger.info("")
        logger.info("📱 PRÓXIMOS PASSOS")
        logger.info("-" * 50)
        logger.info(f"1. Verifique o Telegram no chat {chat_id}")
        logger.info("2. Procure por mensagem solicitando endereço Lightning")
        logger.info("3. Se recebeu a mensagem, envie um endereço Lightning válido")
        logger.info("4. Aguarde a confirmação do pagamento")
        
        logger.info("")
        logger.info("🏁 SIMULAÇÃO CONCLUÍDA")
        logger.info(f"� Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        logger.info(f"📄 Log detalhado salvo em: {os.path.join(os.path.dirname(__file__), 'fluxo.log')}")
        
    except Exception as e:
        logger.error(f"❌ ERRO GERAL NA SIMULAÇÃO: {str(e)}")
        logger.debug(f"❌ Detalhes do erro: {type(e).__name__}: {str(e)}")
        raise

if __name__ == "__main__":
    main()
