#!/usr/bin/env python3
"""
Monitor em Tempo Real do Sistema de Captura
Execute este script para acompanhar todos os passos do usuário em tempo real
"""
import os
import time
from pathlib import Path
from datetime import datetime
import argparse


def monitor_logs(capture_dir, log_date, filter_user=None, filter_keyword=None):
    """Monitora logs de captura em tempo real, com filtros opcionais"""
    log_file = capture_dir / f"capture_{log_date}.log"
    print("🎯 MONITOR DE CAPTURA EM TEMPO REAL")
    print("=" * 50)
    print(f"📁 Monitorando: {log_file}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
    if filter_user:
        print(f"🔎 Filtro de usuário: {filter_user}")
    if filter_keyword:
        print(f"🔎 Filtro de palavra-chave: {filter_keyword}")
    print("=" * 50)
    print()
    if not log_file.exists():
        print("⚠️ Arquivo de log não encontrado. Aguardando criação...")
        while not log_file.exists():
            time.sleep(1)
            print(".", end="", flush=True)
        print("\n✅ Arquivo de log encontrado!")
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                if filter_user and filter_user not in line:
                    continue
                if filter_keyword and filter_keyword not in line:
                    continue
                print(line, end="")
    except KeyboardInterrupt:
        print("\n🛑 Monitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no monitoramento: {e}")


def main():
    parser = argparse.ArgumentParser(description="Monitor em tempo real do sistema de captura")
    parser.add_argument('--dir', type=str, default="/home/mau/bot/ghost/captura", help="Diretório dos logs de captura")
    parser.add_argument('--date', type=str, default=datetime.now().strftime('%Y%m%d'), help="Data do log (YYYYMMDD)")
    parser.add_argument('--user', type=str, help="Filtrar por ID de usuário")
    parser.add_argument('--keyword', type=str, help="Filtrar por palavra-chave")
    args = parser.parse_args()
    capture_dir = Path(args.dir)
    monitor_logs(capture_dir, args.date, args.user, args.keyword)

if __name__ == "__main__":
    main()
