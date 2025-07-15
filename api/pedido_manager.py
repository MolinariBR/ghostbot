"""
Gerenciador de Pedidos - Salva pedidos no banco e ativa validação de pagamento
"""

import asyncio
import sqlite3
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from core.validador_depix import ValidadorDepix

# Configuração de logging
logger = logging.getLogger(__name__)

# Configuração adicional para debug
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pedido_manager.log'),
        logging.StreamHandler()
    ]
)

class PedidoManager:
    """Gerencia pedidos e validação de pagamento PIX."""
    
    def __init__(self, db_path: str = "data/pedidos.db"):
        """
        Inicializa o gerenciador de pedidos.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        logger.debug(f"🔧 Inicializando PedidoManager com db_path: {db_path}")
        self.db_path = db_path
        
        logger.debug("🔑 Inicializando ValidadorDepix...")
        self.validador = ValidadorDepix(api_key="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0")
        logger.debug("✅ ValidadorDepix inicializado com sucesso")
        
        # Cria a tabela se não existir
        logger.debug("🗄️ Criando/verificando tabela de pedidos...")
        self._criar_tabela()
        logger.debug("✅ PedidoManager inicializado com sucesso")
    
    def _criar_tabela(self):
        """Cria a tabela de pedidos se não existir."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedidos_bot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gtxid TEXT NOT NULL,
                    chatid TEXT NOT NULL,
                    moeda TEXT NOT NULL,
                    rede TEXT NOT NULL,
                    valor REAL NOT NULL,
                    comissao REAL NOT NULL,
                    parceiro REAL NOT NULL,
                    cotacao REAL NOT NULL,
                    recebe REAL NOT NULL,
                    forma_pagamento TEXT NOT NULL,
                    depix_id TEXT,
                    status TEXT DEFAULT 'novo',
                    pagamento_verificado INTEGER DEFAULT 0,
                    tentativas_verificacao INTEGER DEFAULT 0,
                    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Tabela pedidos_bot criada/verificada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar tabela: {e}")
    
    def salvar_pedido(self, dados_pedido: Dict[str, Any]) -> bool:
        """
        Salva um pedido no banco de dados.
        
        Args:
            dados_pedido: Dicionário com os dados do pedido
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        logger.debug(f"💾 Iniciando salvamento do pedido: {dados_pedido.get('gtxid')}")
        logger.debug(f"📊 Dados do pedido: {dados_pedido}")
        
        try:
            logger.debug(f"🔗 Conectando ao banco: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Dados para inserção
            dados_insercao = (
                dados_pedido.get('gtxid'),
                dados_pedido.get('chatid'),
                dados_pedido.get('moeda', 'BTC'),
                dados_pedido.get('rede', 'Lightning'),
                dados_pedido.get('valor'),
                dados_pedido.get('comissao'),
                dados_pedido.get('parceiro'),
                dados_pedido.get('cotacao'),
                dados_pedido.get('recebe'),
                dados_pedido.get('forma_pagamento', 'PIX'),
                'novo'
            )
            
            logger.debug(f"📝 Executando INSERT com dados: {dados_insercao}")
            
            cursor.execute("""
                INSERT INTO pedidos_bot (
                    gtxid, chatid, moeda, rede, valor, comissao, parceiro, 
                    cotacao, recebe, forma_pagamento, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, dados_insercao)
            
            logger.debug("💾 Commitando transação...")
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Pedido salvo com sucesso: {dados_pedido.get('gtxid')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar pedido: {e}")
            logger.error(f"📊 Dados que falharam: {dados_pedido}")
            return False
    
    async def verificar_pagamento_background(self, depix_id: str, gtxid: str, chatid: str, max_tentativas: int = 5):
        """
        Verifica pagamento em background (stateless function).
        
        Args:
            depix_id: ID do depósito PIX
            gtxid: ID do pedido
            chatid: ID do chat do usuário
            max_tentativas: Número máximo de tentativas (padrão: 5)
        """
        logger.info(f"🚀 INICIANDO STATELESS FUNCTION - Verificação de pagamento")
        logger.info(f"📋 Parâmetros: depix_id={depix_id}, gtxid={gtxid}, chatid={chatid}, max_tentativas={max_tentativas}")
        
        for tentativa in range(1, max_tentativas + 1):
            try:
                logger.info(f"🔄 TENTATIVA {tentativa}/{max_tentativas} - Iniciando verificação...")
                logger.debug(f"🔍 Consultando depósito: {depix_id}")
                
                # Consulta o status do pagamento
                logger.debug("📡 Fazendo requisição para API Depix...")
                resultado = await self.validador.consultar_deposito(depix_id)
                logger.debug(f"📥 Resposta da API: {resultado}")
                
                if resultado.get('success'):
                    status = resultado.get('status', 'unknown')
                    logger.info(f"✅ Status do pagamento: {status}")
                    logger.debug(f"📊 Dados completos da resposta: {resultado}")
                    
                    # Atualiza o banco com o status
                    logger.debug(f"💾 Atualizando status no banco: {status}")
                    self._atualizar_status_pedido(gtxid, status, tentativa)
                    
                    # Se o pagamento foi confirmado, para as verificações
                    if status in ['paid', 'completed', 'confirmed', 'depix_confirmed']:
                        logger.info(f"🎉 PAGAMENTO CONFIRMADO! Parando verificações. Status: {status}")
                        break
                    else:
                        logger.info(f"⏳ Pagamento ainda pendente. Status: {status}")
                    
                else:
                    error_msg = resultado.get('error', 'Erro desconhecido')
                    logger.warning(f"⚠️ Erro na verificação {tentativa}: {error_msg}")
                    logger.debug(f"❌ Resposta de erro completa: {resultado}")
                    self._atualizar_status_pedido(gtxid, 'erro_verificacao', tentativa)
                
                # Aguarda 30 segundos antes da próxima verificação
                if tentativa < max_tentativas:
                    logger.info(f"⏰ Aguardando 30 segundos antes da próxima tentativa...")
                    await asyncio.sleep(30)
                    
            except Exception as e:
                logger.error(f"💥 ERRO CRÍTICO na tentativa {tentativa}: {e}")
                logger.error(f"📋 Detalhes do erro: {type(e).__name__}: {str(e)}")
                self._atualizar_status_pedido(gtxid, 'erro_verificacao', tentativa)
                
                if tentativa < max_tentativas:
                    logger.info(f"⏰ Aguardando 30 segundos após erro...")
                    await asyncio.sleep(30)
        
        logger.info(f"🏁 VERIFICAÇÃO CONCLUÍDA para gtxid: {gtxid}")
        logger.info(f"📊 Total de tentativas realizadas: {max_tentativas}")
    
    def _atualizar_status_pedido(self, gtxid: str, status: str, tentativa: int):
        """
        Atualiza o status do pedido no banco de dados.
        
        Args:
            gtxid: ID do pedido
            status: Novo status
            tentativa: Número da tentativa
        """
        logger.debug(f"💾 Atualizando status: gtxid={gtxid}, status={status}, tentativa={tentativa}")
        
        try:
            logger.debug(f"🔗 Conectando ao banco para atualização...")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logger.debug(f"📝 Executando UPDATE...")
            cursor.execute("""
                UPDATE pedidos_bot 
                SET status = ?, tentativas_verificacao = ?, atualizado_em = CURRENT_TIMESTAMP
                WHERE gtxid = ?
            """, (status, tentativa, gtxid))
            
            rows_affected = cursor.rowcount
            logger.debug(f"📊 Linhas afetadas: {rows_affected}")
            
            logger.debug("💾 Commitando atualização...")
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Status atualizado para gtxid {gtxid}: {status} (tentativa {tentativa})")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar status do pedido {gtxid}: {e}")
            logger.error(f"📋 Detalhes: status={status}, tentativa={tentativa}")

