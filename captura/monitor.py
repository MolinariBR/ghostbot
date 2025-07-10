#!/usr/bin/env python3
"""
Monitor em Tempo Real
Monitora as sessões ativas em tempo real
"""
import time
import sys
from pathlib import Path
import json
from datetime import datetime

# Adicionar o path do sistema de captura
sys.path.insert(0, str(Path(__file__).parent))

try:
    from capture_system import capture_system
    CAPTURE_AVAILABLE = True
except ImportError:
    CAPTURE_AVAILABLE = False
    print("⚠️ Sistema de captura não disponível - usando modo de arquivos")

def monitor_with_capture_system():
    """Monitora usando o sistema de captura diretamente"""
    print("🎯 Monitor em Tempo Real - Sistema de Captura")
    print("=" * 60)
    print("Pressione Ctrl+C para sair\n")
    
    try:
        while True:
            # Obter sessões ativas
            active_sessions = capture_system.get_all_active_sessions()
            stuck_sessions = capture_system.find_stuck_sessions(10)  # 10 minutos
            
            # Limpar tela
            print("\033[2J\033[H")  # Clear screen
            
            print(f"🎯 MONITOR EM TEMPO REAL - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            
            if not active_sessions:
                print("😴 Nenhuma sessão ativa no momento")
            else:
                print(f"📊 {len(active_sessions)} sessões ativas")
                print()
                
                for user_id, session_data in active_sessions.items():
                    status = "🔴" if user_id in stuck_sessions else "🟢"
                    
                    print(f"{status} Usuário: {user_id}")
                    print(f"   Estado: {session_data['current_state']}")
                    print(f"   Passos: {session_data['total_steps']}")
                    print(f"   Erros: {session_data['total_errors']}")
                    print(f"   Duração: {session_data['duration_seconds']:.1f}s")
                    
                    if session_data['last_step']:
                        last_step = session_data['last_step']
                        step_status = "✅" if last_step.get('success', True) else "❌"
                        print(f"   Último passo: {step_status} {last_step.get('step', 'N/A')}")
                    
                    print()
            
            if stuck_sessions:
                print("🚨 SESSÕES POSSIVELMENTE TRAVADAS:")
                for user_id, info in stuck_sessions.items():
                    print(f"   🔴 {user_id}: {info['current_state']} ({info['duration_minutes']:.1f} min)")
                print()
            
            print("⏰ Atualização a cada 5 segundos...")
            print("📊 Pressione Ctrl+C para sair")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n👋 Monitor finalizado")

def monitor_with_files():
    """Monitora usando arquivos de log"""
    print("📄 Monitor em Tempo Real - Arquivos de Log")
    print("=" * 60)
    print("Pressione Ctrl+C para sair\n")
    
    capture_dir = Path(__file__).parent
    last_update = datetime.now()
    
    try:
        while True:
            # Verificar arquivos novos/modificados
            log_files = list(capture_dir.glob("capture_*.log"))
            session_files = list(capture_dir.glob("session_*.json"))
            
            # Contar linhas nos logs
            total_log_lines = 0
            recent_errors = []
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_log_lines += len(lines)
                        
                        # Procurar erros recentes
                        for line in lines[-20:]:  # Últimas 20 linhas
                            if 'ERROR' in line or 'FAILED' in line:
                                recent_errors.append(line.strip())
                except:
                    pass
            
            # Contar sessões
            total_sessions = len(session_files)
            recent_sessions = [f for f in session_files if f.stat().st_mtime > last_update.timestamp()]
            
            # Limpar tela
            print("\033[2J\033[H")
            
            print(f"📄 MONITOR DE ARQUIVOS - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            
            print(f"📊 Total de linhas de log: {total_log_lines}")
            print(f"📋 Total de sessões: {total_sessions}")
            print(f"🆕 Sessões desde última atualização: {len(recent_sessions)}")
            
            if recent_errors:
                print(f"\n🚨 ERROS RECENTES:")
                for error in recent_errors[-5:]:  # Últimos 5 erros
                    print(f"   {error}")
            
            if recent_sessions:
                print(f"\n🆕 SESSÕES RECENTES:")
                for session_file in recent_sessions[-5:]:  # Últimas 5 sessões
                    try:
                        with open(session_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                            user_id = session_data.get('user_id', 'N/A')
                            state = session_data.get('current_state', 'N/A')
                            steps = session_data.get('total_steps', 0)
                            errors = session_data.get('total_errors', 0)
                            
                            status = "❌" if errors > 0 else "✅"
                            print(f"   {status} {user_id}: {state} ({steps} passos)")
                    except:
                        print(f"   ❓ {session_file.name}: Erro ao ler arquivo")
            
            print(f"\n⏰ Atualização a cada 10 segundos...")
            print("📊 Pressione Ctrl+C para sair")
            
            last_update = datetime.now()
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n👋 Monitor finalizado")

def show_live_stats():
    """Mostra estatísticas em tempo real"""
    capture_dir = Path(__file__).parent
    
    while True:
        try:
            # Estatísticas básicas
            log_files = list(capture_dir.glob("capture_*.log"))
            session_files = list(capture_dir.glob("session_*.json"))
            
            print(f"\n📊 ESTATÍSTICAS EM TEMPO REAL - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 40)
            
            if CAPTURE_AVAILABLE:
                active = capture_system.get_all_active_sessions()
                stuck = capture_system.find_stuck_sessions(15)
                
                print(f"🟢 Sessões ativas: {len(active)}")
                print(f"🔴 Sessões travadas: {len(stuck)}")
            
            print(f"📄 Arquivos de log: {len(log_files)}")
            print(f"📋 Arquivos de sessão: {len(session_files)}")
            
            # Contadores de hoje
            today = datetime.now().strftime('%Y%m%d')
            today_sessions = [f for f in session_files if today in f.name]
            print(f"📅 Sessões hoje: {len(today_sessions)}")
            
            time.sleep(3)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(5)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor em tempo real do sistema de captura")
    parser.add_argument("--mode", choices=["live", "files", "stats"], default="live",
                       help="Modo de monitoramento")
    
    args = parser.parse_args()
    
    if args.mode == "live":
        if CAPTURE_AVAILABLE:
            monitor_with_capture_system()
        else:
            monitor_with_files()
    elif args.mode == "files":
        monitor_with_files()
    elif args.mode == "stats":
        show_live_stats()

if __name__ == "__main__":
    main()
