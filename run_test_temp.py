#!/usr/bin/env python3
import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.abspath('.'))

# Executa o teste
if __name__ == "__main__":
    exec(open('testpy/test_fluxo_compra_completo.py').read())
