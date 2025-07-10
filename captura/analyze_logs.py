#!/usr/bin/env python3
"""
Analisador de Logs de Captura
Ferramenta para analisar onde o bot está parando
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

def load_session_files(capture_dir: Path):
    """Carrega todos os arquivos de sessão"""
    sessions = []
    
    for file_path in capture_dir.glob("session_*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                sessions.append(session_data)
        except Exception as e:
            print(f"❌ Erro ao carregar {file_path}: {e}")
    
    return sessions

def analyze_user_journey(user_id: str, sessions: list):
    """Analisa a jornada de um usuário específico"""
    user_sessions = [s for s in sessions if s['user_id'] == user_id]
    
    if not user_sessions:
        print(f"❌ Nenhuma sessão encontrada para usuário {user_id}")
        return
    
    print(f"\n🔍 ANÁLISE DETALHADA - USUÁRIO {user_id}")
    print("=" * 60)
    
    for i, session in enumerate(user_sessions, 1):
        print(f"\n📋 SESSÃO {i} - {session.get('start_time', 'N/A')}")
        print(f"   Duração: {session.get('duration_seconds', 0):.1f}s")
        print(f"   Estado Final: {session.get('current_state', 'N/A')}")
        print(f"   Total de Passos: {session.get('total_steps', 0)}")
        print(f"   Total de Erros: {session.get('total_errors', 0)}")
        
        if session.get('errors'):
            print(f"\n   🚨 ERROS ENCONTRADOS:")
            for error in session['errors']:
                print(f"      - {error.get('error', 'N/A')}")
        
        print(f"\n   📝 PASSOS DA JORNADA:")
        for j, step in enumerate(session.get('steps', []), 1):
            status = "✅" if step.get('success', True) else "❌"
            print(f"      {j:2d}. {status} {step.get('step', 'N/A')}")
            
            if step.get('data'):
                data = step['data']
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key in ['message_text', 'currency', 'network', 'amount', 'payment_method']:
                            print(f"          {key}: {value}")
        
        # Mostrar onde parou
        last_step = session.get('steps', [])[-1] if session.get('steps') else None
        if last_step:
            print(f"\n   🛑 ÚLTIMO PASSO: {last_step.get('step', 'N/A')}")
            if not last_step.get('success', True):
                print(f"      ❌ Falhou neste passo!")

def find_common_stopping_points(sessions: list):
    """Encontra pontos comuns onde usuários param"""
    stopping_points = {}
    
    for session in sessions:
        steps = session.get('steps', [])
        if steps:
            last_step = steps[-1]
            step_name = last_step.get('step', 'UNKNOWN')
            
            if step_name not in stopping_points:
                stopping_points[step_name] = {
                    'count': 0,
                    'users': set(),
                    'success_rate': 0,
                    'failed_count': 0
                }
            
            stopping_points[step_name]['count'] += 1
            stopping_points[step_name]['users'].add(session.get('user_id'))
            
            if not last_step.get('success', True):
                stopping_points[step_name]['failed_count'] += 1
    
    # Calcular taxa de sucesso
    for point in stopping_points.values():
        if point['count'] > 0:
            point['success_rate'] = (point['count'] - point['failed_count']) / point['count'] * 100
        point['users'] = len(point['users'])
    
    return stopping_points

def analyze_flow_patterns(sessions: list):
    """Analisa padrões de fluxo"""
    flow_patterns = {}
    
    for session in sessions:
        steps = session.get('steps', [])
        
        # Criar sequência de passos
        sequence = []
        for step in steps:
            step_name = step.get('step', 'UNKNOWN')
            if step.get('success', True):
                sequence.append(step_name)
            else:
                sequence.append(f"FAILED_{step_name}")
                break  # Parar na primeira falha
        
        # Registrar padrão
        pattern_key = " → ".join(sequence)
        if pattern_key not in flow_patterns:
            flow_patterns[pattern_key] = {
                'count': 0,
                'users': set(),
                'avg_duration': 0,
                'total_duration': 0
            }
        
        flow_patterns[pattern_key]['count'] += 1
        flow_patterns[pattern_key]['users'].add(session.get('user_id'))
        flow_patterns[pattern_key]['total_duration'] += session.get('duration_seconds', 0)
    
    # Calcular médias
    for pattern in flow_patterns.values():
        if pattern['count'] > 0:
            pattern['avg_duration'] = pattern['total_duration'] / pattern['count']
        pattern['users'] = len(pattern['users'])
    
    return flow_patterns

def main():
    parser = argparse.ArgumentParser(description="Analisar logs de captura do bot")
    parser.add_argument("--user", help="Analisar usuário específico")
    parser.add_argument("--summary", action="store_true", help="Mostrar resumo geral")
    parser.add_argument("--patterns", action="store_true", help="Mostrar padrões de fluxo")
    parser.add_argument("--stopping", action="store_true", help="Mostrar pontos onde usuários param")
    
    args = parser.parse_args()
    
    # Carregar dados
    capture_dir = Path(__file__).parent
    sessions = load_session_files(capture_dir)
    
    if not sessions:
        print("❌ Nenhuma sessão encontrada!")
        return
    
    print(f"📊 Carregadas {len(sessions)} sessões")
    
    if args.user:
        analyze_user_journey(args.user, sessions)
    
    if args.summary or not any([args.user, args.patterns, args.stopping]):
        print(f"\n📈 RESUMO GERAL")
        print("=" * 40)
        
        total_users = len(set(s.get('user_id') for s in sessions))
        total_errors = sum(s.get('total_errors', 0) for s in sessions)
        avg_duration = sum(s.get('duration_seconds', 0) for s in sessions) / len(sessions)
        
        print(f"Total de usuários únicos: {total_users}")
        print(f"Total de sessões: {len(sessions)}")
        print(f"Total de erros: {total_errors}")
        print(f"Duração média da sessão: {avg_duration:.1f}s")
        
        # Estados finais mais comuns
        final_states = {}
        for session in sessions:
            state = session.get('current_state', 'UNKNOWN')
            final_states[state] = final_states.get(state, 0) + 1
        
        print(f"\n🏁 ESTADOS FINAIS MAIS COMUNS:")
        for state, count in sorted(final_states.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {state}: {count} sessões")
    
    if args.stopping:
        stopping_points = find_common_stopping_points(sessions)
        
        print(f"\n🛑 PONTOS ONDE USUÁRIOS PARAM")
        print("=" * 50)
        
        for step, data in sorted(stopping_points.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
            print(f"{step}:")
            print(f"   Ocorrências: {data['count']}")
            print(f"   Usuários únicos: {data['users']}")
            print(f"   Taxa de sucesso: {data['success_rate']:.1f}%")
            if data['failed_count'] > 0:
                print(f"   ❌ Falhas: {data['failed_count']}")
            print()
    
    if args.patterns:
        flow_patterns = analyze_flow_patterns(sessions)
        
        print(f"\n🔄 PADRÕES DE FLUXO")
        print("=" * 50)
        
        for pattern, data in sorted(flow_patterns.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
            print(f"Padrão ({data['count']} ocorrências, {data['users']} usuários):")
            print(f"   {pattern}")
            print(f"   Duração média: {data['avg_duration']:.1f}s")
            print()

if __name__ == "__main__":
    main()
