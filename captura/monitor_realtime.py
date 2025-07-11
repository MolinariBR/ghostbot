#!/usr/bin/env python3
"""
Monitor em Tempo Real do Sistema de Captura
Execute este script para acompanhar todos os passos do usuário em tempo real
"""
import os
import time
from pathlib import Path
from datetime import datetime

def monitor_logs():
    """Monitora logs de captura em tempo real"""
    
    capture_dir = Path("/home/mau/bot/ghost/captura")
    log_file = capture_dir / f"capture_{datetime.now().strftime('%Y%m%d')}.log"
    
    print("🎯 MONITOR DE CAPTURA EM TEMPO REAL")
    print("=" * 50)
    print(f"📁 Monitorando: {log_file}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    print()
    
    if not log_file.exists():
        print("⚠️ Arquivo de log não encontrado. Aguardando criação...")
        while not log_file.exists():
            time.sleep(1)
            print(".", end="", flush=True)
        print("\n✅ Arquivo de log encontrado!")
    
    # Usar tail -f para monitorar o arquivo
    try:
        cmd = f"tail -f {log_file}"
        os.system(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Monitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no monitoramento: {e}")

if __name__ == "__main__":
    monitor_logs()
