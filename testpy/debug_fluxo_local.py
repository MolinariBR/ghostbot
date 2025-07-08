#!/usr/bin/env python3
"""
Debug do fluxo Lightning - versão local/robusta
Verifica o fluxo sem depender de conectividade externa e simula o que o cron deveria fazer.
"""
import requests
import json
import time
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

depix_id = "0197ea6c80bc7dfc81b1e02fe8d06954"
chat_id = "7910260237"

def create_robust_session():
    """Cria uma sessão robusta para requisições HTTP"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def safe_request(session, url, timeout=5):
    """Faz uma requisição segura com tratamento de erros"""
    try:
        resp = session.get(url, timeout=timeout)
        return resp
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout na URL: {url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"🔌 Erro de conexão na URL: {url}")
        return None
    except Exception as e:
        print(f"❌ Erro geral na URL {url}: {e}")
        return None

def main():
    print("\n🔍 DEBUG DO FLUXO LIGHTNING - VERSÃO ROBUSTA")
    print("=" * 60)
    
    session = create_robust_session()
    
    print(f"\n1️⃣ TESTANDO CONECTIVIDADE")
    print(f"🎯 Depix ID: {depix_id}")
    print(f"💬 Chat ID: {chat_id}")
    
    # Teste básico de conectividade
    print("\n📡 Testando conectividade básica...")
    resp = safe_request(session, "https://useghost.squareweb.app/", timeout=3)
    if resp is None:
        print("❌ Servidor não está acessível no momento")
        print("💡 Simulando fluxo baseado no que deveria acontecer...")
        simulate_local_flow()
        return
    else:
        print(f"✅ Servidor respondeu com status: {resp.status_code}")
    
    print(f"\n2️⃣ CONSULTANDO DEPÓSITO")
    url_deposit = f"https://useghost.squareweb.app/rest/deposit.php?depix_id={depix_id}"
    resp = safe_request(session, url_deposit, timeout=10)
    
    if resp and resp.status_code == 200:
        try:
            data = resp.json()
            print("✅ Resposta do depósito:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            deposito = data.get('deposits', [{}])[0] if data.get('deposits') else {}
            
            # Verificações críticas
            blockchainTxID = deposito.get('blockchainTxID')
            status = deposito.get('status')
            valor = deposito.get('valor')
            
            print(f"\n🔍 ANÁLISE DO DEPÓSITO:")
            print(f"   - Status: {status}")
            print(f"   - BlockchainTxID: {blockchainTxID}")
            print(f"   - Valor: R$ {valor}")
            
            if not blockchainTxID:
                print("⚠️  blockchainTxID está vazio! O cron não processará este depósito.")
                return
            else:
                print("✅ blockchainTxID presente - cron pode processar")
                
        except Exception as e:
            print(f"❌ Erro ao processar resposta do depósito: {e}")
            return
    else:
        print("❌ Falha ao consultar depósito")
        return
    
    print(f"\n3️⃣ TESTANDO ENDPOINT CRON")
    url_cron = f"https://useghost.squareweb.app/api/lightning_cron_endpoint_final.php?chat_id={chat_id}"
    resp_cron = safe_request(session, url_cron, timeout=15)
    
    if resp_cron and resp_cron.status_code == 200:
        try:
            cron_data = resp_cron.json()
            print("✅ Resposta do cron:")
            print(json.dumps(cron_data, indent=2, ensure_ascii=False))
            
            results = cron_data.get('results', [])
            if results:
                print(f"🎯 Cron encontrou {len(results)} depósito(s) para processar")
                for result in results:
                    if result.get('depix_id') == depix_id:
                        print(f"✅ Nosso depósito {depix_id} foi encontrado pelo cron!")
                        break
                else:
                    print(f"⚠️  Nosso depósito {depix_id} NÃO foi encontrado pelo cron")
            else:
                print("⚠️  Cron não retornou nenhum depósito para processar")
                
        except Exception as e:
            print(f"❌ Erro ao processar resposta do cron: {e}")
    else:
        print("❌ Falha ao chamar endpoint cron")
    
    print(f"\n4️⃣ TESTANDO NOTIFIER")
    url_notifier = f"https://useghost.squareweb.app/api/lightning_notifier.php?chat_id={chat_id}"
    resp_notifier = safe_request(session, url_notifier, timeout=10)
    
    if resp_notifier and resp_notifier.status_code == 200:
        try:
            notifier_data = resp_notifier.json()
            print("✅ Resposta do notifier:")
            print(json.dumps(notifier_data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ Erro ao processar resposta do notifier: {e}")
            print(f"Resposta bruta: {resp_notifier.text}")
    else:
        print("❌ Falha ao chamar notifier")
    
    print(f"\n5️⃣ RESUMO E PRÓXIMOS PASSOS")
    print("=" * 60)
    print("✅ Se tudo estiver funcionando:")
    print("   - O depósito deve ter blockchainTxID preenchido")
    print("   - O cron deve encontrar o depósito na consulta")
    print("   - O notifier deve retornar 'success'")
    print("   - O bot deve solicitar endereço Lightning no chat")
    print("")
    print("🔧 Se algo não estiver funcionando:")
    print("   - Verifique logs do backend (/logs/)")
    print("   - Verifique se o bot está rodando")
    print("   - Verifique se o chat_id está correto")
    print("   - Execute o cron manualmente algumas vezes")

def simulate_local_flow():
    """Simula o fluxo localmente quando o servidor não está acessível"""
    print("\n🔄 SIMULAÇÃO LOCAL DO FLUXO")
    print("=" * 40)
    print("Como o servidor não está acessível, vou explicar o que deveria acontecer:")
    print("")
    print(f"1. Consulta do depósito {depix_id}:")
    print("   - Deve ter status 'awaiting_client_invoice' ou similar")
    print("   - Deve ter blockchainTxID preenchido")
    print("   - Deve ter chat_id associado")
    print("")
    print("2. Cron endpoint:")
    print("   - Busca depósitos com blockchainTxID preenchido")
    print("   - Filtra por status apropriado")
    print("   - Retorna lista de depósitos para processar")
    print("")
    print("3. Notifier:")
    print("   - Recebe chat_id como parâmetro")
    print("   - Processa depósitos pendentes para esse chat")
    print("   - Envia mensagem via bot solicitando endereço Lightning")
    print("")
    print("💡 Para testar quando o servidor voltar:")
    print("   - Execute este script novamente")
    print("   - Ou use o simulador em /simulador/")
    print("   - Ou acesse diretamente as URLs via curl/browser")

if __name__ == "__main__":
    main()
