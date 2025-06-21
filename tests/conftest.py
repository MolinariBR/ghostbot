"""
Configurações globais para os testes.
"""
import os
import sys
import pytest
from pathlib import Path

# Adiciona o diretório raiz ao path do Python
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuração de logging para testes
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Fixtures comuns podem ser definidas aqui

@pytest.fixture(autouse=True)
def setup_teardown():
    """Executa antes e depois de cada teste."""
    # Setup: código que roda antes de cada teste
    logger.info("Iniciando teste...")
    
    yield  # aqui o teste é executado
    
    # Teardown: código que roda depois de cada teste
    logger.info("Teste finalizado")
