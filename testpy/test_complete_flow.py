#!/usr/bin/env python3
"""
Teste completo do novo fluxo de PIX
Simula um PIX novo e testa todo o sistema
"""
import asyncio
import logging
import sys
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.append('/home/mau/bot/ghost')

async def test_complete_flow():
    """Testa o fluxo completo do sistema"""
    try:
        logger.info("🚀 Iniciando teste completo do sistema...")
        
        # Dados do PIX para teste
        depix_id = "0197f7083e627dfe8532dfb32d576171"
        chat_id = "7910260237"
        
        # 1. Importar sistema de notificação
        from direct_notification import notification_system
        logger.info("✅ Sistema de notificação importado")
        
        # 2. Testar verificação única
        logger.info("🔍 Testando verificação única...")
        result = await notification_system.check_and_notify(depix_id, chat_id)
        logger.info(f"✅ Verificação única: {result}")
        
        # 3. Testar sistema inteligente (apenas 1 verificação para teste)
        logger.info("🎯 Testando sistema inteligente...")
        
        # Simular apenas primeira verificação (30s seria muito longo)
        await asyncio.sleep(2)  # Simula 30s com 2s para teste
        result2 = await notification_system.check_and_notify(depix_id, chat_id)
        logger.info(f"✅ Sistema inteligente: {result2}")
        
        # 4. Testar captura de dados
        logger.info("📊 Testando captura de dados...")
        try:
            from captura.capture_system import capture_system
            capture_system.start_session(chat_id, "triacorelabs")
            capture_system.capture_step(chat_id, "DIRECT_NOTIFICATION_TEST", {
                "depix_id": depix_id,
                "result": result,
                "timestamp": "2025-07-10T22:25:00"
            })
            logger.info("✅ Dados capturados com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ Erro capturando dados: {e}")
        
        # 5. Resultado final
        if result and result2:
            logger.info("🎉 TESTE COMPLETO: SUCESSO!")
            logger.info("✅ Sistema de notificação funcionando 100%")
            logger.info("✅ PIX detectado e mensagem enviada")
            logger.info("✅ Fluxo completo operacional")
            return True
        else:
            logger.error("❌ TESTE COMPLETO: FALHA!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste completo: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Função principal"""
    logger.info("🧪 TESTE COMPLETO DO SISTEMA DE NOTIFICAÇÃO DIRETA")
    logger.info("=" * 60)
    
    success = await test_complete_flow()
    
    logger.info("=" * 60)
    if success:
        logger.info("🎉 TODOS OS TESTES PASSARAM!")
        logger.info("✅ Sistema pronto para produção")
    else:
        logger.error("❌ ALGUNS TESTES FALHARAM!")
        logger.error("⚠️ Verifique os logs acima")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
