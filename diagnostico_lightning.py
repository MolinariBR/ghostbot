#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO DO SISTEMA LIGHTNING
==========================================
Script para identificar conflitos e problemas no fluxo Lightning
"""

import requests
import json
import os
import sqlite3
from pathlib import Path
import hashlib

class DiagnosticoLightning:
    def __init__(self):
        self.bot_path = "/home/mau/bot/ghost"
        self.backend_path = "/home/mau/bot/ghostbackend"
        self.problemas = []
        self.arquivos_verificados = []
        
    def log_problema(self, categoria, descricao, arquivo=None):
        """Registra um problema encontrado"""
        problema = {
            "categoria": categoria,
            "descricao": descricao,
            "arquivo": arquivo
        }
        self.problemas.append(problema)
        print(f"❌ [{categoria}] {descricao}")
        if arquivo:
            print(f"   📁 Arquivo: {arquivo}")
    
    def log_ok(self, descricao):
        """Registra algo que está funcionando"""
        print(f"✅ {descricao}")
    
    def verificar_arquivos_lightning(self):
        """Verifica todos os arquivos relacionados ao Lightning"""
        print("\n🔍 VERIFICANDO ARQUIVOS LIGHTNING...")
        print("=" * 50)
        
        arquivos_importantes = [
            # Backend PHP
            (f"{self.backend_path}/api/lightning_cron_endpoint.php", "Cron Lightning Principal"),
            (f"{self.backend_path}/api/lightning_cron_endpoint_fixed.php", "Cron Lightning Corrigido"),
            
            # Bot Python
            (f"{self.bot_path}/handlers/lightning_integration.py", "Handler Lightning Python"),
            (f"{self.bot_path}/criar_lightning_servidor.py", "Script Criação Depósitos"),
            
            # Banco de dados
            (f"{self.backend_path}/data/deposit.db", "Banco de Dados SQLite"),
        ]
        
        for arquivo, descricao in arquivos_importantes:
            if os.path.exists(arquivo):
                # Calcular hash do arquivo
                with open(arquivo, 'rb') as f:
                    hash_arquivo = hashlib.md5(f.read()).hexdigest()
                
                self.arquivos_verificados.append({
                    "arquivo": arquivo,
                    "descricao": descricao,
                    "hash": hash_arquivo,
                    "tamanho": os.path.getsize(arquivo)
                })
                self.log_ok(f"{descricao} encontrado")
                
                # Verificar conteúdo específico
                if "lightning_cron_endpoint.php" in arquivo:
                    self.verificar_conteudo_cron_php(arquivo)
                elif "lightning_integration.py" in arquivo:
                    self.verificar_conteudo_handler_python(arquivo)
            else:
                self.log_problema("ARQUIVO_AUSENTE", f"{descricao} não encontrado", arquivo)
    
    def verificar_conteudo_cron_php(self, arquivo):
        """Verifica o conteúdo do arquivo cron PHP"""
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Verificar se tem a correção
            if 'amount_in_cents' in conteudo and '$valor = $amount_cents / 100.0' in conteudo:
                self.log_ok(f"  📝 Correção de valor implementada em {os.path.basename(arquivo)}")
            else:
                self.log_problema("CODIGO_INCORRETO", f"Correção de valor NÃO implementada", arquivo)
            
            # Verificar se ainda tem referência ao campo "valor" problemático
            if '$deposito[\'valor\']' in conteudo:
                self.log_problema("CODIGO_PROBLEMÁTICO", "Ainda usa campo 'valor' inexistente", arquivo)
            
            # Verificar se tem logs de debug
            if 'DEBUG' in conteudo:
                self.log_ok(f"  📝 Logs de debug habilitados em {os.path.basename(arquivo)}")
            
        except Exception as e:
            self.log_problema("ERRO_LEITURA", f"Erro ao ler {arquivo}: {e}")
    
    def verificar_conteudo_handler_python(self, arquivo):
        """Verifica o conteúdo do handler Python"""
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Verificar conversão correta
            if '166.67' in conteudo:
                self.log_ok(f"  📝 Conversão 166.67 sats/real implementada")
            else:
                self.log_problema("CONVERSAO_INCORRETA", "Conversão sats/real incorreta", arquivo)
            
            # Verificar tratamento de JSON concatenado
            if 'split_point = content.find' in conteudo:
                self.log_ok(f"  📝 Tratamento de JSON concatenado implementado")
            else:
                self.log_problema("JSON_NAO_TRATADO", "JSON concatenado não tratado", arquivo)
                
        except Exception as e:
            self.log_problema("ERRO_LEITURA", f"Erro ao ler {arquivo}: {e}")
    
    def verificar_endpoints_ativos(self):
        """Verifica quais endpoints estão realmente ativos"""
        print("\n🌐 VERIFICANDO ENDPOINTS ATIVOS...")
        print("=" * 50)
        
        endpoints = [
            ("https://useghost.squareweb.app/api/lightning_cron_endpoint.php?token=lightning_cron_2025", "Cron Lightning Principal"),
            ("https://useghost.squareweb.app/api/lightning_cron_endpoint_fixed.php?token=lightning_cron_2025", "Cron Lightning Corrigido"),
        ]
        
        for url, descricao in endpoints:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    versao = data.get('versao', 'ORIGINAL')
                    encontrados = data.get('lightning_encontrados', 0)
                    processados = data.get('invoices_solicitados', 0)
                    
                    self.log_ok(f"{descricao} ativo")
                    print(f"   📊 Versão: {versao}")
                    print(f"   📊 Lightning encontrados: {encontrados}")
                    print(f"   📊 Invoices processados: {processados}")
                    
                    if versao == 'CORRIGIDA':
                        self.log_ok("  ✨ Versão corrigida está ativa!")
                    else:
                        self.log_problema("VERSAO_INCORRETA", "Versão original ainda ativa", url)
                else:
                    self.log_problema("ENDPOINT_ERRO", f"Status {response.status_code}", url)
            except Exception as e:
                self.log_problema("ENDPOINT_INACESSIVEL", f"Erro: {e}", url)
    
    def verificar_banco_dados(self):
        """Verifica o banco de dados SQLite"""
        print("\n🗃️ VERIFICANDO BANCO DE DADOS...")
        print("=" * 50)
        
        db_path = f"{self.backend_path}/data/deposit.db"
        if not os.path.exists(db_path):
            self.log_problema("BANCO_AUSENTE", "Banco de dados não encontrado", db_path)
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar estrutura da tabela
            cursor.execute("PRAGMA table_info(deposit)")
            colunas = cursor.fetchall()
            colunas_nomes = [col[1] for col in colunas]
            
            self.log_ok(f"Banco de dados acessível")
            print(f"   📊 Colunas encontradas: {', '.join(colunas_nomes)}")
            
            # Verificar se tem amount_in_cents
            if 'amount_in_cents' in colunas_nomes:
                self.log_ok("  ✅ Coluna amount_in_cents encontrada")
            else:
                self.log_problema("COLUNA_AUSENTE", "Coluna amount_in_cents não encontrada")
            
            # Verificar se tem campo 'valor'
            if 'valor' in colunas_nomes:
                self.log_ok("  ⚠️ Coluna 'valor' existe (pode causar confusão)")
            else:
                self.log_ok("  ✅ Coluna 'valor' não existe (correto)")
            
            # Verificar depósitos Lightning recentes
            cursor.execute("""
                SELECT id, depix_id, amount_in_cents, rede, status, comprovante 
                FROM deposit 
                WHERE rede LIKE '%lightning%' 
                ORDER BY id DESC 
                LIMIT 5
            """)
            depositos = cursor.fetchall()
            
            print(f"   📊 Últimos {len(depositos)} depósitos Lightning:")
            for dep in depositos:
                valor_reais = dep[2] / 100.0 if dep[2] else 0
                status_processamento = "PROCESSADO" if dep[5] and "invoice solicitado" in dep[5] else "PENDENTE"
                print(f"     ID: {dep[0]}, Valor: R$ {valor_reais:.2f}, Status: {dep[4]}, {status_processamento}")
            
            conn.close()
            
        except Exception as e:
            self.log_problema("ERRO_BANCO", f"Erro ao acessar banco: {e}")
    
    def testar_fluxo_completo(self):
        """Testa o fluxo completo criando um depósito de teste"""
        print("\n🧪 TESTANDO FLUXO COMPLETO...")
        print("=" * 50)
        
        import time
        test_depix_id = f"teste_diagnostico_{int(time.time())}"
        
        # Criar depósito de teste
        payload = {
            "action": "update_status",
            "depix_id": test_depix_id,
            "chatid": "7910260237",
            "user_id": "7910260237",
            "status": "confirmed",
            "moeda": "BTC",
            "rede": "lightning",
            "amount_in_cents": 1000,  # R$ 10,00
            "taxa": 0,
            "address": "lightning_address",
            "forma_pagamento": "PIX",
            "send": True,
            "blockchainTxID": f"teste_diagnostico_{int(time.time())}"
        }
        
        try:
            url = "https://useghost.squareweb.app/rest/deposit.php"
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                self.log_ok(f"Depósito de teste criado: {test_depix_id}")
                
                # Testar endpoint corrigido
                cron_url = "https://useghost.squareweb.app/api/lightning_cron_endpoint_fixed.php?token=lightning_cron_2025"
                cron_response = requests.get(cron_url, timeout=15)
                
                if cron_response.status_code == 200:
                    cron_data = cron_response.json()
                    if cron_data.get('invoices_solicitados', 0) > 0:
                        self.log_ok("✨ Fluxo completo funcionando com endpoint corrigido!")
                    else:
                        self.log_problema("FLUXO_NAO_PROCESSOU", "Depósito não foi processado pelo cron")
                
            else:
                self.log_problema("ERRO_CRIACAO_DEPOSITO", f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_problema("ERRO_TESTE_FLUXO", f"Erro no teste: {e}")
    
    def gerar_relatorio(self):
        """Gera relatório final"""
        print("\n📋 RELATÓRIO FINAL")
        print("=" * 50)
        
        total_problemas = len(self.problemas)
        
        if total_problemas == 0:
            print("🎉 SISTEMA ESTÁ FUNCIONANDO PERFEITAMENTE!")
        else:
            print(f"⚠️ ENCONTRADOS {total_problemas} PROBLEMAS:")
            
            # Agrupar por categoria
            problemas_por_categoria = {}
            for problema in self.problemas:
                cat = problema['categoria']
                if cat not in problemas_por_categoria:
                    problemas_por_categoria[cat] = []
                problemas_por_categoria[cat].append(problema)
            
            for categoria, problemas in problemas_por_categoria.items():
                print(f"\n🔸 {categoria}:")
                for problema in problemas:
                    print(f"   • {problema['descricao']}")
                    if problema['arquivo']:
                        print(f"     📁 {problema['arquivo']}")
        
        # Resumo dos arquivos
        print(f"\n📁 ARQUIVOS VERIFICADOS ({len(self.arquivos_verificados)}):")
        for arquivo_info in self.arquivos_verificados:
            print(f"   • {arquivo_info['descricao']}")
            print(f"     📁 {arquivo_info['arquivo']}")
            print(f"     🔢 Hash: {arquivo_info['hash'][:8]}... Tamanho: {arquivo_info['tamanho']} bytes")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        if any(p['categoria'] == 'VERSAO_INCORRETA' for p in self.problemas):
            print("   1. O endpoint original ainda está ativo - substitua pelo corrigido")
        if any(p['categoria'] == 'CODIGO_INCORRETO' for p in self.problemas):
            print("   2. Implemente as correções de valor nos arquivos PHP")
        if any(p['categoria'] == 'JSON_NAO_TRATADO' for p in self.problemas):
            print("   3. Implemente tratamento de JSON concatenado no handler Python")
    
    def executar_diagnostico_completo(self):
        """Executa diagnóstico completo"""
        print("🚀 INICIANDO DIAGNÓSTICO COMPLETO DO SISTEMA LIGHTNING")
        print("=" * 60)
        
        self.verificar_arquivos_lightning()
        self.verificar_endpoints_ativos()
        self.verificar_banco_dados()
        self.testar_fluxo_completo()
        self.gerar_relatorio()

if __name__ == "__main__":
    diagnostico = DiagnosticoLightning()
    diagnostico.executar_diagnostico_completo()
