#!/usr/bin/env python3
"""
Integração Mínima: Hook para substituir apenas o CRON
Mantém 100% da estrutura atual, apenas melhora o monitoramento
"""
import sys
import os
sys.path.append('/home/mau/bot/ghost')

from smart_cron_replacement import cron_replacement, add_order_to_monitor
import logging

logger = logging.getLogger('minimal_integration')

class MinimalCronHook:
    """Hook mínimo para interceptar apenas a criação de PIX"""
    
    def __init__(self):
        self.enabled = False
    
    def enable(self):
        """Ativa apenas o substituto do cron (mantém todo resto igual)"""
        if self.enabled:
            return
        
        # Ativar monitoramento inteligente
        cron_replacement.enable()
        self.enabled = True
        
        logger.info("🔄 Hook mínimo ativado - apenas CRON substituído")
        logger.info("✅ Estrutura atual do bot mantida 100%")
    
    def disable(self):
        """Desativa hook (volta tudo como era)"""
        if not self.enabled:
            return
        
        cron_replacement.disable()
        self.enabled = False
        
        logger.info("🔄 Hook desativado - voltando para cron original")
    
    def on_pix_created(self, depix_id: str, chat_id: str, amount_brl: float):
        """
        Chamar esta função APENAS quando um PIX for criado
        Substitui a necessidade do cron para monitorar este pedido
        """
        if not self.enabled:
            return  # Não fazer nada se não estiver ativado
        
        logger.info(f"📱 PIX criado: {depix_id} (R$ {amount_brl:.2f}) - iniciando monitoramento inteligente")
        
        # Adicionar ao monitoramento inteligente
        add_order_to_monitor(depix_id, str(chat_id), amount_brl)
    
    def get_monitoring_stats(self):
        """Retorna stats do monitoramento (opcional)"""
        if not self.enabled:
            return {"status": "disabled"}
        
        return cron_replacement.get_stats()

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================
hook = MinimalCronHook()

def enable_smart_cron():
    """Ativa apenas substituto do cron (mantém todo resto)"""
    hook.enable()
    return hook

def disable_smart_cron():
    """Desativa substituto do cron"""
    hook.disable()

def notify_pix_created(depix_id: str, chat_id: str, amount_brl: float):
    """
    ÚNICA FUNÇÃO que precisa ser chamada no código existente
    Chamar sempre que um PIX for criado
    """
    hook.on_pix_created(depix_id, chat_id, amount_brl)

# ============================================================================
# INSTRUÇÕES DE INTEGRAÇÃO
# ============================================================================

INTEGRATION_INSTRUCTIONS = """
🎯 INTEGRAÇÃO MÍNIMA - SUBSTITUIÇÃO APENAS DO CRON

Para integrar com o código atual, siga apenas estes passos:

1. ATIVAR o sistema (uma vez):
   ```python
   from minimal_cron_hook import enable_smart_cron
   enable_smart_cron()
   ```

2. CHAMAR quando PIX for criado (onde quer que isso aconteça):
   ```python
   from minimal_cron_hook import notify_pix_created
   
   # Após criar PIX no sistema atual:
   notify_pix_created(depix_id, chat_id, amount_in_brl)
   ```

3. PRONTO! O resto funciona exatamente igual:
   - Bot continua igual
   - APIs continuam iguais  
   - Fluxo continua igual
   - Apenas o CRON é substituído por monitoramento inteligente

VANTAGENS:
✅ 30s de resposta vs 60s+ do cron
✅ Sem dependência do cron.job.org
✅ Mais confiável e rápido
✅ Zero mudanças no código existente
✅ Pode ser desativado a qualquer momento

LOCALIZAR NO CÓDIGO:
- Procure onde o depix_id é gerado/criado
- Adicione a chamada notify_pix_created() logo após
- Pronto!

EXEMPLO DE ONDE CHAMAR:
```python
# Depois de criar PIX (onde quer que seja):
depix_id = create_pix_payment(chat_id, amount)  # código atual
notify_pix_created(depix_id, chat_id, amount)   # NOVA LINHA
```
"""

if __name__ == "__main__":
    print(INTEGRATION_INSTRUCTIONS)
    
    # Teste simples
    print("\n" + "="*50)
    print("🧪 TESTE DO SISTEMA:")
    
    # Ativar
    smart_cron = enable_smart_cron()
    print("✅ Sistema ativado")
    
    # Simular criação de PIX
    notify_pix_created("test_123", "7910260237", 25.0)
    print("✅ PIX simulado adicionado ao monitoramento")
    
    # Ver stats
    print("📊 Stats:", smart_cron.get_monitoring_stats())
    
    import time
    print("⏳ Aguardando 5 segundos...")
    time.sleep(5)
    
    print("📊 Stats após 5s:", smart_cron.get_monitoring_stats())
    
    # Desativar
    disable_smart_cron()
    print("✅ Sistema desativado")