print("\033[1;34m💤 STATELESS FUNCTION AGUARDANDO EVENTO DE COMPRA...\033[0m", file=sys.stderr)

# Instância global
logger.info("🌍 CRIANDO INSTÂNCIA GLOBAL DO PEDIDO MANAGER...")
pedido_manager = PedidoManager()
logger.info("✅ INSTÂNCIA GLOBAL CRIADA COM SUCESSO")
logger.info("💤 STATELESS FUNCTION AGUARDANDO ATIVAÇÃO...")

async def processar_pedido_completo(dados_pedido: Dict[str, Any], depix_id: str):
    """
    Função stateless para processar pedido completo.
    
    Args:
        dados_pedido: Dados do pedido para salvar no banco
        depix_id: ID do depósito PIX para verificação
    """
    logger.info(f"🚀 INICIANDO PROCESSAMENTO COMPLETO DO PEDIDO")
    logger.info(f"📋 Parâmetros recebidos: depix_id={depix_id}")
    logger.debug(f"📊 Dados do pedido: {dados_pedido}")
    
    try:
        # 1. Salva o pedido no banco
        logger.info("💾 ETAPA 1: Salvando pedido no banco...")
        sucesso_salvamento = pedido_manager.salvar_pedido(dados_pedido)
        
        if not sucesso_salvamento:
            logger.error("❌ Falha ao salvar pedido no banco - ABORTANDO PROCESSAMENTO")
            return
        
        logger.info("✅ Pedido salvo com sucesso no banco")
        
        # 2. Inicia verificação de pagamento em background
        gtxid = dados_pedido.get('gtxid')
        chatid = dados_pedido.get('chatid')
        
        logger.info(f"🔄 ETAPA 2: Iniciando verificação de pagamento em background...")
        logger.info(f"📋 Parâmetros para verificação: gtxid={gtxid}, chatid={chatid}, depix_id={depix_id}")
        
        # Executa a verificação em background (não bloqueia)
        logger.debug("🎯 Criando task assíncrona para verificação...")
        task = asyncio.create_task(
            pedido_manager.verificar_pagamento_background(depix_id, gtxid, chatid)
        )
        logger.debug(f"✅ Task criada: {task}")
        
        logger.info(f"🎉 PEDIDO PROCESSADO COM SUCESSO: {gtxid}")
        logger.info(f"📊 Verificação de pagamento iniciada em background")
        
    except Exception as e:
        logger.error(f"💥 ERRO CRÍTICO ao processar pedido completo: {e}")
        logger.error(f"📋 Tipo do erro: {type(e).__name__}")
        logger.error(f"📊 Dados que causaram erro: {dados_pedido}")

