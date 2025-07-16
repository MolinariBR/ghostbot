"""
Rate Limiter - Controle de taxa de requisições
=============================================

Este módulo fornece um limitador de taxa assíncrono para proteger
contra spam e abuso no bot do Telegram.
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Limitador de taxa assíncrono para bot do Telegram.
    
    Protege contra:
    - Spam de mensagens
    - Abuso de comandos
    - Ataques de DDoS
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Inicializa o RateLimiter.
        
        Args:
            max_requests: Número máximo de requisições por janela
            window_seconds: Tamanho da janela em segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.lock = asyncio.Lock()
        self.requests: Dict[str, deque] = defaultdict(deque)
        
        logger.info(f"✅ RateLimiter inicializado: {max_requests} req/{window_seconds}s")
    
    async def is_allowed(self, user_id: str, action: str = "default") -> bool:
        """
        Verifica se uma requisição é permitida.
        
        Args:
            user_id: ID do usuário
            action: Tipo de ação (comando, mensagem, etc.)
            
        Returns:
            True se permitido, False se bloqueado
        """
        async with self.lock:
            key = f"{user_id}:{action}"
            now = time.time()
            
            # Limpar requisições antigas
            while self.requests[key] and now - self.requests[key][0] > self.window_seconds:
                self.requests[key].popleft()
            
            # Verificar se ainda há espaço na janela
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True
            
            logger.warning(f"🚫 Rate limit excedido: user_id={user_id}, action={action}")
            return False
    
    async def get_remaining_time(self, user_id: str, action: str = "default") -> float:
        """
        Obtém o tempo restante até a próxima requisição permitida.
        
        Args:
            user_id: ID do usuário
            action: Tipo de ação
            
        Returns:
            Tempo restante em segundos
        """
        async with self.lock:
            key = f"{user_id}:{action}"
            now = time.time()
            
            # Limpar requisições antigas
            while self.requests[key] and now - self.requests[key][0] > self.window_seconds:
                self.requests[key].popleft()
            
            if len(self.requests[key]) < self.max_requests:
                return 0.0
            
            # Calcular tempo restante
            oldest_request = self.requests[key][0]
            return max(0.0, self.window_seconds - (now - oldest_request))
    
    async def reset_user(self, user_id: str) -> None:
        """
        Reseta o rate limit para um usuário específico.
        
        Args:
            user_id: ID do usuário
        """
        async with self.lock:
            # Remover todas as ações do usuário
            keys_to_remove = [key for key in self.requests.keys() if key.startswith(f"{user_id}:")]
            for key in keys_to_remove:
                del self.requests[key]
            
            logger.info(f"🔄 Rate limit resetado para usuário: {user_id}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do RateLimiter.
        
        Returns:
            Dicionário com estatísticas
        """
        async with self.lock:
            total_requests = sum(len(requests) for requests in self.requests.values())
            active_users = len(set(key.split(':')[0] for key in self.requests.keys()))
            
            return {
                'total_requests': total_requests,
                'active_users': active_users,
                'max_requests': self.max_requests,
                'window_seconds': self.window_seconds,
                'user_requests': {key: len(requests) for key, requests in self.requests.items()}
            }

# Instância global do RateLimiter
rate_limiter = RateLimiter()

# Decorator para aplicar rate limiting
def rate_limit(max_requests: int = 10, window_seconds: int = 60, action: str = "default"):
    """
    Decorator para aplicar rate limiting em handlers.
    
    Args:
        max_requests: Número máximo de requisições
        window_seconds: Janela de tempo em segundos
        action: Nome da ação para rate limiting
    """
    def decorator(func):
        async def wrapper(update, context):
            user_id = str(update.effective_user.id) if update.effective_user else "unknown"
            
            # Verificar rate limit
            if not await rate_limiter.is_allowed(user_id, action):
                remaining_time = await rate_limiter.get_remaining_time(user_id, action)
                
                await update.message.reply_text(
                    f"⏳ **Muitas requisições!**\n\n"
                    f"🔄 Aguarde {int(remaining_time)} segundos antes de tentar novamente.\n\n"
                    f"💡 Isso protege nosso sistema contra spam.",
                    parse_mode='Markdown'
                )
                return
            
            # Executar função original
            return await func(update, context)
        
        return wrapper
    return decorator 