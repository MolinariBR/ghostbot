#!/usr/bin/env python3
"""
Teste Multi-Usuário do Ghost Bot
Executa testes paralelos com diferentes usuários e valores
"""

import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor
from test_fluxo_compra_completo import TesteFluxoCompleto

class TesteMultiUsuario:
    def __init__(self):
        with open('config/test_config.json', 'r') as f:
            self.config = json.load(f)
    
    def executar_teste_usuario(self, usuario_config, valor_teste):
        """Executa teste para um usuário específico"""
        print(f"\n🚀 Iniciando teste para usuário {usuario_config['chat_id']}")
        print(f"💰 Valor: R$ {valor_teste}")
        
        try:
            # Cria instância customizada do teste
            teste = TesteFluxoCompleto()
            teste.chat_id = usuario_config['chat_id']
            teste.lightning_address = usuario_config['lightning_address']
            teste.valor_compra = valor_teste
            
            # Executa teste
            resultado = teste.executar_teste_completo()
            
            return {
                'usuario': usuario_config['chat_id'],
                'valor': valor_teste,
                'sucesso': resultado,
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"❌ Erro no teste do usuário {usuario_config['chat_id']}: {e}")
            return {
                'usuario': usuario_config['chat_id'],
                'valor': valor_teste,
                'sucesso': False,
                'erro': str(e),
                'timestamp': time.time()
            }
    
    def executar_testes_paralelos(self):
        """Executa testes paralelos para múltiplos usuários"""
        print("🔄 Iniciando testes paralelos...")
        
        usuarios = self.config['test_users']
        valores = list(self.config['test_values'].values())
        
        # Cria lista de tarefas
        tarefas = []
        for usuario in usuarios:
            for valor in valores:
                tarefas.append((usuario, valor))
        
        # Executa em paralelo (máximo 3 simultâneos)
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.executar_teste_usuario, usuario, valor)
                for usuario, valor in tarefas
            ]
            
            resultados = []
            for future in futures:
                resultado = future.result()
                resultados.append(resultado)
        
        # Relatório final
        self.gerar_relatorio(resultados)
        
        return resultados
    
    def gerar_relatorio(self, resultados):
        """Gera relatório consolidado dos testes"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE TESTES MULTI-USUÁRIO")
        print("="*80)
        
        total_testes = len(resultados)
        sucessos = sum(1 for r in resultados if r['sucesso'])
        falhas = total_testes - sucessos
        
        print(f"📋 Total de testes: {total_testes}")
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print(f"📈 Taxa de sucesso: {sucessos/total_testes*100:.1f}%")
        
        print("\n📋 DETALHES POR TESTE:")
        for resultado in resultados:
            status = "✅" if resultado['sucesso'] else "❌"
            print(f"{status} Usuário {resultado['usuario']} - R$ {resultado['valor']}")
            if 'erro' in resultado:
                print(f"   💥 Erro: {resultado['erro']}")
        
        print("="*80)

if __name__ == "__main__":
    teste_multi = TesteMultiUsuario()
    teste_multi.executar_testes_paralelos()
