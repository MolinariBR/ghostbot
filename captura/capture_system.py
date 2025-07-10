#!/usr/bin/env python3
"""
Sistema de Captura de Eventos do Bot
Monitora e registra todos os passos do usuário desde o /start até o processo final
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import traceback

# Configurar logging específico para captura
capture_logger = logging.getLogger('capture_system')
capture_logger.setLevel(logging.DEBUG)

# Criar handler para arquivo de captura
capture_dir = Path(__file__).parent
capture_file = capture_dir / f"capture_{datetime.now().strftime('%Y%m%d')}.log"

# Handler para arquivo
file_handler = logging.FileHandler(capture_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Handler para console 
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatador detalhado
detailed_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)8s | [%(name)s] | %(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler.setFormatter(detailed_formatter)
console_handler.setFormatter(detailed_formatter)

capture_logger.addHandler(file_handler)
capture_logger.addHandler(console_handler)

class UserSession:
    """Classe para rastrear a sessão de um usuário"""
    
    def __init__(self, user_id: str, username: str = None):
        self.user_id = user_id
        self.username = username
        self.start_time = datetime.now()
        self.steps = []
        self.current_state = "STARTED"
        self.context_data = {}
        self.errors = []
        
    def add_step(self, step_name: str, data: Dict = None, success: bool = True):
        """Adiciona um passo à sessão"""
        step = {
            'timestamp': datetime.now().isoformat(),
            'step': step_name,
            'data': data or {},
            'success': success,
            'state_before': self.current_state
        }
        self.steps.append(step)
        capture_logger.info(f"[{self.user_id}] STEP: {step_name} | Success: {success} | Data: {data}")
        
    def update_state(self, new_state: str):
        """Atualiza o estado atual"""
        old_state = self.current_state
        self.current_state = new_state
        capture_logger.info(f"[{self.user_id}] STATE CHANGE: {old_state} → {new_state}")
        
    def add_error(self, error: str, exception: Exception = None):
        """Adiciona um erro à sessão"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error': error,
            'exception': str(exception) if exception else None,
            'traceback': traceback.format_exc() if exception else None
        }
        self.errors.append(error_data)
        capture_logger.error(f"[{self.user_id}] ERROR: {error} | Exception: {exception}")
        
    def to_dict(self) -> Dict:
        """Converte a sessão para dicionário"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'start_time': self.start_time.isoformat(),
            'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
            'current_state': self.current_state,
            'total_steps': len(self.steps),
            'total_errors': len(self.errors),
            'steps': self.steps,
            'context_data': self.context_data,
            'errors': self.errors
        }

class CaptureSystem:
    """Sistema principal de captura de eventos"""
    
    def __init__(self):
        self.active_sessions: Dict[str, UserSession] = {}
        self.session_history = []
        capture_logger.info("🎯 Sistema de Captura inicializado")
        
    def start_session(self, user_id: str, username: str = None) -> UserSession:
        """Inicia uma nova sessão para o usuário"""
        if user_id in self.active_sessions:
            # Finalizar sessão anterior se existir
            self.end_session(user_id)
            
        session = UserSession(user_id, username)
        self.active_sessions[user_id] = session
        
        capture_logger.info(f"🚀 NOVA SESSÃO INICIADA: {user_id} ({username})")
        session.add_step("SESSION_STARTED", {"username": username})
        
        return session
        
    def get_session(self, user_id: str) -> Optional[UserSession]:
        """Obtém a sessão ativa do usuário"""
        return self.active_sessions.get(user_id)
        
    def end_session(self, user_id: str):
        """Finaliza a sessão do usuário"""
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            session.add_step("SESSION_ENDED")
            
            # Salvar no histórico
            self.session_history.append(session.to_dict())
            
            # Salvar em arquivo JSON
            self.save_session_to_file(session)
            
            capture_logger.info(f"🏁 SESSÃO FINALIZADA: {user_id} | Duração: {(datetime.now() - session.start_time).total_seconds():.1f}s")
            
            del self.active_sessions[user_id]
            
    def save_session_to_file(self, session: UserSession):
        """Salva a sessão em arquivo JSON"""
        try:
            session_file = capture_dir / f"session_{session.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            capture_logger.debug(f"💾 Sessão salva: {session_file}")
        except Exception as e:
            capture_logger.error(f"❌ Erro ao salvar sessão: {e}")
    
    # ============================================================================
    # MÉTODOS DE CAPTURA ESPECÍFICOS
    # ============================================================================
    
    def capture_start_command(self, user_id: str, username: str = None, first_name: str = None):
        """Captura comando /start"""
        session = self.start_session(user_id, username)
        session.add_step("START_COMMAND", {
            "username": username,
            "first_name": first_name,
            "command": "/start"
        })
        session.update_state("MENU_PRINCIPAL")
        
    def capture_menu_click(self, user_id: str, menu_option: str):
        """Captura clique em opção do menu"""
        session = self.get_session(user_id)
        if session:
            session.add_step("MENU_CLICK", {
                "option": menu_option,
                "previous_state": session.current_state
            })
            
            if menu_option == "🛒 Comprar":
                session.update_state("COMPRA_INICIADA")
            elif menu_option == "💰 Vender":
                session.update_state("VENDA_INICIADA")
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} ao clicar em {menu_option}")
            
    def capture_currency_selection(self, user_id: str, currency: str):
        """Captura seleção de moeda"""
        session = self.get_session(user_id)
        if session:
            session.add_step("CURRENCY_SELECTED", {"currency": currency})
            session.context_data["currency"] = currency
            session.update_state("MOEDA_SELECIONADA")
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} ao selecionar moeda {currency}")
            
    def capture_network_selection(self, user_id: str, network: str):
        """Captura seleção de rede"""
        session = self.get_session(user_id)
        if session:
            session.add_step("NETWORK_SELECTED", {"network": network})
            session.context_data["network"] = network
            session.update_state("REDE_SELECIONADA")
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} ao selecionar rede {network}")
            
    def capture_amount_input(self, user_id: str, amount_text: str, parsed_amount: float = None, success: bool = True):
        """Captura entrada de valor"""
        session = self.get_session(user_id)
        if session:
            session.add_step("AMOUNT_INPUT", {
                "amount_text": amount_text,
                "parsed_amount": parsed_amount,
                "success": success
            }, success)
            
            if success and parsed_amount:
                session.context_data["amount"] = parsed_amount
                session.update_state("VALOR_DEFINIDO")
            else:
                session.add_error(f"Valor inválido: {amount_text}")
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} ao inserir valor {amount_text}")
            
    def capture_address_input(self, user_id: str, address: str, address_type: str = None):
        """Captura entrada de endereço"""
        session = self.get_session(user_id)
        if session:
            session.add_step("ADDRESS_INPUT", {
                "address": address,
                "address_type": address_type
            })
            session.context_data["address"] = address
            session.update_state("ENDERECO_FORNECIDO")
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} ao inserir endereço")
            
    def capture_payment_method(self, user_id: str, payment_method: str):
        """Captura seleção de método de pagamento"""
        session = self.get_session(user_id)
        if session:
            session.add_step("PAYMENT_METHOD_SELECTED", {"payment_method": payment_method})
            session.context_data["payment_method"] = payment_method
            session.update_state("METODO_PAGAMENTO_SELECIONADO")
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} ao selecionar pagamento")
            
    def capture_pix_generation(self, user_id: str, depix_id: str, qr_code_url: str = None, success: bool = True):
        """Captura geração de PIX"""
        session = self.get_session(user_id)
        if session:
            session.add_step("PIX_GENERATED", {
                "depix_id": depix_id,
                "qr_code_url": qr_code_url,
                "success": success
            }, success)
            
            if success:
                session.context_data["depix_id"] = depix_id
                session.update_state("PIX_GERADO")
            else:
                session.add_error("Falha ao gerar PIX")
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} ao gerar PIX")
            
    def capture_pix_payment(self, user_id: str, depix_id: str, blockchain_txid: str = None):
        """Captura confirmação de pagamento PIX"""
        session = self.get_session(user_id)
        if session:
            session.add_step("PIX_PAYMENT_CONFIRMED", {
                "depix_id": depix_id,
                "blockchain_txid": blockchain_txid
            })
            session.context_data["blockchain_txid"] = blockchain_txid
            session.update_state("PIX_CONFIRMADO")
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} ao confirmar PIX")
            
    def capture_crypto_send(self, user_id: str, txid: str = None, success: bool = True, error: str = None):
        """Captura envio de criptomoeda"""
        session = self.get_session(user_id)
        if session:
            session.add_step("CRYPTO_SENT", {
                "txid": txid,
                "success": success,
                "error": error
            }, success)
            
            if success:
                session.context_data["crypto_txid"] = txid
                session.update_state("CRIPTO_ENVIADA")
            else:
                session.add_error(f"Falha ao enviar cripto: {error}")
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} ao enviar cripto")
            
    def capture_conversation_state(self, user_id: str, conversation_state: str, handler_name: str = None):
        """Captura estado da conversa"""
        session = self.get_session(user_id)
        if session:
            session.add_step("CONVERSATION_STATE", {
                "conversation_state": conversation_state,
                "handler_name": handler_name
            })
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} no estado {conversation_state}")
            
    def capture_trigger_event(self, user_id: str, event_name: str, event_data: Dict = None, success: bool = True):
        """Captura evento do sistema de gatilhos"""
        session = self.get_session(user_id)
        if session:
            session.add_step("TRIGGER_EVENT", {
                "event_name": event_name,
                "event_data": event_data,
                "success": success
            }, success)
        else:
            capture_logger.warning(f"⚠️ Sessão não encontrada para {user_id} no evento {event_name}")
            
    def capture_error(self, user_id: str, error_type: str, error_message: str, exception: Exception = None):
        """Captura erro genérico"""
        session = self.get_session(user_id)
        if session:
            session.add_error(f"{error_type}: {error_message}", exception)
            session.add_step("ERROR_OCCURRED", {
                "error_type": error_type,
                "error_message": error_message,
                "exception": str(exception) if exception else None
            }, success=False)
        else:
            capture_logger.error(f"❌ Erro para usuário sem sessão {user_id}: {error_type} - {error_message}")
    
    # ============================================================================
    # MÉTODOS DE ANÁLISE
    # ============================================================================
    
    def get_session_summary(self, user_id: str) -> Dict:
        """Retorna resumo da sessão"""
        session = self.get_session(user_id)
        if session:
            return {
                'user_id': user_id,
                'current_state': session.current_state,
                'total_steps': len(session.steps),
                'total_errors': len(session.errors),
                'duration_seconds': (datetime.now() - session.start_time).total_seconds(),
                'last_step': session.steps[-1] if session.steps else None,
                'context_data': session.context_data
            }
        return None
        
    def get_all_active_sessions(self) -> Dict:
        """Retorna todas as sessões ativas"""
        return {user_id: self.get_session_summary(user_id) for user_id in self.active_sessions.keys()}
        
    def find_stuck_sessions(self, max_duration_minutes: int = 30) -> Dict:
        """Encontra sessões que podem estar travadas"""
        stuck_sessions = {}
        current_time = datetime.now()
        
        for user_id, session in self.active_sessions.items():
            duration = (current_time - session.start_time).total_seconds() / 60
            if duration > max_duration_minutes:
                stuck_sessions[user_id] = {
                    'duration_minutes': duration,
                    'current_state': session.current_state,
                    'last_step': session.steps[-1] if session.steps else None,
                    'total_errors': len(session.errors)
                }
                
        return stuck_sessions

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

capture_system = CaptureSystem()

# ============================================================================
# DECORATOR PARA CAPTURA AUTOMÁTICA
# ============================================================================

def capture_handler(step_name: str = None):
    """Decorator para capturar automaticamente handlers"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Tentar extrair user_id dos argumentos
            user_id = None
            if len(args) >= 1 and hasattr(args[0], 'effective_user'):
                user_id = str(args[0].effective_user.id)
            elif len(args) >= 2 and hasattr(args[1], 'effective_user'):
                user_id = str(args[1].effective_user.id)
                
            if user_id:
                actual_step_name = step_name or func.__name__
                capture_system.capture_conversation_state(user_id, actual_step_name, func.__name__)
                
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if user_id:
                    capture_system.capture_error(user_id, "HANDLER_ERROR", str(e), e)
                raise
                
        return wrapper
    return decorator

if __name__ == "__main__":
    # Teste do sistema
    print("🧪 Testando sistema de captura...")
    
    # Simular sessão
    capture_system.capture_start_command("123456789", "test_user", "Test User")
    capture_system.capture_menu_click("123456789", "🛒 Comprar")
    capture_system.capture_currency_selection("123456789", "₿ Bitcoin (BTC)")
    capture_system.capture_network_selection("123456789", "⚡ Lightning")
    capture_system.capture_amount_input("123456789", "50.00", 50.0, True)
    
    # Mostrar resumo
    summary = capture_system.get_session_summary("123456789")
    print(f"📊 Resumo da sessão: {json.dumps(summary, indent=2, ensure_ascii=False)}")
    
    # Finalizar sessão
    capture_system.end_session("123456789")
    
    print("✅ Teste concluído!")
