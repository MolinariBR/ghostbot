#!/usr/bin/env python3
"""
Script de varredura de código para o diretório 'api'.
- Lista todas as funções de cada arquivo PHP e Python.
- Aponta duplicidade de nomes de funções.
- Aponta possíveis duplicidades de código (hash do corpo da função).
- Aponta funções vazias ou suspeitas.
- Relata arquivos sem funções.
"""
import os
import re
import hashlib
from collections import defaultdict

API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../api'))

funcs_por_arquivo = defaultdict(list)
funcs_por_nome = defaultdict(list)
funcs_por_hash = defaultdict(list)

for root, _, files in os.walk(API_DIR):
    for fname in files:
        if fname.endswith('.php') or fname.endswith('.py'):
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            # PHP
            if fname.endswith('.php'):
                pattern = re.compile(r'function\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*\{', re.MULTILINE)
            else:  # Python
                pattern = re.compile(r'def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\):', re.MULTILINE)
            for m in pattern.finditer(code):
                func_name = m.group(1)
                start = m.end()
                # Tenta pegar o corpo da função (simples)
                if fname.endswith('.php'):
                    # Pega até o próximo '}' no mesmo nível
                    body = ''
                    level = 1
                    i = start
                    while i < len(code) and level > 0:
                        if code[i] == '{':
                            level += 1
                        elif code[i] == '}':
                            level -= 1
                        body += code[i]
                        i += 1
                else:
                    # Python: pega até próxima def ou fim
                    lines = code[start:].split('\n')
                    body = ''
                    for line in lines:
                        if re.match(r'^\s*def\s', line):
                            break
                        body += line + '\n'
                body_hash = hashlib.md5(body.strip().encode()).hexdigest()
                funcs_por_arquivo[fname].append((func_name, body.strip(), body_hash))
                funcs_por_nome[func_name].append(fname)
                funcs_por_hash[body_hash].append((fname, func_name))

# Relatório
print("\n==== FUNÇÕES POR ARQUIVO ====")
for fname, funclist in funcs_por_arquivo.items():
    print(f"\nArquivo: {fname}")
    for func_name, body, _ in funclist:
        print(f"  - {func_name} (len: {len(body)})")
    if not funclist:
        print("  [SEM FUNÇÕES]")

print("\n==== DUPLICIDADE DE NOMES DE FUNÇÃO ====")
for func_name, files in funcs_por_nome.items():
    if len(files) > 1:
        print(f"Função '{func_name}' aparece em: {', '.join(files)}")

print("\n==== DUPLICIDADE DE CÓDIGO DE FUNÇÃO ====")
for body_hash, funclist in funcs_por_hash.items():
    if len(funclist) > 1:
        print(f"Funções duplicadas (hash {body_hash}):")
        for fname, func_name in funclist:
            print(f"  - {func_name} em {fname}")

print("\n==== FUNÇÕES VAZIAS OU SUSPEITAS ====")
for fname, funclist in funcs_por_arquivo.items():
    for func_name, body, _ in funclist:
        if len(body.strip()) < 10:
            print(f"Função '{func_name}' vazia/suspeita em {fname}")

print("\n==== ARQUIVOS SEM FUNÇÕES ====")
for root, _, files in os.walk(API_DIR):
    for fname in files:
        if fname.endswith('.php') or fname.endswith('.py'):
            if fname not in funcs_por_arquivo or not funcs_por_arquivo[fname]:
                print(f"{fname}")
