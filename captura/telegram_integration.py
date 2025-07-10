#!/usr/bin/env python3
"""
Integração do Sistema de Captura com os Handlers do Bot
"""
import functools
from telegram import Update
from telegram.ext import ContextTypes
import logging

# Import relativo corrigido
try:
    from capture_system import capture_system
except ImportError:
    # Fallback para import absoluto
    from captura.capture_system import capture_system

logger = logging.getLogger('capture_integration')

def capture_telegram_handler(step_name: str = None, capture_context: bool = True):
    """
    Decorator específico para handlers do Telegram Bot
    
    Args:
        step_name: Nome do passo (se não fornecido, usa o nome da função)
        capture_context: Se deve capturar dados do contexto
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(update: Update, context, *args, **kwargs):
            # Extrair informações do usuário
            user = update.effective_user
            user_id = str(user.id) if user else "unknown"
            username = user.username if user else None
            first_name = user.first_name if user else None
            
            # Nome do passo
            actual_step_name = step_name or func.__name__
            
            # Dados da mensagem
            message_data = {}
            if update.message:
                message_data.update({
                    "message_text": update.message.text,
                    "message_id": update.message.message_id,
                    "chat_id": update.message.chat_id
                })
            
            if update.callback_query:
                message_data.update({
                    "callback_data": update.callback_query.data,
                    "callback_id": update.callback_query.id
                })
            
            # Dados do contexto
            context_data = {}
            if capture_context and hasattr(context, 'user_data'):
                context_data = dict(context.user_data)
            
            # Registrar início do handler
            capture_system.capture_conversation_state(
                user_id, 
                actual_step_name, 
                func.__name__
            )
            
            logger.info(f"🎯 [CAPTURE] Handler {actual_step_name} iniciado para {user_id}")
            
            try:
                # Executar handler original
                result = await func(update, context, *args, **kwargs)
                
                # Registrar sucesso
                session = capture_system.get_session(user_id)
                if session:
                    session.add_step(
                        f"HANDLER_{actual_step_name.upper()}", 
                        {
                            "message_data": message_data,
                            "context_data": context_data,
                            "result": str(result) if result is not None else None
                        },
                        success=True
                    )
                
                logger.info(f"✅ [CAPTURE] Handler {actual_step_name} concluído com sucesso para {user_id}")
                return result
                
            except Exception as e:
                # Registrar erro
                capture_system.capture_error(
                    user_id, 
                    f"HANDLER_ERROR_{actual_step_name.upper()}", 
                    str(e), 
                    e
                )
                
                logger.error(f"❌ [CAPTURE] Erro no handler {actual_step_name} para {user_id}: {e}")
                raise
                
        @functools.wraps(func)
        def sync_wrapper(update: Update, context, *args, **kwargs):
            # Para handlers síncronos (caso existam)
            user = update.effective_user
            user_id = str(user.id) if user else "unknown"
            actual_step_name = step_name or func.__name__
            
            capture_system.capture_conversation_state(user_id, actual_step_name, func.__name__)
            
            try:
                result = func(update, context, *args, **kwargs)
                session = capture_system.get_session(user_id)
                if session:
                    session.add_step(f"HANDLER_{actual_step_name.upper()}", success=True)
                return result
            except Exception as e:
                capture_system.capture_error(user_id, f"HANDLER_ERROR_{actual_step_name.upper()}", str(e), e)
                raise
        
        # Retornar wrapper apropriado baseado se a função é async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator

def capture_menu_compra_handler(step_name: str = None):
    """Decorator específico para handlers do menu de compra"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(update: Update, context, *args, **kwargs):
            user_id = str(update.effective_user.id)
            actual_step_name = step_name or func.__name__
            
            # Capturar dados específicos do menu de compra
            session = capture_system.get_session(user_id)
            if session and hasattr(context, 'user_data'):
                # Capturar dados importantes do contexto
                important_data = {}
                for key in ['moeda', 'rede', 'valor_brl', 'endereco_recebimento', 'metodo_pagamento', 'cpf']:
                    if key in context.user_data:
                        important_data[key] = context.user_data[key]
                
                session.add_step(f"COMPRA_{actual_step_name.upper()}", {
                    "context_data": important_data,
                    "message_text": update.message.text if update.message else None
                })
            
            try:
                result = await func(update, context, *args, **kwargs)
                
                # Capturar resultado
                if session:
                    session.add_step(f"COMPRA_{actual_step_name.upper()}_SUCCESS", {
                        "result": str(result) if result is not None else None
                    })
                
                return result
                
            except Exception as e:
                capture_system.capture_error(user_id, f"COMPRA_ERROR_{actual_step_name.upper()}", str(e), e)
                raise
                
        return wrapper
    return decorator

