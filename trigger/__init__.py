"""
Módulo de Triggers do Ghost Bot
Sistema de gatilhos event-driven para fluxo de compra automático
"""

try:
    from .sistema_gatilhos import trigger_system, TriggerEvent, OrderStatus
except ImportError:
    from .simple_system import simple_trigger_system as trigger_system
    from .config import TriggerEvent, OrderStatus

try:
    from .integrador_bot_gatilhos import BotTriggerIntegrator, TriggerUIImplementation
except ImportError:
    BotTriggerIntegrator = None
    TriggerUIImplementation = None

try:
    from .lightning_handler import LightningHandler
except ImportError:
    LightningHandler = None

try:
    from .smart_pix_monitor import SmartPixMonitor
except ImportError:
    SmartPixMonitor = None

__all__ = [
    'trigger_system',
    'TriggerEvent',
    'OrderStatus',
    'BotTriggerIntegrator',
    'TriggerUIImplementation',
    'LightningHandler',
    'SmartPixMonitor'
]