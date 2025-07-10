#!/usr/bin/env python3
"""
Sistema de Captura de Eventos do Bot Ghost
"""
from .capture_system import capture_system, CaptureSystem, UserSession
from .telegram_integration import (
    capture_telegram_handler,
    capture_menu_compra_handler, 
    capture_start_command,
    capture_button_click,
    capture_text_input,
    capture_conversation_state_change,
    capture_api_call,
    monitor_active_sessions,
    get_user_journey
)
from .bot_instrumentation import (
    bot_instrumentation,
    initialize_capture_system,
    BotInstrumentation
)

__all__ = [
    'capture_system',
    'CaptureSystem',
    'UserSession',
    'capture_telegram_handler',
    'capture_menu_compra_handler',
    'capture_start_command', 
    'capture_button_click',
    'capture_text_input',
    'capture_conversation_state_change',
    'capture_api_call',
    'monitor_active_sessions',
    'get_user_journey',
    'bot_instrumentation',
    'initialize_capture_system',
    'BotInstrumentation'
]
