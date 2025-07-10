#!/usr/bin/env python3
"""
Teste de Performance do Ghost Bot
Mede tempos de resposta e throughput do sistema
"""

import time
import asyncio
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from test_fluxo_compra_completo import TesteFluxoCompleto

class TestePerformance(TesteFluxoCompleto):
    def __init__(self):
        super().__init__()
        self.metricas = {
            'tempos_resposta': [],
            'throughput': [],
            'erros': [],
            'picos_memoria': []
        }
    
    def medir_tempo_api(self, endpoint, metodo='GET', payload=None, tentativas=10):
        """Mede tempo de resposta de um endpoint"""
        print(f"\n📊 Medindo performance: {endpoint}")
        
        tempos = []
        erros = 0
        
        for i in range(tentativas):
            start_time = time.time()
            
            try:
                if metodo == 'GET':
                    response = requests.get(endpoint, timeout=10)
                elif metodo == 'POST':
                    response = requests.post(endpoint, json=payload, timeout=10)
                
                end_time = time.time()
                tempo_resposta = (end_time - start_time) * 1000  # ms
                
                if response.status_code == 200:
                    tempos.append(tempo_resposta)
                    print(f"✅ Tentativa {i+1}: {tempo_resposta:.2f}ms")
                else:
                    erros += 1
                    print(f"❌ Tentativa {i+1}: HTTP {response.status_code}")
                    
            except Exception as e:
                erros += 1
                print(f"⚠️ Tentativa {i+1}: Erro - {e}")
            
            # Pequeno delay entre tentativas
            time.sleep(0.1)
        
        if tempos:
            return {
                'endpoint': endpoint,
                'tentativas': tentativas,
                'sucessos': len(tempos),
                'erros': erros,
                'tempo_medio': statistics.mean(tempos),
                'tempo_mediano': statistics.median(tempos),
                'tempo_min': min(tempos),
                'tempo_max': max(tempos),
                'desvio_padrao': statistics.stdev(tempos) if len(tempos) > 1 else 0
            }
        else:
            return {
                'endpoint': endpoint,
                'tentativas': tentativas,
                'sucessos': 0,
                'erros': erros,
                'erro_total': True
            }
    
    def testar_throughput_pedidos(self, num_pedidos=50):
        """Testa throughput de criação de pedidos"""
        print(f"\n🚀 Testando throughput com {num_pedidos} pedidos simultâneos")
        
        def criar_pedido_rapido():
            """Cria pedido rapidamente para teste de throughput"""
            try:
                depix_id = f"PERF_{int(time.time()*1000)}"
                payload = {
                    "chatid": self.chat_id,
                    "moeda": "BTC",
                    "rede": "⚡ Lightning",
                    "amount_in_cents": 1000,  # R$ 10,00
                    "taxa": 10.0,
                    "address": self.lightning_address,
                    "forma_pagamento": "PIX",
                    "send": 0.00003,
                    "user_id": int(self.chat_id),
                    "depix_id": depix_id,
                    "status": "pending"
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{self.backend_url}/rest/deposit.php",
                    json=payload,
                    timeout=15
                )
                end_time = time.time()
                
                return {
                    'tempo': (end_time - start_time) * 1000,
                    'sucesso': response.status_code == 200,
                    'status_code': response.status_code
                }
                
            except Exception as e:
                return {
                    'tempo': 0,
                    'sucesso': False,
                    'erro': str(e)
                }
        
        start_total = time.time()
        
        # Executa pedidos em paralelo
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(criar_pedido_rapido) for _ in range(num_pedidos)]
            resultados = []
            
            for future in as_completed(futures):
                resultado = future.result()
                resultados.append(resultado)
        
        end_total = time.time()
        tempo_total = end_total - start_total
        
        # Calcula métricas
        sucessos = sum(1 for r in resultados if r['sucesso'])
        falhas = num_pedidos - sucessos
        tempos_sucessos = [r['tempo'] for r in resultados if r['sucesso']]
        
        throughput = sucessos / tempo_total if tempo_total > 0 else 0
        
        print(f"📊 RESULTADO DO TESTE DE THROUGHPUT:")
        print(f"   📋 Pedidos totais: {num_pedidos}")
        print(f"   ✅ Sucessos: {sucessos}")
        print(f"   ❌ Falhas: {falhas}")
        print(f"   ⏱️ Tempo total: {tempo_total:.2f}s")
        print(f"   🚀 Throughput: {throughput:.2f} pedidos/s")
        
        if tempos_sucessos:
            print(f"   📈 Tempo médio por pedido: {statistics.mean(tempos_sucessos):.2f}ms")
            print(f"   📊 Tempo mediano: {statistics.median(tempos_sucessos):.2f}ms")
        
        return {
            'total_pedidos': num_pedidos,
            'sucessos': sucessos,
            'falhas': falhas,
            'tempo_total': tempo_total,
            'throughput': throughput,
            'tempos_resposta': tempos_sucessos
        }
    
    def testar_carga_progressiva(self):
        """Testa carga progressiva no sistema"""
        print("\n📈 TESTE DE CARGA PROGRESSIVA")
        
        cargas = [1, 5, 10, 20, 30, 50]
        resultados_carga = []
        
        for carga in cargas:
            print(f"\n🔄 Testando carga: {carga} pedidos simultâneos")
            resultado = self.testar_throughput_pedidos(carga)
            resultados_carga.append({
                'carga': carga,
                'resultado': resultado
            })
            
            # Pausa entre testes para não sobrecarregar
            time.sleep(2)
        
        # Analisa resultados
        print("\n📊 ANÁLISE DE CARGA PROGRESSIVA:")
        print("Carga | Sucessos | Throughput | Tempo Médio")
        print("-" * 50)
        
        for item in resultados_carga:
            carga = item['carga']
            resultado = item['resultado']
            sucessos = resultado['sucessos']
            throughput = resultado['throughput']
            tempo_medio = statistics.mean(resultado['tempos_resposta']) if resultado['tempos_resposta'] else 0
            
            print(f"{carga:5d} | {sucessos:8d} | {throughput:10.2f} | {tempo_medio:11.2f}ms")
        
        return resultados_carga
    
    def executar_teste_performance_completo(self):
        """Executa suite completa de testes de performance"""
        print("🚀 EXECUTANDO TESTE DE PERFORMANCE COMPLETO")
        print("="*60)
        
        resultados = {}
        
        # 1. Teste de tempo de resposta dos endpoints
        print("\n1️⃣ TESTE DE TEMPO DE RESPOSTA")
        endpoints = [
            f"{self.backend_url}/rest/deposit.php",
            f"{self.backend_url}/api/status.php",
            f"{self.backend_url}/square_webhook.php"
        ]
        
        for endpoint in endpoints:
            try:
                resultado = self.medir_tempo_api(endpoint, tentativas=20)
                resultados[f'tempo_resposta_{endpoint.split("/")[-1]}'] = resultado
            except Exception as e:
                print(f"❌ Erro testando {endpoint}: {e}")
        
        # 2. Teste de throughput
        print("\n2️⃣ TESTE DE THROUGHPUT")
        try:
            resultado_throughput = self.testar_throughput_pedidos(30)
            resultados['throughput'] = resultado_throughput
        except Exception as e:
            print(f"❌ Erro no teste de throughput: {e}")
        
        # 3. Teste de carga progressiva
        print("\n3️⃣ TESTE DE CARGA PROGRESSIVA")
        try:
            resultado_carga = self.testar_carga_progressiva()
            resultados['carga_progressiva'] = resultado_carga
        except Exception as e:
            print(f"❌ Erro no teste de carga: {e}")
        
        # 4. Relatório final
        self.gerar_relatorio_performance(resultados)
        
        return resultados
    
    def gerar_relatorio_performance(self, resultados):
        """Gera relatório completo de performance"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE PERFORMANCE")
        print("="*60)
        
        # Tempos de resposta
        print("\n📈 TEMPOS DE RESPOSTA:")
        for key, value in resultados.items():
            if key.startswith('tempo_resposta_'):
                endpoint = key.replace('tempo_resposta_', '')
                if 'erro_total' not in value:
                    print(f"   📋 {endpoint}:")
                    print(f"      ⏱️ Médio: {value['tempo_medio']:.2f}ms")
                    print(f"      📊 Mediano: {value['tempo_mediano']:.2f}ms")
                    print(f"      ⚡ Min: {value['tempo_min']:.2f}ms")
                    print(f"      🔥 Max: {value['tempo_max']:.2f}ms")
                    print(f"      ✅ Taxa sucesso: {value['sucessos']}/{value['tentativas']}")
                else:
                    print(f"   ❌ {endpoint}: Falha total")
        
        # Throughput
        if 'throughput' in resultados:
            throughput = resultados['throughput']
            print(f"\n🚀 THROUGHPUT:")
            print(f"   📋 Pedidos/segundo: {throughput['throughput']:.2f}")
            print(f"   ✅ Taxa sucesso: {throughput['sucessos']}/{throughput['total_pedidos']}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        
        # Analisa throughput
        if 'throughput' in resultados:
            throughput_rate = resultados['throughput']['throughput']
            if throughput_rate > 10:
                print("   ✅ Throughput excelente (>10 req/s)")
            elif throughput_rate > 5:
                print("   ⚠️ Throughput moderado (5-10 req/s)")
            else:
                print("   ❌ Throughput baixo (<5 req/s) - considere otimizações")
        
        # Analisa tempos de resposta
        tempos_medios = []
        for key, value in resultados.items():
            if key.startswith('tempo_resposta_') and 'erro_total' not in value:
                tempos_medios.append(value['tempo_medio'])
        
        if tempos_medios:
            tempo_medio_geral = statistics.mean(tempos_medios)
            if tempo_medio_geral < 500:
                print("   ✅ Tempos de resposta excelentes (<500ms)")
            elif tempo_medio_geral < 1000:
                print("   ⚠️ Tempos de resposta moderados (500-1000ms)")
            else:
                print("   ❌ Tempos de resposta altos (>1000ms) - requer otimização")
        
        print("="*60)

if __name__ == "__main__":
    teste_perf = TestePerformance()
    teste_perf.executar_teste_performance_completo()
