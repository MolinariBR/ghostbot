import sys
sys.path.insert(0, '.')
from comissao.validador import gerar_resumo_compra
from comissao.limites import get_limite, registrar_compra, precisa_cpf, precisa_atendente
from comissao.comissao import calcular_comissao
from comissao.cotacao import get_cotacao

# Teste completo do fluxo de compra

def teste_fluxo_compra(chatid, moeda, rede, valor, pix=False):
    print(f"\n--- Teste Compra ---")
    print(f"ChatID: {chatid}")
    print(f"Moeda: {moeda}")
    print(f"Rede: {rede}")
    print(f"Valor: R${valor:.2f}")
    print(f"PIX: {pix}")
    print(f"Limite atual: R${get_limite(chatid):.2f}")
    print("Resumo:")
    print(gerar_resumo_compra(chatid, moeda, rede, valor, pix=pix))
    if not precisa_cpf(chatid, valor) and not precisa_atendente(valor):
        registrar_compra(chatid, valor)
        print(f"Compra registrada! Novo limite: R${get_limite(chatid):.2f}")
    else:
        print("Compra não registrada devido ao limite ou necessidade de CPF/atendente.")
    print("Cotação:", get_cotacao(moeda))
    print("Comissão:", calcular_comissao(valor, moeda, pix=pix))

if __name__ == "__main__":
    chatid = "testuser"
    # Testes variados
    teste_fluxo_compra(chatid, "Bitcoin", "Lightning", 400)
    teste_fluxo_compra(chatid, "Bitcoin", "Lightning", 600)
    teste_fluxo_compra(chatid, "DEPIX", "Liquid", 1000)
    teste_fluxo_compra(chatid, "USDT", "Polygon", 2000, pix=True)
    teste_fluxo_compra(chatid, "Bitcoin", "Onchain", 6000)
