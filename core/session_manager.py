"""
SessionManager - Gerenciamento seguro de sessões de usuário
==========================================================

Este módulo fornece um gerenciador de sessões assíncrono que protege
contra colisões entre usuários simultâneos e garante consistência
de estado.
"""

from collections import defaultdict
import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Gerenciador de sessões assíncrono para bot do Telegram.
    
    Protege contra:
    - Colisões entre usuários simultâneos
    - Estados corrompidos
    - Vazamentos de memória (TTL automático)
    """
    
    def __init__(self, ttl_hours: int = 24):
        """
        Inicializa o SessionManager.
        
        Args:
            ttl_hours: Tempo de vida das sessões em horas (padrão: 24h)
        """
        self.lock = asyncio.Lock()
        self.sessions: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.timestamps: Dict[str, datetime] = {}
        self.ttl_hours = ttl_hours
        
        logger.info(f"✅ SessionManager inicializado com TTL de {ttl_hours}h")
    
    async def get(self, user_id: str, key: str, default: Any = None) -> Any:
        """
        Obtém um valor da sessão do usuário de forma segura.
        
        Args:
            user_id: ID do usuário
            key: Chave do valor
            default: Valor padrão se não encontrado
            
        Returns:
            Valor da sessão ou default
        """
        async with self.lock:
            # Limpar sessões expiradas
            await self._cleanup_expired_sessions()
            
            user_sessions = self.sessions.get(str(user_id), {})
            value = user_sessions.get(key, default)
            
            if value is not None:
                logger.debug(f"📖 Sessão lida: user_id={user_id}, key={key}")
            
            return value
    
    async def set(self, user_id: str, key: str, value: Any) -> None:
        """
        Define um valor na sessão do usuário de forma segura.
        
        Args:
            user_id: ID do usuário
            key: Chave do valor
            value: Valor a ser armazenado
        """
        async with self.lock:
            user_id_str = str(user_id)
            
            # Atualizar timestamp da sessão
            self.timestamps[user_id_str] = datetime.now()
            
            # Armazenar valor
            self.sessions[user_id_str][key] = value
            
            logger.debug(f"💾 Sessão salva: user_id={user_id}, key={key}")
    
    async def clear(self, user_id: str) -> None:
        """
        Limpa toda a sessão do usuário.
        
        Args:
            user_id: ID do usuário
        """
        async with self.lock:
            user_id_str = str(user_id)
            
            if user_id_str in self.sessions:
                del self.sessions[user_id_str]
            
            if user_id_str in self.timestamps:
                del self.timestamps[user_id_str]
            
            logger.info(f"🗑️ Sessão limpa: user_id={user_id}")
    
    async def delete(self, user_id: str, key: str) -> bool:
        """
        Remove uma chave específica da sessão do usuário.
        
        Args:
            user_id: ID do usuário
            key: Chave a ser removida
            
        Returns:
            True se a chave foi removida, False se não existia
        """
        async with self.lock:
            user_id_str = str(user_id)
            user_sessions = self.sessions.get(user_id_str, {})
            
            if key in user_sessions:
                del user_sessions[key]
                logger.debug(f"🗑️ Chave removida: user_id={user_id}, key={key}")
                return True
            
            return False
    
    async def exists(self, user_id: str, key: str) -> bool:
        """
        Verifica se uma chave existe na sessão do usuário.
        
        Args:
            user_id: ID do usuário
            key: Chave a ser verificada
            
        Returns:
            True se a chave existe, False caso contrário
        """
        async with self.lock:
            await self._cleanup_expired_sessions()
            
            user_sessions = self.sessions.get(str(user_id), {})
            return key in user_sessions
    
    async def get_all(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém todas as chaves da sessão do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com todas as chaves e valores
        """
        async with self.lock:
            await self._cleanup_expired_sessions()
            
            user_sessions = self.sessions.get(str(user_id), {})
            return user_sessions.copy()
    
    async def _cleanup_expired_sessions(self) -> None:
        """
        Remove sessões expiradas automaticamente.
        """
        now = datetime.now()
        expired_users = []
        
        for user_id, timestamp in self.timestamps.items():
            if now - timestamp > timedelta(hours=self.ttl_hours):
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.sessions[user_id]
            del self.timestamps[user_id]
            logger.debug(f"🧹 Sessão expirada removida: user_id={user_id}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do SessionManager.
        
        Returns:
            Dicionário com estatísticas
        """
        async with self.lock:
            await self._cleanup_expired_sessions()
            
            return {
                'total_sessions': len(self.sessions),
                'total_timestamps': len(self.timestamps),
                'ttl_hours': self.ttl_hours,
                'session_keys': {user_id: len(sessions) for user_id, sessions in self.sessions.items()}
            }

# Instância global do SessionManager
session_manager = SessionManager()

# Funções de conveniência para compatibilidade
async def get_user_data(user_id: str, key: str, default: Any = None) -> Any:
    """Função de conveniência para obter dados do usuário."""
    return await session_manager.get(user_id, key, default)

async def set_user_data(user_id: str, key: str, value: Any) -> None:
    """Função de conveniência para definir dados do usuário."""
    await session_manager.set(user_id, key, value)

async def clear_user_data(user_id: str) -> None:
    """Função de conveniência para limpar dados do usuário."""
    await session_manager.clear(user_id) 