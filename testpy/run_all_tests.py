#!/usr/bin/env python3
"""
Executor de Todos os Testes do Ghost Bot
Executa suite completa de testes automatizados
"""

import os
import sys
import json
import time
from datetime import datetime

# Adiciona diretório do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Imports dos testes
from test_fluxo_compra_completo import TesteFluxoCompleto
from test_multi_usuario import TesteMultiUsuario
from test_cenarios_erro import TesteCenariosErro
from test_performance import TestePerformance

class ExecutorTestes:
    def __init__(self):
        self.inicio_execucao = datetime.now()
        self.resultados = {}
        self.log_execucao = []
    
    def log(self, mensagem):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] {mensagem}"
        print(msg)
        self.log_execucao.append(msg)
    
    def executar_teste_basico(self):
        """Executa teste básico de fluxo completo"""
        self.log("🚀 Iniciando teste básico de fluxo completo")
        
        try:
            teste = TesteFluxoCompleto()
            resultado = teste.executar_teste_completo()
            
            self.resultados['teste_basico'] = {
                'sucesso': resultado,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log(f"✅ Teste básico: {'SUCESSO' if resultado else 'FALHA'}")
            return resultado
            
        except Exception as e:
            self.log(f"❌ Erro no teste básico: {e}")
            self.resultados['teste_basico'] = {
                'sucesso': False,
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def executar_teste_multi_usuario(self):
        """Executa testes multi-usuário"""
        self.log("👥 Iniciando testes multi-usuário")
        
        try:
            teste = TesteMultiUsuario()
            resultados = teste.executar_testes_paralelos()
            
            sucessos = sum(1 for r in resultados if r['sucesso'])
            total = len(resultados)
            
            self.resultados['multi_usuario'] = {
                'sucessos': sucessos,
                'total': total,
                'taxa_sucesso': sucessos/total if total > 0 else 0,
                'resultados': resultados,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log(f"✅ Multi-usuário: {sucessos}/{total} sucessos")
            return sucessos == total
            
        except Exception as e:
            self.log(f"❌ Erro nos testes multi-usuário: {e}")
            self.resultados['multi_usuario'] = {
                'sucesso': False,
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def executar_teste_cenarios_erro(self):
        """Executa testes de cenários de erro"""
        self.log("🧪 Iniciando testes de cenários de erro")
        
        try:
            teste = TesteCenariosErro()
            resultados = teste.executar_todos_cenarios_erro()
            
            sucessos = sum(1 for r in resultados.values() if r['sucesso'])
            total = len(resultados)
            
            self.resultados['cenarios_erro'] = {
                'sucessos': sucessos,
                'total': total,
                'taxa_sucesso': sucessos/total if total > 0 else 0,
                'resultados': resultados,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log(f"✅ Cenários de erro: {sucessos}/{total} sucessos")
            return sucessos == total
            
        except Exception as e:
            self.log(f"❌ Erro nos testes de cenários de erro: {e}")
            self.resultados['cenarios_erro'] = {
                'sucesso': False,
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def executar_teste_performance(self):
        """Executa testes de performance"""
        self.log("🚀 Iniciando testes de performance")
        
        try:
            teste = TestePerformance()
            resultados = teste.executar_teste_performance_completo()
            
            self.resultados['performance'] = {
                'resultados': resultados,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log("✅ Testes de performance concluídos")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro nos testes de performance: {e}")
            self.resultados['performance'] = {
                'sucesso': False,
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def executar_suite_completa(self):
        """Executa suite completa de testes"""
        self.log("🎯 INICIANDO SUITE COMPLETA DE TESTES")
        self.log("="*60)
        
        # Lista de testes
        testes = [
            ("Teste Básico", self.executar_teste_basico),
            ("Multi-Usuário", self.executar_teste_multi_usuario),
            ("Cenários de Erro", self.executar_teste_cenarios_erro),
            ("Performance", self.executar_teste_performance)
        ]
        
        resultados_finais = []
        
        for nome, metodo in testes:
            self.log(f"\n📋 EXECUTANDO: {nome}")
            self.log("-" * 40)
            
            start_time = time.time()
            sucesso = metodo()
            end_time = time.time()
            
            duracao = end_time - start_time
            
            resultados_finais.append({
                'nome': nome,
                'sucesso': sucesso,
                'duracao': duracao
            })
            
            self.log(f"⏱️ Duração: {duracao:.2f}s")
            self.log(f"{'✅' if sucesso else '❌'} {nome}: {'SUCESSO' if sucesso else 'FALHA'}")
        
        # Relatório final
        self.gerar_relatorio_final(resultados_finais)
        
        return resultados_finais
    
    def gerar_relatorio_final(self, resultados_finais):
        """Gera relatório final da suite de testes"""
        fim_execucao = datetime.now()
        duracao_total = fim_execucao - self.inicio_execucao
        
        self.log("\n" + "="*60)
        self.log("📊 RELATÓRIO FINAL DA SUITE DE TESTES")
        self.log("="*60)
        
        sucessos = sum(1 for r in resultados_finais if r['sucesso'])
        total = len(resultados_finais)
        
        self.log(f"📅 Início: {self.inicio_execucao.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"📅 Fim: {fim_execucao.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"⏱️ Duração total: {duracao_total.total_seconds():.2f}s")
        self.log(f"📋 Testes executados: {total}")
        self.log(f"✅ Sucessos: {sucessos}")
        self.log(f"❌ Falhas: {total - sucessos}")
        self.log(f"📈 Taxa de sucesso: {sucessos/total*100:.1f}%")
        
        self.log("\n📋 RESUMO POR TESTE:")
        for resultado in resultados_finais:
            status = "✅" if resultado['sucesso'] else "❌"
            self.log(f"{status} {resultado['nome']}: {resultado['duracao']:.2f}s")
        
        # Salva relatório em arquivo
        self.salvar_relatorio_arquivo(resultados_finais, duracao_total)
        
        self.log("="*60)
        
        # Retorna se todos os testes passaram
        return sucessos == total
    
    def salvar_relatorio_arquivo(self, resultados_finais, duracao_total):
        """Salva relatório em arquivo JSON"""
        try:
            relatorio = {
                'timestamp': datetime.now().isoformat(),
                'duracao_total_segundos': duracao_total.total_seconds(),
                'testes_executados': len(resultados_finais),
                'sucessos': sum(1 for r in resultados_finais if r['sucesso']),
                'falhas': sum(1 for r in resultados_finais if not r['sucesso']),
                'resultados_detalhados': self.resultados,
                'log_execucao': self.log_execucao,
                'resultados_finais': resultados_finais
            }
            
            # Cria diretório de relatórios se não existir
            os.makedirs('reports', exist_ok=True)
            
            # Nome do arquivo com timestamp
            nome_arquivo = f"reports/relatorio_testes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, ensure_ascii=False, indent=2)
            
            self.log(f"📄 Relatório salvo em: {nome_arquivo}")
            
        except Exception as e:
            self.log(f"❌ Erro salvando relatório: {e}")

if __name__ == "__main__":
    executor = ExecutorTestes()
    sucesso_geral = executor.executar_suite_completa()
    
    # Exit code para integração com CI/CD
    sys.exit(0 if sucesso_geral else 1)
