#!/usr/bin/env python3
"""
Instrumentação do Bot Principal com Sistema de Captura
"""
import sys
from pathlib import Path
import logging

# Adicionar o diretório de captura ao path
captura_dir = Path(__file__).parent
sys.path.insert(0, str(captura_dir))

try:
    from capture_system import capture_system
    from telegram_integration import (
        capture_telegram_handler, 
        capture_menu_compra_handler,
        capture_start_command,
        capture_button_click,
        capture_text_input,
        capture_conversation_state_change,
        capture_api_call,
        monitor_active_sessions
    )
except ImportError as e:
    logging.error(f"Erro ao importar módulos de captura: {e}")
    # Criar mocks para evitar erro
    capture_system = None
    def capture_telegram_handler(func): return func
    def capture_menu_compra_handler(func): return func
    def capture_start_command(func): return func
    def capture_button_click(func): return func
    def capture_text_input(func): return func
    def capture_conversation_state_change(func): return func
    def capture_api_call(func): return func
    def monitor_active_sessions(): pass

logger = logging.getLogger('bot_instrumentation')

class BotInstrumentation:
    """Classe para instrumentar o bot principal"""
    
    def __init__(self):
        self.capture_system = capture_system
        self.conversation_states = {
            0: "SOLICITAR_CPF",
            1: "ESCOLHER_MOEDA", 
            2: "ESCOLHER_REDE",
            3: "QUANTIDADE",
            4: "RESUMO_COMPRA",
            5: "CONFIRMAR_COMPRA",
            6: "SOLICITAR_ENDERECO",
            7: "ESCOLHER_PAGAMENTO",
            8: "AGUARDAR_TED_COMPROVANTE"
        }
        
    def instrument_bot_handlers(self, application):
        """Instrumenta os handlers do bot"""
        logger.info("🔧 Instrumentando handlers do bot...")
        
        # Instrumentar handlers principais
        original_handlers = list(application.handlers.values())
        
        for group_handlers in original_handlers:
            for handler in group_handlers:
                if hasattr(handler, 'callback'):
                    # Instrumentar callback do handler
                    original_callback = handler.callback
                    handler.callback = self._instrument_handler(original_callback)
        
        logger.info(f"✅ {len(original_handlers)} grupos de handlers instrumentados")
        
    def _instrument_handler(self, original_handler):
        """Instrumenta um handler individual"""
        @capture_telegram_handler()
        async def instrumented_handler(update, context):
            return await original_handler(update, context)
        
        return instrumented_handler
    
    def patch_menu_compra(self):
        """Aplica patches específicos ao menu de compra, incluindo fluxo Lightning"""
        try:
            import menus.menu_compra as menu_compra
            
            # Patch das funções principais
            original_iniciar_compra = menu_compra.iniciar_compra
            original_escolher_moeda = menu_compra.escolher_moeda
            original_escolher_rede = menu_compra.escolher_rede
            original_processar_quantidade = menu_compra.processar_quantidade
            original_resumo_compra = menu_compra.resumo_compra
            original_processar_pix = menu_compra.processar_pix
            
            @capture_menu_compra_handler("iniciar_compra")
            async def patched_iniciar_compra(update, context):
                user_id = str(update.effective_user.id)
                capture_button_click(update, "🛒 Comprar")
                capture_system.capture_currency_selection(user_id, "MENU_OPENED")
                return await original_iniciar_compra(update, context)
            
            @capture_menu_compra_handler("escolher_moeda")
            async def patched_escolher_moeda(update, context):
                user_id = str(update.effective_user.id)
                moeda = update.message.text if update.message else ""
                capture_system.capture_currency_selection(user_id, moeda)
                return await original_escolher_moeda(update, context)
            
            @capture_menu_compra_handler("escolher_rede")
            async def patched_escolher_rede(update, context):
                user_id = str(update.effective_user.id)
                rede = update.message.text if update.message else ""
                capture_system.capture_network_selection(user_id, rede)
                return await original_escolher_rede(update, context)
            
            @capture_menu_compra_handler("processar_quantidade")
            async def patched_processar_quantidade(update, context):
                user_id = str(update.effective_user.id)
                amount_text = update.message.text if update.message else ""
                
                try:
                    # Tentar parsear o valor
                    import re
                    valor_str = amount_text.replace('R$', '').replace(',', '.').strip()
                    valor = float(re.sub(r'[^0-9.]', '', valor_str))
                    capture_text_input(update, "amount", valor, True)
                except:
                    capture_text_input(update, "amount", None, False)
                    
                return await original_processar_quantidade(update, context)
            
            @capture_menu_compra_handler("resumo_compra")
            async def patched_resumo_compra(update, context):
                user_id = str(update.effective_user.id)
                session = capture_system.get_session(user_id)
                if session:
                    session.add_step("RESUMO_GERADO", {
                        "moeda": context.user_data.get('moeda'),
                        "rede": context.user_data.get('rede'),
                        "valor_brl": context.user_data.get('valor_brl')
                    })
                return await original_resumo_compra(update, context)
            
            @capture_menu_compra_handler("processar_pix")
            async def patched_processar_pix(update, context):
                user_id = str(update.effective_user.id)
                
                # Capturar dados antes do processamento
                session = capture_system.get_session(user_id)
                if session:
                    session.add_step("PIX_PROCESSING_STARTED", {
                        "moeda": context.user_data.get('moeda'),
                        "rede": context.user_data.get('rede'),
                        "valor_brl": context.user_data.get('valor_brl'),
                        "endereco_recebimento": context.user_data.get('endereco_recebimento')
                    })
                
                try:
                    result = await original_processar_pix(update, context)
                    
                    # Capturar sucesso na geração do PIX
                    if session:
                        session.add_step("PIX_PROCESSING_SUCCESS")
                    
                    return result
                except Exception as e:
                    # Capturar erro na geração do PIX
                    capture_system.capture_error(user_id, "PIX_PROCESSING_ERROR", str(e), e)
                    raise
            
            # Patch dos novos eventos do fluxo Lightning
            original_solicitar_lightning_address = getattr(menu_compra, 'solicitar_lightning_address', None)
            original_validar_lightning_address = getattr(menu_compra, 'validar_lightning_address', None)
            original_verificar_voltz_saldo = getattr(menu_compra, 'verificar_voltz_saldo', None)
            original_executar_pagamento_lightning = getattr(menu_compra, 'executar_pagamento_lightning', None)

            if original_solicitar_lightning_address:
                @capture_menu_compra_handler("solicitar_lightning_address")
                async def patched_solicitar_lightning_address(update, context):
                    user_id = str(update.effective_user.id)
                    capture_system.capture_lightning_address_request(user_id)
                    return await original_solicitar_lightning_address(update, context)
                menu_compra.solicitar_lightning_address = patched_solicitar_lightning_address

            if original_validar_lightning_address:
                @capture_menu_compra_handler("validar_lightning_address")
                async def patched_validar_lightning_address(update, context):
                    user_id = str(update.effective_user.id)
                    address = update.message.text if update.message else ""
                    # Supondo que a função retorna (valid, error)
                    valid, error = await original_validar_lightning_address(update, context)
                    capture_system.capture_lightning_address_validation(user_id, address, valid, error)
                    return valid, error
                menu_compra.validar_lightning_address = patched_validar_lightning_address

            if original_verificar_voltz_saldo:
                @capture_menu_compra_handler("verificar_voltz_saldo")
                async def patched_verificar_voltz_saldo(update, context):
                    user_id = str(update.effective_user.id)
                    saldo, suficiente, error = await original_verificar_voltz_saldo(update, context)
                    capture_system.capture_voltz_balance_check(user_id, saldo, suficiente, error)
                    return saldo, suficiente, error
                menu_compra.verificar_voltz_saldo = patched_verificar_voltz_saldo

            if original_executar_pagamento_lightning:
                @capture_menu_compra_handler("executar_pagamento_lightning")
                async def patched_executar_pagamento_lightning(update, context):
                    user_id = str(update.effective_user.id)
                    address = context.user_data.get('lightning_address')
                    valor_sats = context.user_data.get('valor_btc')
                    try:
                        txid, success, error = await original_executar_pagamento_lightning(update, context)
                        capture_system.capture_lightning_payment(user_id, address, valor_sats, txid, success, error)
                        return txid, success, error
                    except Exception as e:
                        capture_system.capture_lightning_payment(user_id, address, valor_sats, None, False, str(e))
                        raise
                menu_compra.executar_pagamento_lightning = patched_executar_pagamento_lightning
            
            # Aplicar patches
            menu_compra.iniciar_compra = patched_iniciar_compra
            menu_compra.escolher_moeda = patched_escolher_moeda
            menu_compra.escolher_rede = patched_escolher_rede
            menu_compra.processar_quantidade = patched_processar_quantidade
            menu_compra.resumo_compra = patched_resumo_compra
            menu_compra.processar_pix = patched_processar_pix
            
            logger.info("✅ Menu de compra instrumentado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao instrumentar menu de compra: {e}")
    
    def patch_sistema_gatilhos(self):
        """Aplica patches ao sistema de gatilhos"""
        try:
            from trigger.sistema_gatilhos import trigger_system, EventTriggerSystem
            
            # Patch do método trigger_event
            original_trigger_event = trigger_system.trigger_event
            
            def patched_trigger_event(event, chat_id, data=None):
                # Capturar evento
                capture_system.capture_trigger_event(chat_id, event.value, data)
                
                try:
                    result = original_trigger_event(event, chat_id, data)
                    
                    # Capturar sucesso
                    session = capture_system.get_session(chat_id)
                    if session:
                        session.add_step(f"TRIGGER_{event.value.upper()}_SUCCESS", {"result": result})
                    
                    return result
                except Exception as e:
                    capture_system.capture_error(chat_id, f"TRIGGER_{event.value.upper()}_ERROR", str(e), e)
                    raise
            
            trigger_system.trigger_event = patched_trigger_event
            
            logger.info("✅ Sistema de gatilhos instrumentado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao instrumentar sistema de gatilhos: {e}")
    
    def patch_api_calls(self):
        """Instrumenta chamadas de API"""
        try:
            # Patch da API Depix
            from api.depix import pix_api
            
            if hasattr(pix_api, 'criar_pagamento'):
                original_criar_pagamento = pix_api.criar_pagamento
                
                def patched_criar_pagamento(*args, **kwargs):
                    # Extrair chat_id dos argumentos
                    chatid = kwargs.get('chatid') or (args[2] if len(args) > 2 else None)
                    
                    request_data = {
                        "args": args,
                        "kwargs": kwargs
                    }
                    
                    try:
                        result = original_criar_pagamento(*args, **kwargs)
                        
                        # Capturar sucesso
                        if chatid:
                            capture_api_call(chatid, "depix_criar_pagamento", request_data, result, True)
                            
                            # Extrair depix_id se disponível
                            if isinstance(result, dict):
                                depix_id = None
                                if result.get('success') and 'data' in result:
                                    depix_id = result['data'].get('transaction_id')
                                elif 'transaction_id' in result:
                                    depix_id = result['transaction_id']
                                
                                if depix_id:
                                    capture_system.capture_pix_generation(chatid, depix_id, result.get('qr_image_url'), True)
                        
                        return result
                        
                    except Exception as e:
                        if chatid:
                            capture_api_call(chatid, "depix_criar_pagamento", request_data, str(e), False)
                        raise
                
                pix_api.criar_pagamento = patched_criar_pagamento
            
            logger.info("✅ APIs instrumentadas com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao instrumentar APIs: {e}")
    
    def setup_monitoring(self):
        """Configura monitoramento contínuo"""
        import asyncio
        
        async def monitoring_loop():
            while True:
                try:
                    await asyncio.sleep(300)  # 5 minutos
                    monitor_active_sessions()
                except Exception as e:
                    logger.error(f"❌ Erro no monitoramento: {e}")
        
        # Iniciar loop de monitoramento
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(monitoring_loop())
            else:
                loop.run_until_complete(monitoring_loop())
        except RuntimeError:
            # Loop será iniciado quando o bot iniciar
            pass
    
    def instrument_all(self, application):
        """Instrumenta todos os componentes"""
        logger.info("🚀 Iniciando instrumentação completa do bot...")
        
        try:
            self.patch_menu_compra()
            self.patch_sistema_gatilhos()
            self.patch_api_calls()
            self.setup_monitoring()
            
            logger.info("✅ Instrumentação completa finalizada!")
            
        except Exception as e:
            logger.error(f"❌ Erro na instrumentação: {e}")

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

bot_instrumentation = BotInstrumentation()

# ============================================================================
# FUNÇÃO DE INICIALIZAÇÃO
# ============================================================================

def initialize_capture_system(application):
    """Inicializa o sistema de captura no bot"""
    logger.info("🎯 Inicializando sistema de captura...")
    
    try:
        bot_instrumentation.instrument_all(application)
        
        logger.info("✅ Sistema de captura inicializado com sucesso!")
        logger.info("📊 Logs detalhados serão salvos em: /home/mau/bot/ghost/captura/")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar sistema de captura: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testando instrumentação...")
    
    # Teste básico
    test_session = capture_system.start_session("test_user", "TestUser")
    print(f"📋 Sessão de teste criada: {test_session.user_id}")
    
    # Simular alguns passos
    test_session.add_step("TEST_STEP_1", {"data": "test"})
    test_session.add_step("TEST_STEP_2", {"data": "test2"})
    
    summary = capture_system.get_session_summary("test_user")
    print(f"📊 Resumo: {summary}")
    
    capture_system.end_session("test_user")
    print("✅ Teste concluído!")