def capture_trigger_handler(event_name: str = None):
    """Decorator para handlers do sistema de gatilhos"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(chat_id: str, data: dict = None, *args, **kwargs):
            actual_event_name = event_name or func.__name__
            
            # Registrar evento
            capture_system.capture_trigger_event(chat_id, actual_event_name, data)
            
            try:
                result = func(chat_id, data, *args, **kwargs)
                
                # Registrar sucesso
                session = capture_system.get_session(chat_id)
                if session:
                    session.add_step(f"TRIGGER_{actual_event_name.upper()}_SUCCESS", {
                        "input_data": data,
                        "result": result
                    })
                
                return result
                
            except Exception as e:
                capture_system.capture_error(chat_id, f"TRIGGER_ERROR_{actual_event_name.upper()}", str(e), e)
                raise
                
        return wrapper
    return decorator

# ============================================================================
# FUNÇÕES DE INTEGRAÇÃO DIRETA
# ============================================================================

def capture_start_command(update: Update, context):
    """Captura comando /start"""
    user = update.effective_user
    user_id = str(user.id)
    username = user.username
    first_name = user.first_name
    
    capture_system.capture_start_command(user_id, username, first_name)

def capture_button_click(update: Update, button_text: str):
    """Captura clique em botão"""
    user_id = str(update.effective_user.id)
    capture_system.capture_menu_click(user_id, button_text)

def capture_text_input(update: Update, input_type: str, parsed_value=None, success: bool = True):
    """Captura entrada de texto"""
    user_id = str(update.effective_user.id)
    text = update.message.text if update.message else ""
    
    if input_type == "amount":
        capture_system.capture_amount_input(user_id, text, parsed_value, success)
    elif input_type == "address":
        capture_system.capture_address_input(user_id, text, "crypto_address")
    else:
        session = capture_system.get_session(user_id)
        if session:
            session.add_step(f"TEXT_INPUT_{input_type.upper()}", {
                "text": text,
                "parsed_value": parsed_value,
                "success": success
            }, success)

def capture_conversation_state_change(user_id: str, old_state: int, new_state: int, state_names: dict = None):
    """Captura mudança de estado da conversa"""
    session = capture_system.get_session(user_id)
    if session:
        old_name = state_names.get(old_state, f"STATE_{old_state}") if state_names else f"STATE_{old_state}"
        new_name = state_names.get(new_state, f"STATE_{new_state}") if state_names else f"STATE_{new_state}"
        
        session.add_step("CONVERSATION_STATE_CHANGE", {
            "old_state": old_state,
            "new_state": new_state,
            "old_state_name": old_name,
            "new_state_name": new_name
        })
        
        session.update_state(new_name)

def capture_api_call(user_id: str, api_name: str, request_data: dict, response_data: dict, success: bool):
    """Captura chamada de API"""
    session = capture_system.get_session(user_id)
    if session:
        session.add_step(f"API_CALL_{api_name.upper()}", {
            "request_data": request_data,
            "response_data": response_data,
            "success": success
        }, success)

# ============================================================================
# FUNÇÕES DE MONITORAMENTO
# ============================================================================

def monitor_active_sessions():
    """Monitora sessões ativas e detecta possíveis problemas"""
    active = capture_system.get_all_active_sessions()
    stuck = capture_system.find_stuck_sessions(30)  # 30 minutos
    
    logger.info(f"📊 [MONITOR] Sessões ativas: {len(active)}")
    
    if stuck:
        logger.warning(f"⚠️ [MONITOR] Sessões possivelmente travadas: {len(stuck)}")
        for user_id, info in stuck.items():
            logger.warning(f"🔴 [MONITOR] Usuário {user_id} travado em {info['current_state']} há {info['duration_minutes']:.1f} minutos")
    
    return {"active": active, "stuck": stuck}

def get_user_journey(user_id: str) -> dict:
    """Retorna a jornada completa do usuário"""
    session = capture_system.get_session(user_id)
    if session:
        return {
            "summary": capture_system.get_session_summary(user_id),
            "full_journey": session.to_dict()
        }
    return None
