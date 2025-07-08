#!/usr/bin/env python3
"""
Validador de sintaxe PHP para identificar erros
"""

import subprocess
import os

def validar_sintaxe_php(arquivo):
    """Valida sintaxe de um arquivo PHP"""
    try:
        result = subprocess.run(['php', '-l', arquivo], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {arquivo} - Sintaxe OK")
            return True
        else:
            print(f"❌ {arquivo} - ERRO DE SINTAXE:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("⚠️  PHP não encontrado. Instale PHP: sudo apt install php-cli")
        return None
    except Exception as e:
        print(f"❌ Erro ao validar {arquivo}: {e}")
        return False

def main():
    """Valida arquivos PHP principais"""
    print("🔍 Validador de Sintaxe PHP")
    print("="*40)
    
    arquivos = [
        "/home/mau/bot/ghostbackend/api/lightning_cron_endpoint_final.php",
        "/home/mau/bot/ghostbackend/api/utils_lightning.php",
        "/home/mau/bot/ghostbackend/api/lightning_notifier.php",
        "/home/mau/bot/ghostbackend/config/db.php"
    ]
    
    todos_ok = True
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            resultado = validar_sintaxe_php(arquivo)
            if resultado is False:
                todos_ok = False
        else:
            print(f"⚠️  {arquivo} - Arquivo não encontrado")
            todos_ok = False
    
    print("\n" + "="*40)
    if todos_ok:
        print("🎉 Todos os arquivos PHP têm sintaxe válida!")
    else:
        print("❌ Erros de sintaxe encontrados!")
    
    return 0 if todos_ok else 1

if __name__ == "__main__":
    exit(main())
