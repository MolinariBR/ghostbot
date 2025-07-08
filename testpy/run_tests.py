#!/usr/bin/env python3
"""
Script para executar todos os testes do projeto.

Uso:
    python run_tests.py       # Executa todos os testes
    python run_tests.py -v    # Modo verboso
    python run_tests.py -k "test_compra"  # Executa apenas testes com 'test_compra' no nome
"""
import sys
import subprocess
import os

def run_tests():
    """Executa todos os testes usando pytest."""
    # Cria o diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Comando para executar os testes
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=api", "--cov=menus",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "tests/"
    ] + sys.argv[1:]
    
    # Executa o comando
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(run_tests())
