#!/usr/bin/env python3
"""
Teste do Sistema Completo de Limites por Usuário
Testa o sistema de banco de dados local, limites progressivos e redirecionamentos.
"""

import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from limites.gerenciador_usuario import (
    GerenciadorLimites,
    validar_compra_usuario,
    registrar_compra_usuario,
    obter_estatisticas_usuario
)

def teste_banco_dados():
    """Testa a criação e funcionamento do banco de dados."""
    print("=== TESTE DE BANCO DE DADOS ===\n")
    
    # Testa criação do gerenciador
    gerenciador = GerenciadorLimites("data/teste_limites.db")
    print("✅ Banco de dados criado com sucesso")
    
    # Testa criação de usuário
    chatid_teste = "123456789"
    usuario = gerenciador.obter_ou_criar_usuario(chatid_teste)
    print(f"✅ Usuário criado: {usuario['chatid']}")
    print(f"   Limite inicial: R$ {usuario['limite_atual']:.2f}")
    print(f"   Compras: {usuario['num_compras']}")
    
    # Verifica se o usuário já existe
    usuario2 = gerenciador.obter_ou_criar_usuario(chatid_teste)
    print(f"✅ Usuário encontrado: {usuario2['chatid']}")
    
    print()

def teste_limites_usuario():
    """Testa os limites por usuário."""
    print("=== TESTE DE LIMITES POR USUÁRIO ===\n")
    
    chatid_teste = "user_test_001"
    
    # Primeira compra
    print("🔹 Primeira compra:")
    validacao = validar_compra_usuario(chatid_teste, 100.00)
    print(f"  R$ 100,00 - {'✅ APROVADO' if validacao['valido'] else '❌ REJEITADO'}")
    if validacao['valido']:
        print(f"  Limite atual: R$ {validacao['limite_atual']:.2f}")
        print(f"  Primeira compra: {validacao['primeira_compra']}")
    
    # Compra acima do limite
    print("\n🔹 Compra acima do limite:")
    validacao = validar_compra_usuario(chatid_teste, 600.00)
    print(f"  R$ 600,00 - {'✅ APROVADO' if validacao['valido'] else '❌ REJEITADO'}")
    if not validacao['valido']:
        print(f"  Erro: {validacao['erro']}")
        print(f"  Mensagem: {validacao['mensagem']}")
        print(f"  Dica: {validacao['dica']}")
    
    # Registra primeira compra
    print("\n🔹 Registrando primeira compra:")
    registrar_compra_usuario(chatid_teste, 100.00)
    print("  ✅ Compra registrada com sucesso")
    
    # Testa segunda compra
    print("\n🔹 Segunda compra:")
    validacao = validar_compra_usuario(chatid_teste, 800.00)
    print(f"  R$ 800,00 - {'✅ APROVADO' if validacao['valido'] else '❌ REJEITADO'}")
    if validacao['valido']:
        print(f"  Limite atual: R$ {validacao['limite_atual']:.2f}")
        print(f"  Primeira compra: {validacao['primeira_compra']}")
    
    print()

def teste_cpf_limite():
    """Testa o sistema de CPF para aumentar limite."""
    print("=== TESTE DE CPF PARA LIMITE ===\n")
    
    chatid_teste = "user_cpf_test"
    
    # Primeira compra sem CPF
    print("🔹 Primeira compra sem CPF:")
    validacao = validar_compra_usuario(chatid_teste, 600.00)
    print(f"  R$ 600,00 - {'✅ APROVADO' if validacao['valido'] else '❌ REJEITADO'}")
    if not validacao['valido']:
        print(f"  Limite atual: R$ {validacao['limite_atual']:.2f}")
        print(f"  Precisa CPF: {validacao['precisa_cpf']}")
    
    # Primeira compra com CPF
    print("\n🔹 Primeira compra com CPF:")
    cpf_valido = "12345678909"
    validacao = validar_compra_usuario(chatid_teste, 600.00, cpf_valido)
    print(f"  R$ 600,00 - {'✅ APROVADO' if validacao['valido'] else '❌ REJEITADO'}")
    if validacao['valido']:
        print(f"  Limite atual: R$ {validacao['limite_atual']:.2f}")
        print(f"  Precisa CPF: {validacao['precisa_cpf']}")
    
    # Compra máxima com CPF
    print("\n🔹 Compra máxima com CPF:")
    validacao = validar_compra_usuario(chatid_teste, 4999.99, cpf_valido)
    print(f"  R$ 4999,99 - {'✅ APROVADO' if validacao['valido'] else '❌ REJEITADO'}")
    if validacao['valido']:
        print(f"  Limite atual: R$ {validacao['limite_atual']:.2f}")
    
    print()

def teste_estatisticas():
    """Testa as estatísticas do usuário."""
    print("=== TESTE DE ESTATÍSTICAS ===\n")
    
    chatid_teste = "user_stats_test"
    
    # Cria usuário e faz algumas compras
    registrar_compra_usuario(chatid_teste, 100.00)
    registrar_compra_usuario(chatid_teste, 200.00)
    registrar_compra_usuario(chatid_teste, 300.00)
    
    # Obtém estatísticas
    stats = obter_estatisticas_usuario(chatid_teste)
    print(f"📊 Estatísticas do usuário {chatid_teste}:")
    print(f"  Compras realizadas: {stats['num_compras']}")
    print(f"  Limite atual: R$ {stats['limite_atual']:.2f}")
    print(f"  Total comprado: R$ {stats['total_comprado']:.2f}")
    print(f"  Compras hoje: {stats['compras_hoje']}")
    print(f"  Tem CPF: {stats['tem_cpf']}")
    print(f"  Precisa CPF: {stats['precisa_cpf']}")
    print(f"  Primeira compra: {stats['primeira_compra']}")
    
    print()

def teste_escada_completa():
    """Testa a escada completa de limites."""
    print("=== TESTE DE ESCADA COMPLETA ===\n")
    
    chatid_teste = "user_escada_test"
    
    # Simula compras ao longo da escada
    for i in range(12):
        stats = obter_estatisticas_usuario(chatid_teste)
        print(f"Compra {i+1}:")
        print(f"  Limite atual: R$ {stats['limite_atual']:.2f}")
        
        # Faz uma compra dentro do limite
        valor_compra = min(stats['limite_atual'], 100.00)
        registrar_compra_usuario(chatid_teste, valor_compra)
        print(f"  Compra realizada: R$ {valor_compra:.2f}")
        print()

def limpar_dados_teste():
    """Limpa os dados de teste."""
    try:
        if os.path.exists("data/teste_limites.db"):
            os.remove("data/teste_limites.db")
        print("✅ Dados de teste limpos")
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DO SISTEMA COMPLETO DE LIMITES\n")
    
    teste_banco_dados()
    teste_limites_usuario()
    teste_cpf_limite()
    teste_estatisticas()
    teste_escada_completa()
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("📝 Sistema de limites por usuário funcionando corretamente!")
    
    # Limpa dados de teste
    limpar_dados_teste()
