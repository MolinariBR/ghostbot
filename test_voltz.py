from api.voltz import VoltzAPI

if __name__ == "__main__":
    voltz = VoltzAPI()
    print("Testando saldo da carteira...")
    try:
        saldo = voltz.get_wallet_balance()
        print(f"Saldo da carteira: {saldo} sats")
    except Exception as e:
        print(f"Erro ao consultar saldo: {e}")

    print("Testando criação de link de saque...")
    try:
        # Valor de teste: 1000 sats
        result = voltz.create_withdraw_link(amount_sats=1000, description="Teste saque bot")
        print(f"Resultado: {result}")
        if 'lnurl' in result and 'qr_code_url' in result:
            print(voltz.format_withdraw_message(1000, result['lnurl'], result['qr_code_url']))
        else:
            print("Resposta inesperada da API Voltz.")
    except Exception as e:
        print(f"Erro ao criar link de saque: {e}")
