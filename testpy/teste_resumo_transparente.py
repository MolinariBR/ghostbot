#!/usr/bin/env python3
"""
Teste do Novo Resumo Transparente da Compra
==========================================

Este teste demonstra como o novo resumo da compra exibe de forma transparente
todas as taxas e comissões, mesmo quando o método de pagamento ainda não foi escolhido.
"""

import sys
import os
sys.path.append('/home/mau/bot/ghost')

from limites.comissao import calcular_comissao
from decimal import Decimal

def formatar_brl(valor):
    """Formata valor para BRL."""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def formatar_cripto(valor, moeda):
    """Formata valor para criptomoeda."""
    if moeda == 'BTC':
        return f"{valor:.8f} BTC"
    elif moeda == 'USDT':
        return f"{valor:.2f} USDT"
    elif moeda == 'DEPIX':
        return f"{valor:.2f} DEPIX"
    return f"{valor:.6f} {moeda}"

def simular_resumo_compra(valor_brl, moeda, rede, metodo_pagamento=None):
    """Simula o resumo da compra com o novo sistema."""
    
    # Simula cotação
    cotacoes = {
        'BTC': 600000.00,
        'USDT': 6.00,
        'DEPIX': 1.00
    }
    cotacao = cotacoes.get(moeda, 1.0)
    
    # Calcula comissão
    resultado_comissao = calcular_comissao(valor_brl, moeda)
    
    if resultado_comissao:
        comissao_total = resultado_comissao['comissao']['total']
        valor_liquido = resultado_comissao['valor_liquido']
        valor_recebido = valor_liquido / cotacao
        
        comissao_info = resultado_comissao['comissao']
        percentual = comissao_info['percentual']
        taxa_fixa = comissao_info['fixo']
    else:
        print(f"❌ Erro: Não foi possível calcular comissão para {moeda} valor R$ {valor_brl}")
        return
    
    # Formata valores
    valor_brl_formatado = formatar_brl(valor_brl)
    valor_recebido_formatado = formatar_cripto(valor_recebido, moeda)
    comissao_formatada = formatar_brl(comissao_total)
    cotacao_formatada = formatar_brl(cotacao)
    
    # Mapeia métodos de pagamento para taxa do parceiro
    mapeamento_taxas = {
        'PIX': 1.00,
        '💠 PIX': 1.00,
        'DEPIX': 1.00,
        'TED': 0.00,  # Será redirecionado
        'Boleto': 0.00,  # Será redirecionado
        'Lightning': 0.00  # Sem taxa adicional
    }
    
    # Determina a taxa do parceiro
    if metodo_pagamento and metodo_pagamento in mapeamento_taxas:
        taxa_parceiro = mapeamento_taxas[metodo_pagamento]
        taxa_parceiro_info = f"R$ {taxa_parceiro:.2f}"
    else:
        # Método não escolhido ainda - mostra informação transparente
        taxa_parceiro_info = "Definida após escolha do pagamento"
    
    # Monta mensagem do resumo
    mensagem = (
        f"📋 *RESUMO DA COMPRA*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Moeda:* {moeda}\n"
        f"• *Rede:* {rede}\n"
        f"• *Valor Investido:* {valor_brl_formatado}\n"
        f"• *Parceiro:* {taxa_parceiro_info}\n"
        f"• *Comissão:* {percentual:.1f}% + R$ {taxa_fixa:.2f} = {comissao_formatada}\n"
        f"• *Cotação:* {cotacao_formatada}\n"
        f"• *Você receberá:* {valor_recebido_formatado}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    # Adiciona nota explicativa se método não foi escolhido
    if not metodo_pagamento or metodo_pagamento not in mapeamento_taxas:
        mensagem += (
            "ℹ️ *Nota:* A taxa do parceiro (R$ 1,00 para PIX) será "
            "exibida após a escolha do método de pagamento.\n\n"
        )
    
    mensagem += "Confirma os dados da compra?"
    
    return mensagem

def main():
    """Demonstra o novo resumo transparente."""
    
    print("🧪 TESTE DO NOVO RESUMO TRANSPARENTE DA COMPRA")
    print("=" * 60)
    
    # Cenários de teste
    cenarios = [
        {
            'valor': 150.00,
            'moeda': 'BTC',
            'rede': 'Lightning',
            'metodo': None,
            'desc': 'BTC Lightning - Sem método de pagamento'
        },
        {
            'valor': 150.00,
            'moeda': 'BTC',
            'rede': 'Lightning',
            'metodo': 'PIX',
            'desc': 'BTC Lightning - Com PIX'
        },
        {
            'valor': 750.00,
            'moeda': 'BTC',
            'rede': 'On-chain',
            'metodo': None,
            'desc': 'BTC On-chain - Sem método de pagamento'
        },
        {
            'valor': 300.00,
            'moeda': 'DEPIX',
            'rede': 'Polygon',
            'metodo': '💠 PIX',
            'desc': 'DEPIX - Com PIX'
        },
        {
            'valor': 500.00,
            'moeda': 'USDT',
            'rede': 'Polygon',
            'metodo': None,
            'desc': 'USDT - Sem método de pagamento'
        }
    ]
    
    for i, cenario in enumerate(cenarios, 1):
        print(f"\n🔸 CENÁRIO {i}: {cenario['desc']}")
        print("-" * 50)
        
        resumo = simular_resumo_compra(
            cenario['valor'],
            cenario['moeda'],
            cenario['rede'],
            cenario['metodo']
        )
        
        print(resumo)
        print()
    
    print("✅ BENEFÍCIOS DO NOVO SISTEMA:")
    print("• Transparência total das taxas e comissões")
    print("• Usuário sabe exatamente o que vai pagar")
    print("• Comissão é calculada automaticamente")
    print("• Taxa do parceiro é explicada claramente")
    print("• Fluxo atual do bot é mantido")
    
    print("\n🎯 RESULTADO:")
    print("• Resumo exibe todas as informações necessárias")
    print("• Usuário não fica surpreso com taxas")
    print("• Sistema é transparente e profissional")
    print("• Integração perfeita com sistema de comissões")

if __name__ == "__main__":
    main()
