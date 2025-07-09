#!/usr/bin/env python3
"""
Gerenciador de Limites por Usuário
Sistema de controle de limites baseado em chatid com banco de dados SQLite local.
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Dict, Optional, Tuple
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GerenciadorLimites:
    """
    Gerencia os limites de compra por usuário (chatid).
    """
    
    def __init__(self, db_path: str = "data/limites.db"):
        """
        Inicializa o gerenciador de limites.
        
        Args:
            db_path (str): Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados e cria as tabelas necessárias."""
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Conecta ao banco e cria as tabelas
            with sqlite3.connect(self.db_path) as conn:
                # Lê e executa o schema
                schema_path = os.path.join(os.path.dirname(__file__), "data", "schema.sql")
                if os.path.exists(schema_path):
                    with open(schema_path, 'r') as f:
                        conn.executescript(f.read())
                else:
                    # Schema inline caso o arquivo não exista
                    conn.executescript("""
                        CREATE TABLE IF NOT EXISTS chatid_limites (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            chatid TEXT UNIQUE NOT NULL,
                            num_compras INTEGER DEFAULT 0,
                            limite_atual REAL DEFAULT 500.00,
                            tem_cpf BOOLEAN DEFAULT FALSE,
                            cpf TEXT DEFAULT NULL,
                            primeiro_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            total_comprado REAL DEFAULT 0.00,
                            compras_hoje INTEGER DEFAULT 0,
                            ultimo_reset_diario DATE DEFAULT CURRENT_DATE
                        );
                        CREATE INDEX IF NOT EXISTS idx_chatid ON chatid_limites(chatid);
                        CREATE INDEX IF NOT EXISTS idx_ultimo_reset ON chatid_limites(ultimo_reset_diario);
                    """)
                conn.commit()
                logger.info("✅ Banco de dados inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            raise
    
    def obter_ou_criar_usuario(self, chatid: str) -> Dict:
        """
        Obtém os dados do usuário ou cria um novo registro.
        
        Args:
            chatid (str): ID do chat do usuário
            
        Returns:
            Dict: Dados do usuário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Verifica se o usuário já existe
                cursor.execute("SELECT * FROM chatid_limites WHERE chatid = ?", (chatid,))
                usuario = cursor.fetchone()
                
                if usuario:
                    # Converte Row para dict
                    usuario_dict = dict(usuario)
                    
                    # Verifica se precisa resetar o limite diário
                    hoje = date.today().isoformat()
                    if usuario_dict['ultimo_reset_diario'] != hoje:
                        cursor.execute("""
                            UPDATE chatid_limites 
                            SET compras_hoje = 0, ultimo_reset_diario = ?
                            WHERE chatid = ?
                        """, (hoje, chatid))
                        conn.commit()
                        usuario_dict['compras_hoje'] = 0
                        usuario_dict['ultimo_reset_diario'] = hoje
                    
                    return usuario_dict
                else:
                    # Cria novo usuário
                    cursor.execute("""
                        INSERT INTO chatid_limites (chatid, num_compras, limite_atual, tem_cpf)
                        VALUES (?, 0, 500.00, FALSE)
                    """, (chatid,))
                    conn.commit()
                    
                    # Busca o usuário recém-criado
                    cursor.execute("SELECT * FROM chatid_limites WHERE chatid = ?", (chatid,))
                    usuario = cursor.fetchone()
                    return dict(usuario)
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter/criar usuário {chatid}: {e}")
            raise
    
    def calcular_limite_usuario(self, chatid: str, cpf: Optional[str] = None) -> Tuple[float, bool]:
        """
        Calcula o limite atual do usuário baseado no histórico.
        
        Args:
            chatid (str): ID do chat do usuário
            cpf (str, optional): CPF do usuário
            
        Returns:
            Tuple[float, bool]: (limite_atual, precisa_cpf)
        """
        try:
            usuario = self.obter_ou_criar_usuario(chatid)
            
            # Se tem CPF válido, libera limite máximo
            if cpf and self.validar_cpf(cpf):
                return 4999.99, False
            
            # Se já tem CPF salvo, usa limite máximo
            if usuario['tem_cpf']:
                return 4999.99, False
            
            # Calcula limite baseado no número de compras
            from limites.limite_valor import LimitesValor
            
            num_compras = usuario['num_compras']
            limite_progressivo = LimitesValor.calcular_limite_progressivo(num_compras)
            
            # Primeira compra sempre R$ 500,00
            if num_compras == 0:
                return 500.00, False
            
            # Demais compras seguem a escada
            return limite_progressivo, limite_progressivo < 4999.99
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular limite para {chatid}: {e}")
            return 500.00, False
    
    def validar_compra_usuario(self, chatid: str, valor: float, cpf: Optional[str] = None) -> Dict:
        """
        Valida se o usuário pode fazer a compra com o valor informado.
        
        Args:
            chatid (str): ID do chat do usuário
            valor (float): Valor da compra
            cpf (str, optional): CPF do usuário
            
        Returns:
            Dict: Resultado da validação
        """
        try:
            # Primeiro, valida limites PIX básicos
            from limites.limite_valor import LimitesValor
            
            validacao_pix = LimitesValor.validar_pix_compra(valor)
            if not validacao_pix['valido']:
                return validacao_pix
            
            # Obtém dados do usuário
            usuario = self.obter_ou_criar_usuario(chatid)
            
            # Calcula limite atual
            limite_atual, precisa_cpf = self.calcular_limite_usuario(chatid, cpf)
            
            # Verifica se valor está dentro do limite
            if valor > limite_atual:
                return {
                    "valido": False,
                    "erro": "LIMITE_DIARIO",
                    "mensagem": f"Limite diário: R$ {limite_atual:.2f}",
                    "dica": f"Digite um valor até R$ {limite_atual:.2f}" + (
                        " ou forneça seu CPF para aumentar o limite" if precisa_cpf else ""
                    ),
                    "limite_atual": limite_atual,
                    "num_compras": usuario['num_compras'],
                    "precisa_cpf": precisa_cpf,
                    "primeira_compra": usuario['num_compras'] == 0
                }
            
            return {
                "valido": True,
                "mensagem": "Compra aprovada",
                "limite_atual": limite_atual,
                "num_compras": usuario['num_compras'],
                "precisa_cpf": False,
                "primeira_compra": usuario['num_compras'] == 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao validar compra para {chatid}: {e}")
            return {
                "valido": False,
                "erro": "ERRO_SISTEMA",
                "mensagem": "Erro interno do sistema",
                "dica": "Tente novamente em alguns instantes"
            }
    
    def registrar_compra(self, chatid: str, valor: float, cpf: Optional[str] = None):
        """
        Registra uma compra realizada pelo usuário.
        
        Args:
            chatid (str): ID do chat do usuário
            valor (float): Valor da compra
            cpf (str, optional): CPF do usuário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Atualiza dados do usuário
                tem_cpf = cpf is not None and self.validar_cpf(cpf)
                
                cursor.execute("""
                    UPDATE chatid_limites 
                    SET num_compras = num_compras + 1,
                        total_comprado = total_comprado + ?,
                        compras_hoje = compras_hoje + 1,
                        ultima_atualizacao = CURRENT_TIMESTAMP,
                        tem_cpf = ?,
                        cpf = ?
                    WHERE chatid = ?
                """, (valor, tem_cpf, cpf if tem_cpf else None, chatid))
                
                conn.commit()
                logger.info(f"✅ Compra registrada para {chatid}: R$ {valor:.2f}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar compra para {chatid}: {e}")
            raise
    
    def validar_cpf(self, cpf: str) -> bool:
        """
        Valida CPF usando o algoritmo padrão.
        
        Args:
            cpf (str): CPF a ser validado
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            from limites.limite_valor import LimitesValor
            return LimitesValor.validar_cpf_basico(cpf)
        except Exception as e:
            logger.error(f"❌ Erro ao validar CPF: {e}")
            return False
    
    def obter_estatisticas_usuario(self, chatid: str) -> Dict:
        """
        Obtém estatísticas do usuário.
        
        Args:
            chatid (str): ID do chat do usuário
            
        Returns:
            Dict: Estatísticas do usuário
        """
        try:
            usuario = self.obter_ou_criar_usuario(chatid)
            limite_atual, precisa_cpf = self.calcular_limite_usuario(chatid, usuario.get('cpf'))
            
            return {
                "num_compras": usuario['num_compras'],
                "limite_atual": limite_atual,
                "total_comprado": usuario['total_comprado'],
                "compras_hoje": usuario['compras_hoje'],
                "tem_cpf": bool(usuario['tem_cpf']),
                "precisa_cpf": precisa_cpf,
                "primeira_compra": usuario['num_compras'] == 0,
                "membro_desde": usuario['primeiro_acesso']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas para {chatid}: {e}")
            return {}

# Instância global do gerenciador
gerenciador_limites = GerenciadorLimites()

# Funções de conveniência
def validar_compra_usuario(chatid: str, valor: float, cpf: Optional[str] = None) -> Dict:
    """Função de conveniência para validar compra de usuário."""
    return gerenciador_limites.validar_compra_usuario(chatid, valor, cpf)

def registrar_compra_usuario(chatid: str, valor: float, cpf: Optional[str] = None):
    """Função de conveniência para registrar compra de usuário."""
    return gerenciador_limites.registrar_compra(chatid, valor, cpf)

def obter_estatisticas_usuario(chatid: str) -> Dict:
    """Função de conveniência para obter estatísticas de usuário."""
    return gerenciador_limites.obter_estatisticas_usuario(chatid)

def obter_limite_atual_usuario(chatid: str, cpf: Optional[str] = None) -> float:
    """Função de conveniência para obter limite atual de usuário."""
    limite, _ = gerenciador_limites.calcular_limite_usuario(chatid, cpf)
    return limite
