#!/usr/bin/env python3
"""
Script para verificar logs e dados do bot no servidor remoto
"""

import requests
import json
from datetime import datetime, timedelta

class VerificadorLogsServidor:
    def __init__(self):
        self.backend_url = "https://ghostbotback.meianoitebot.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GhostBot-LogChecker/1.0'
        })
    
    def verificar_endpoints_logs(self):
        """Verifica diferentes endpoints que podem conter logs"""
        print("🔍 VERIFICANDO ENDPOINTS DE LOGS NO SERVIDOR")
        print("=" * 50)
        
        endpoints = [
            # Logs diretos
            "/logs/bot.log",
            "/logs/fluxo.log",
            "/logs/lightning.log",
            "/logs/debug.log",
            "/logs/error.log",
            
            # APIs de logs
            "/api/logs.php",
            "/api/debug.php",
            "/api/status.php",
            "/api/recent_activity.php",
            
            # Admin/diagnóstico
            "/admin/logs.php",
            "/admin/debug.php",
            "/admin/status.php",
            "/diagnostic/logs.php",
            "/diagnostic/debug.php",
            "/diagnostico_completo.php",
            
            # REST endpoints
            "/rest/logs",
            "/rest/debug",
            "/rest/activity",
            
            # Outros possíveis
            "/debug/logs.php",
            "/status.php",
            "/health.php",
            "/info.php"
        ]
        
        found_endpoints = []
        
        for endpoint in endpoints:
            url = f"{self.backend_url}{endpoint}"
            try:
                print(f"📡 Testando: {endpoint}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    content_type = response.headers.get('content-type', '')
                    
                    # Analisa o conteúdo
                    is_log = self.analisar_conteudo_log(content)
                    is_json = 'json' in content_type.lower()
                    
                    if is_log or is_json:
                        print(f"✅ ENCONTRADO: {endpoint}")
                        print(f"   📄 Tipo: {'JSON' if is_json else 'Log/Texto'}")
                        print(f"   📏 Tamanho: {len(content)} chars")
                        
                        found_endpoints.append({
                            'endpoint': endpoint,
                            'url': url,
                            'type': 'json' if is_json else 'log',
                            'content': content[:500] + '...' if len(content) > 500 else content
                        })
                        
                        # Mostra preview do conteúdo
                        self.mostrar_preview(content, is_json)
                    else:
                        print(f"⚠️ Acessível mas não parece ser log: {endpoint}")
                
                elif response.status_code == 403:
                    print(f"🔒 Acesso negado: {endpoint}")
                elif response.status_code == 404:
                    print(f"❌ Não encontrado: {endpoint}")
                else:
                    print(f"❓ HTTP {response.status_code}: {endpoint}")
                    
            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout: {endpoint}")
            except requests.exceptions.ConnectionError:
                print(f"🔌 Erro de conexão: {endpoint}")
            except Exception as e:
                print(f"❌ Erro: {endpoint} - {e}")
            
            print()
        
        return found_endpoints
    
    def analisar_conteudo_log(self, content):
        """Verifica se o conteúdo parece ser um log válido"""
        log_indicators = [
            'lightning', 'bot', 'telegram', 'error', 'info', 'debug',
            'warning', 'deposit', 'payment', 'invoice', 'address',
            'transaction', 'webhook', 'api', 'request', 'response',
            'timestamp', 'datetime', 'log', 'level'
        ]
        
        content_lower = content.lower()
        matches = sum(1 for indicator in log_indicators if indicator in content_lower)
        
        return matches >= 3  # Pelo menos 3 indicadores
    
    def mostrar_preview(self, content, is_json):
        """Mostra um preview do conteúdo encontrado"""
        print("   📋 Preview:")
        
        if is_json:
            try:
                data = json.loads(content)
                print(f"      🔧 JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                
                # Se for array, mostra info do primeiro item
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        print(f"      🔧 First Item Keys: {list(first_item.keys())}")
                
            except json.JSONDecodeError:
                print("      ❌ JSON inválido")
        else:
            # Mostra as primeiras linhas relevantes
            lines = content.split('\n')[:5]
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"      {i+1:2d}: {line.strip()[:80]}")
    
    def verificar_transacoes_recentes(self):
        """Verifica transações recentes via API"""
        print("\n💰 VERIFICANDO TRANSAÇÕES RECENTES")
        print("=" * 40)
        
        # Tenta diferentes endpoints de transações
        transaction_endpoints = [
            "/api/transacoes.php",
            "/api/deposits.php", 
            "/api/recent_deposits.php",
            "/transacoes.php",
            "/rest/transactions",
            "/rest/deposits"
        ]
        
        for endpoint in transaction_endpoints:
            url = f"{self.backend_url}{endpoint}"
            try:
                print(f"📡 Testando: {endpoint}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Tenta parsear como JSON
                    try:
                        data = json.loads(content)
                        print(f"✅ JSON encontrado: {endpoint}")
                        self.analisar_transacoes_json(data)
                    except json.JSONDecodeError:
                        # Verifica se é HTML com dados de transação
                        if any(keyword in content.lower() for keyword in 
                               ['transaction', 'deposit', 'bitcoin', 'lightning']):
                            print(f"✅ Dados de transação encontrados: {endpoint}")
                            print(f"   📄 Tamanho: {len(content)} chars")
                        else:
                            print(f"⚠️ Não parece conter dados de transação")
                
                elif response.status_code == 403:
                    print(f"🔒 Acesso negado: {endpoint}")
                elif response.status_code == 404:
                    print(f"❌ Não encontrado: {endpoint}")
                else:
                    print(f"❓ HTTP {response.status_code}: {endpoint}")
                    
            except Exception as e:
                print(f"❌ Erro: {endpoint} - {e}")
            
            print()
    
    def analisar_transacoes_json(self, data):
        """Analisa dados JSON de transações"""
        if isinstance(data, list):
            print(f"   📊 {len(data)} transações encontradas")
            
            # Mostra as mais recentes
            recent = data[:3] if len(data) >= 3 else data
            for i, transaction in enumerate(recent):
                if isinstance(transaction, dict):
                    print(f"   🔍 Transação {i+1}:")
                    for key, value in transaction.items():
                        print(f"      {key}: {value}")
                    print()
        
        elif isinstance(data, dict):
            print(f"   📊 Objeto de transação:")
            for key, value in data.items():
                print(f"      {key}: {value}")
    
    def verificar_status_sistema(self):
        """Verifica status geral do sistema"""
        print("\n🔧 VERIFICANDO STATUS DO SISTEMA")
        print("=" * 35)
        
        status_endpoints = [
            "/api/status.php",
            "/status.php",
            "/health.php",
            "/ping.php",
            "/api/health.php"
        ]
        
        for endpoint in status_endpoints:
            url = f"{self.backend_url}{endpoint}"
            try:
                print(f"📡 Testando: {endpoint}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    print(f"✅ Disponível: {endpoint}")
                    
                    # Tenta parsear como JSON
                    try:
                        data = json.loads(content)
                        print(f"   📊 Status JSON:")
                        for key, value in data.items():
                            print(f"      {key}: {value}")
                    except json.JSONDecodeError:
                        # Mostra conteúdo texto
                        lines = content.split('\n')[:3]
                        for line in lines:
                            if line.strip():
                                print(f"   📄 {line.strip()}")
                
                elif response.status_code == 404:
                    print(f"❌ Não encontrado: {endpoint}")
                else:
                    print(f"❓ HTTP {response.status_code}: {endpoint}")
                    
            except Exception as e:
                print(f"❌ Erro: {endpoint} - {e}")
            
            print()
    
    def executar_verificacao_completa(self):
        """Executa verificação completa do servidor"""
        print("🚀 INICIANDO VERIFICAÇÃO COMPLETA DO SERVIDOR")
        print("=" * 60)
        print(f"🎯 URL Base: {self.backend_url}")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Verifica endpoints de logs
        found_logs = self.verificar_endpoints_logs()
        
        # 2. Verifica transações
        self.verificar_transacoes_recentes()
        
        # 3. Verifica status do sistema
        self.verificar_status_sistema()
        
        # 4. Resumo
        print("\n📋 RESUMO DA VERIFICAÇÃO")
        print("=" * 30)
        
        if found_logs:
            print(f"✅ {len(found_logs)} endpoint(s) de log encontrado(s):")
            for log_info in found_logs:
                print(f"   🔗 {log_info['endpoint']} ({log_info['type']})")
        else:
            print("❌ Nenhum endpoint de log encontrado")
        
        print("\n💡 PRÓXIMOS PASSOS:")
        if found_logs:
            print("   1. Usar endpoints encontrados para monitorar atividade")
            print("   2. Executar teste de fluxo completo")
            print("   3. Verificar dados nos endpoints encontrados")
        else:
            print("   1. Verificar configuração do servidor")
            print("   2. Verificar permissões de acesso")
            print("   3. Contactar administrador do servidor")

def main():
    verificador = VerificadorLogsServidor()
    verificador.executar_verificacao_completa()

if __name__ == "__main__":
    main()