# Função para uso direto
def salvar_e_verificar_pagamento(dados_pedido: Dict[str, Any], depix_id: str):
    """
    Função síncrona para salvar pedido e iniciar verificação de pagamento.
    
    Args:
        dados_pedido: Dados do pedido
        depix_id: ID do depósito PIX
    """
    print(f"\033[1;33m🔥🔥🔥 STATELESS FUNCTION ATIVADA POR EVENTO DE COMPRA! 🔥🔥🔥\033[0m", file=sys.stderr)
    logger.info(f"🚀 INICIANDO FUNÇÃO SÍNCRONA: salvar_e_verificar_pagamento")
    logger.info(f"📋 Parâmetros: depix_id={depix_id}")
    logger.debug(f"📊 Dados do pedido: {dados_pedido}")
    
    try:
        # 1. Salva o pedido no banco (síncrono)
        logger.info("💾 Salvando pedido no banco...")
        sucesso_salvamento = pedido_manager.salvar_pedido(dados_pedido)
        
        if not sucesso_salvamento:
            logger.error("❌ Falha ao salvar pedido no banco")
            return
        
        logger.info("✅ Pedido salvo com sucesso no banco")
        
        # 2. Inicia verificação em background usando threading
        import threading
        import time
        
        def verificar_em_background():
            """Função que roda em thread separada para verificação"""
            logger.info("🔄 Iniciando verificação em thread separada...")
            
            # Cria um novo loop para esta thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            
            try:
                gtxid = dados_pedido.get('gtxid')
                chatid = dados_pedido.get('chatid')
                
                logger.info(f"📋 Parâmetros para verificação: gtxid={gtxid}, chatid={chatid}, depix_id={depix_id}")
                
                # Executa a verificação
                new_loop.run_until_complete(
                    pedido_manager.verificar_pagamento_background(depix_id, gtxid, chatid)
                )
                
                logger.info("✅ Verificação em background concluída")
                
            except Exception as e:
                logger.error(f"💥 ERRO na verificação em background: {e}")
            finally:
                new_loop.close()
        
        # Inicia a thread de verificação
        logger.info("🧵 Iniciando thread de verificação...")
        thread = threading.Thread(target=verificar_em_background, daemon=True)
        thread.start()
        
        logger.info("✅ Função síncrona executada com sucesso")
        logger.info("📊 Verificação de pagamento iniciada em thread separada")
        
    except Exception as e:
        logger.error(f"💥 ERRO na função síncrona: {e}")
        logger.error(f"📋 Tipo do erro: {type(e).__name__}")
    
    logger.info("🏁 Função síncrona finalizada") 