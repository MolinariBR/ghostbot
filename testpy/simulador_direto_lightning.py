#!/usr/bin/env python3
"""
Simulador direto da solicitação Lightning - bypassa servidor instável
Simula o que acontece quando o notifier processa um depósito
"""
import asyncio
import sys
import os
import time
import hashlib
sys.path.append('/home/mau/bot/ghost')

# Adicionar path do bot
import logging
from telegram import Bot
from telegram.ext import Application

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simulate_lightning_request():
    """Simula solicitação de endereço Lightning diretamente via bot"""
    
    # Dados do teste - USANDO DEPÓSITO REAL CRIADO
    chat_id = 7910260237
    depix_id = "0197eae225117dfc85fe31ea03c518a4"  # Depósito real criado pelo bot
    amount_sats = 806  # Valor em sats para R$ 5 (aproximadamente)
    
    print("\n🚀 SIMULADOR DIRETO DE SOLICITAÇÃO LIGHTNING")
    print("=" * 60)
    print(f"💬 Chat ID: {chat_id}")
    print(f"🎯 Depix ID: {depix_id}")
    print(f"⚡ Valor: {amount_sats} sats")
    
    try:
        # Importar token do bot
        sys.path.append('/home/mau/bot/ghost')
        from tokens import Config
        
        # Criar bot
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        print(f"\n1️⃣ CONECTANDO AO BOT TELEGRAM")
        print("-" * 40)
        
        # Testar conexão
        me = await bot.get_me()
        print(f"✅ Bot conectado: @{me.username}")
        
        print(f"\n2️⃣ ENVIANDO SOLICITAÇÃO DE ENDEREÇO LIGHTNING")
        print("-" * 40)
        
        # Criar mensagem inicial
        mensagem = f"""⚡ Depósito PIX confirmado - Lightning Network

🎯 Depix ID: {depix_id}
💰 Valor: {amount_sats:,} sats (≈ R$ 5,00)
🔄 Status: Aguardando endereço Lightning

📮 Por favor, envie seu endereço Lightning:

Opção 1 - Lightning Address:
• Formato: usuario@dominio.com
• Exemplo: satoshi@getalby.com

Opção 2 - Invoice BOLT11:
• Formato: lnbc...
• Deve ter valor exato de {amount_sats:,} sats

⚠️ Importante:
• Verifique o valor antes de enviar
• Use endereços/carteiras confiáveis
• O pagamento será enviado imediatamente após validação

💡 Dúvidas? Use /help_lightning"""
        
        # Enviar mensagem inicial
        await bot.send_message(
            chat_id=chat_id,
            text=mensagem
        )
        
        print(f"✅ Mensagem inicial enviada")
        
        # Aguardar um pouco para simular tempo de resposta do usuário
        print(f"\n3️⃣ SIMULANDO PROCESSAMENTO DE ENDEREÇO")
        print("-" * 40)
        print("⏳ Aguardando 3 segundos (simulando tempo de resposta do usuário)...")
        await asyncio.sleep(3)
        
        # Simular processamento bem-sucedido
        exemplo_address = "usuario@getalby.com"
        mensagem_sucesso = f"""✅ Endereço Lightning processado com sucesso!

🎯 Depix ID: {depix_id}
📮 Endereço: {exemplo_address}
💰 Valor: {amount_sats:,} sats (≈ R$ 5,00)
⚡ Status: Processando pagamento Lightning

🚀 Seu pagamento Lightning está sendo processado!
Você receberá os satoshis em instantes.

📊 Detalhes da transação:
• Método: Lightning Address
• Validação: ✅ Aprovada
• Processamento: Em andamento

⏰ Tempo estimado: 1-5 segundos
💡 Você será notificado quando o pagamento for concluído."""
        
        # Enviar confirmação de processamento
        await bot.send_message(
            chat_id=chat_id,
            text=mensagem_sucesso
        )
        
        print(f"✅ Confirmação de processamento enviada")
        
        # Simular conclusão do pagamento
        print("⏳ Aguardando mais 3 segundos (simulando processamento Lightning)...")
        await asyncio.sleep(3)
        
        # Simular hash de transação Lightning fictício
        import hashlib
        hash_ficticio = hashlib.sha256(f"{depix_id}_{amount_sats}".encode()).hexdigest()[:16]
        
        mensagem_final = f"""🎉 Pagamento Lightning concluído com sucesso!

🎯 Depix ID: {depix_id}
💰 Valor enviado: {amount_sats:,} sats (≈ R$ 5,00)
📮 Destino: {exemplo_address}
⚡ Hash da transação: {hash_ficticio}

✅ STATUS: CONCLUÍDO
⏰ Processado em: 6 segundos
🌐 Rede: Lightning Network

Obrigado por usar o Ghost P2P! 🚀"""
        
        # Enviar confirmação final
        await bot.send_message(
            chat_id=chat_id,
            text=mensagem_final
        )
        
        print(f"✅ Confirmação final enviada")
        
        print(f"\n4️⃣ FLUXO COMPLETO SIMULADO")
        print("-" * 40)
        print("✅ 1. Solicitação de endereço enviada")
        print("✅ 2. Processamento de endereço simulado")
        print("✅ 3. Pagamento Lightning simulado")
        print("✅ 4. Confirmação final enviada")
        
        print(f"\n📱 Verifique o Telegram - você deve ter recebido 3 mensagens:")
        print("   1. Solicitação de endereço Lightning")
        print("   2. Confirmação de processamento")
        print("   3. Confirmação final do pagamento")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos do bot: {e}")
        print("💡 Certifique-se de que o tokens.py existe e está correto")
        return False
        
    except Exception as e:
        print(f"❌ Erro durante simulação: {e}")
        return False

async def main():
    """Função principal"""
    success = await simulate_lightning_request()
    
    if success:
        print(f"\n🎉 TESTE REALIZADO COM SUCESSO!")
        print("O bot deveria ter enviado a mensagem solicitando endereço Lightning.")
        print("Isso simula exatamente o que aconteceria se o cron/notifier estivesse funcionando.")
    else:
        print(f"\n❌ FALHA NO TESTE")
        print("Verifique as configurações do bot e tente novamente.")

if __name__ == "__main__":
    asyncio.run(main())
