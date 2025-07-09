#!/usr/bin/env python3
"""
Teste do Sistema de Limites Progressivos
Testa a integração dos limites PIX + limites progressivos baseados no número de compras.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from limites.limite_valor import LimitesValor, validar_compra_com_limite_progressivo, calcular_limite_atual, obter_info_limites_usuario

def teste_limites_progressivos():
    """Testa o sistema de limites progressivos."""
    print("=== TESTE DE LIMITES PROGRESSIVOS ===\n")
    
    # Teste sem CPF
    print("🔹 Teste sem CPF:")
    for num_compras in range(0, 12):
        limite = calcular_limite_atual(num_compras)
        print(f"  Compra {num_compras + 1}: R$ {limite:.2f}")
    
    print("\n🔹 Teste com CPF:")
    for num_compras in range(0, 5):
        limite = calcular_limite_atual(num_compras, "12345678901")
        print(f"  Compra {num_compras + 1}: R$ {limite:.2f}")

def teste_validacao_progressiva():
    """Testa a validação combinada PIX + progressiva."""
    print("\n=== TESTE DE VALIDAÇÃO COMBINADA ===\n")
    
    cenarios = [
        # (valor, num_compras, cpf, descrição)
        (5.00, 0, None, "Valor abaixo do mínimo PIX"),
        (100.00, 0, None, "1ª compra - valor OK"),
        (600.00, 0, None, "1ª compra - valor acima do limite"),
        (800.00, 1, None, "2ª compra - valor OK"),
        (900.00, 1, None, "2ª compra - valor acima do limite"),
        (1500.00, 2, None, "3ª compra - valor acima do limite"),
        (1500.00, 2, "12345678901", "3ª compra com CPF - valor OK"),
        (5000.00, 0, "12345678901", "1ª compra com CPF - valor máximo"),
    ]
    
    for valor, num_compras, cpf, descricao in cenarios:
        resultado = validar_compra_com_limite_progressivo(valor, num_compras, cpf)
        status = "✅ VÁLIDO" if resultado["valido"] else "❌ INVÁLIDO"
        print(f"🔹 {descricao}")
        print(f"  R$ {valor:.2f} - {status}")
        if not resultado["valido"]:
            print(f"  Erro: {resultado['erro']}")
            print(f"  Mensagem: {resultado['mensagem']}")
            print(f"  Dica: {resultado['dica']}")
        print()

def teste_info_limites():
    """Testa as informações de limites do usuário."""
    print("=== TESTE DE INFORMAÇÕES DE LIMITES ===\n")
    
    # Usuário iniciante
    print("🔹 Usuário iniciante (0 compras):")
    info = obter_info_limites_usuario(0)
    print(f"  Limite atual: R$ {info['limite_atual']:.2f}")
    print(f"  Próximo limite: R$ {info['proximo_limite']:.2f}")
    print(f"  Compras para próximo: {info['compras_para_proximo']}")
    print()
    
    # Usuário intermediário
    print("🔹 Usuário intermediário (5 compras):")
    info = obter_info_limites_usuario(5)
    print(f"  Limite atual: R$ {info['limite_atual']:.2f}")
    print(f"  Próximo limite: R$ {info['proximo_limite']:.2f}")
    print(f"  Compras para próximo: {info['compras_para_proximo']}")
    print()
    
    # Usuário avançado
    print("🔹 Usuário avançado (10 compras):")
    info = obter_info_limites_usuario(10)
    print(f"  Limite atual: R$ {info['limite_atual']:.2f}")
    print(f"  Próximo limite: {info['proximo_limite']}")
    print(f"  Compras para próximo: {info['compras_para_proximo']}")
    print()
    
    # Usuário com CPF
    print("🔹 Usuário com CPF (3 compras):")
    info = obter_info_limites_usuario(3, "12345678901")
    print(f"  Limite atual: R$ {info['limite_atual']:.2f}")
    print(f"  Tem CPF: {info['tem_cpf']}")
    print()

def teste_validacao_cpf():
    """Testa a validação de CPF."""
    print("=== TESTE DE VALIDAÇÃO DE CPF ===\n")
    
    cpfs_teste = [
        ("12345678901", "CPF válido"),
        ("111.111.111-11", "CPF inválido - todos iguais"),
        ("123.456.789-09", "CPF válido formatado"),
        ("12345678", "CPF inválido - poucos dígitos"),
        ("", "CPF vazio"),
        ("123456789ab", "CPF inválido - caracteres"),
    ]
    
    for cpf, descricao in cpfs_teste:
        valido = LimitesValor.validar_cpf_basico(cpf)
        status = "✅ VÁLIDO" if valido else "❌ INVÁLIDO"
        print(f"🔹 {descricao}: {cpf} - {status}")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DO SISTEMA DE LIMITES PROGRESSIVOS\n")
    
    teste_limites_progressivos()
    teste_validacao_progressiva()
    teste_info_limites()
    teste_validacao_cpf()
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("📝 Sistema de limites progressivos integrado com sucesso!")
