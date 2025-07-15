#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se o Stateless Function está rodando continuamente
"""

import sys
import os
import time
import logging

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_continuous.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_continuous_execution():
    """Testa se há execução contínua do Stateless Function"""
    
    logger.info("🧪 INICIANDO TESTE DE EXECUÇÃO CONTÍNUA")
    
    # Monitora por 30 segundos
    start_time = time.time()
    duration = 30
    
    logger.info(f"⏰ Monitorando por {duration} segundos...")
    
    while time.time() - start_time < duration:
        current_time = time.time() - start_time
        logger.info(f"⏱️ Tempo decorrido: {current_time:.1f}s")
        
        # Verifica se há processos ativos
        try:
            import psutil
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            
            if children:
                logger.info(f"👥 Processos filhos ativos: {len(children)}")
                for child in children:
                    logger.info(f"   - PID {child.pid}: {child.name()}")
            else:
                logger.info("👤 Nenhum processo filho ativo")
                
        except ImportError:
            logger.info("📦 psutil não disponível, pulando verificação de processos")
        
        time.sleep(5)  # Verifica a cada 5 segundos
    
    logger.info("✅ TESTE DE EXECUÇÃO CONTÍNUA CONCLUÍDO")
    
    # Verifica logs recentes
    if os.path.exists('logs/pedido_manager.log'):
        logger.info("📝 Verificando logs do pedido_manager...")
        with open('logs/pedido_manager.log', 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-20:]  # Últimas 20 linhas
            logger.info("📄 Últimas linhas do log:")
            for line in recent_lines:
                logger.info(f"   {line.strip()}")
    else:
        logger.info("⚠️ Arquivo de log não encontrado")

if __name__ == "__main__":
    test_continuous_execution() 