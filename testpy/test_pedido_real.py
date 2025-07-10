#!/usr/bin/env python3
"""
Script para simular um pedido real no sistema Ghost Bot
Testa todo o fluxo: desde o registro até o monitoramento
"""

import sys
import os
import asyncio
import aiohttp
import json
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_pix_monitor import register_pix_payment

async def simular_pedido_completo():
    """Simula um pedido real completo no sistema"""
    
    print("🧪 SIMULAÇÃO DE PEDIDO REAL - GHOST BOT")
    print("=" * 50)
    
    # Dados do pedido simulado
    chat_id = "999888777"  # ID fictício para teste
    valor_brl = 150.00
    moeda = "BTC"
    rede = "Lightning"
    endereco = "voltzapi@tria.com"
    
    print(f"📊 Dados do pedido:")
    print(f"   • Chat ID: {chat_id}")
    print(f"   • Valor: R$ {valor_brl:,.2f}")
    print(f"   • Moeda: {moeda}")
    print(f"   • Rede: {rede}")
    print(f"   • Endereço: {endereco}")
    print()
    
    # 1. Simular registro no backend (API Depix)
    print("1️⃣ Simulando registro no backend...")
    try:
        valor_centavos = int(valor_brl * 100)
        taxa = 0.05  # 5%
        valor_recebido = (valor_brl * (1 - taxa)) / 350000  # Cotação fictícia BTC
        
        payload = {
            "chatid": chat_id,
            "moeda": moeda,
            "rede": rede,
            "amount_in_cents": valor_centavos,
            "taxa": round(taxa * 100, 2),
            "address": endereco,
            "metodo_pagamento": "PIX",
            "forma_pagamento": "PIX",
            "send": float(valor_recebido),
            "depix_id": f"TESTE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "pending",
            "user_id": int(chat_id),
        }
        
        if rede.lower() == "lightning":
            payload["comprovante"] = "Lightning Invoice"
        
        print(f"   📤 Enviando para: https://useghost.squareweb.app/rest/deposit.php")
        print(f"   📦 Payload: {json.dumps(payload, indent=2)}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://useghost.squareweb.app/rest/deposit.php",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                backend_resp = await resp.json()
                print(f"   📥 Resposta do backend: {json.dumps(backend_resp, indent=2)}")
                
                if backend_resp.get("success", False):
                    print("   ✅ Pedido registrado no backend com sucesso!")
                    deposit_id = backend_resp.get("id")
                    if deposit_id:
                        print(f"   🆔 ID do depósito criado: {deposit_id}")
                else:
                    print("   ❌ Falha ao registrar no backend")
                    print(f"   📝 Detalhes: {backend_resp}")
                    
    except Exception as e:
        print(f"   ❌ Erro ao registrar no backend: {e}")
    
    print()
    
    # 2. Registrar no Smart PIX Monitor
    print("2️⃣ Registrando no Smart PIX Monitor...")
    try:
        txid = payload["depix_id"]
        register_pix_payment(txid, chat_id, valor_brl)
        print(f"   ✅ PIX {txid} registrado no Smart Monitor!")
        print(f"   🔄 Monitor irá verificar o status a cada 30 segundos")
    except Exception as e:
        print(f"   ❌ Erro ao registrar no Smart Monitor: {e}")
    
    print()
    
    # 3. Verificar se o pedido foi salvo no backend
    print("3️⃣ Verificando se o pedido foi salvo...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://useghost.squareweb.app/rest/deposit.php?chatid={chat_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                deposits_resp = await resp.json()
                deposits = deposits_resp.get("deposits", [])
                
                print(f"   📊 Total de depósitos encontrados: {len(deposits)}")
                
                if deposits:
                    for i, deposit in enumerate(deposits[-3:], 1):  # Últimos 3
                        print(f"   💰 Depósito #{i}:")
                        print(f"      • ID: {deposit.get('id')}")
                        print(f"      • Valor: R$ {float(deposit.get('amount_in_cents', 0))/100:.2f}")
                        print(f"      • Status: {deposit.get('status')}")
                        print(f"      • Moeda: {deposit.get('moeda')}")
                        print(f"      • Criado: {deposit.get('created_at')}")
                        print()
                    
                    # Verifica se o pedido atual está na lista
                    pedido_atual = next((d for d in deposits if d.get('depix_id') == txid), None)
                    if pedido_atual:
                        print("   ✅ Pedido atual encontrado no backend!")
                        print(f"   🆔 ID: {pedido_atual.get('id')}")
                        print(f"   📊 Status: {pedido_atual.get('status')}")
                    else:
                        print("   ⚠️ Pedido atual não encontrado na consulta")
                else:
                    print("   📝 Nenhum depósito encontrado para este chat_id")
                    
    except Exception as e:
        print(f"   ❌ Erro ao consultar backend: {e}")
    
    print()
    print("🏁 SIMULAÇÃO CONCLUÍDA")
    print("=" * 50)
    print()
    print("📋 PRÓXIMOS PASSOS PARA TESTE REAL:")
    print("1. Acesse o bot no Telegram")
    print("2. Digite /start")
    print("3. Escolha 'Comprar'")
    print("4. Siga o fluxo: Bitcoin > Lightning > R$ 50,00")
    print("5. Pague o PIX gerado")
    print("6. Monitore os logs e o dashboard")
    print()
    print("📊 MONITORAMENTO:")
    print(f"• Bot logs: tail -f /home/mau/bot/ghost/bot.log")
    print(f"• Monitor logs: tail -f /home/mau/bot/ghost/monitor.log")
    print(f"• Dashboard: python monitor_dashboard.py")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(simular_pedido_completo())
    except KeyboardInterrupt:
        print("\n⏹️ Simulação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro na simulação: {e}")
        import traceback
        traceback.print_exc()
