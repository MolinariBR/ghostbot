# Lightning Address e Voltz API - Análise Completa

**Data:** 2025-01-27  
**Status:** ✅ CONCLUÍDO  

## 🎯 Pergunta
**A Voltz aceita Lightning Address (endereços amigáveis como zews21@ripio.com ou da Wallet of Satoshi)?**

## 📋 Resposta Direta
**❌ NÃO** - A Voltz API **NÃO aceita Lightning Address diretamente**. 

A Voltz aceita apenas **BOLT11 invoices** nos endpoints `/api/v1/payments` e `/api/v1/payments/decode`.

## 🔍 Evidências dos Testes

### Teste 1: Lightning Address na Voltz
```bash
# Testando: zews21@ripio.com
Status: 400
Response: "Failed to decode: Bech32 string is not valid."

# Testando: test@walletofsatoshi.com  
Status: 400
Response: "Failed to decode: Bech32 string is not valid."
```

### Teste 2: BOLT11 na Voltz (funciona)
```bash
Status: 200
Response: Decodificação bem-sucedida com dados completos
```

### Teste 3: Lightning Address funciona em outros serviços
```bash
# https://walletofsatoshi.com/.well-known/lnurlp/test
Status: 200
Callback: https://livingroomofsatoshi.com/api/v1/lnurl/payreq/...
Metadata: [["text/identifier","test@walletofsatoshi.com"]]
```

## 📚 O que é Lightning Address?

Lightning Address é um protocolo baseado no **LUD-16** (LNURL RFC) que permite:

- **Formato amigável:** `user@domain.com` (como email)
- **Baseado em LNURL-pay:** Protocolo LUD-06 + LUD-16
- **Resolução automática:** `https://domain/.well-known/lnurlp/user`
- **Compatibilidade:** Funciona entre diferentes wallets/serviços

### Como Funciona (LUD-16)
1. **Input:** `zews21@ripio.com`
2. **Resolução:** GET `https://ripio.com/.well-known/lnurlp/zews21`
3. **Response:** Endpoint LNURL-pay com callback
4. **Payment:** Request ao callback → recebe BOLT11
5. **Final:** Paga o BOLT11 via Lightning Network

## 🔧 Implementação Possível

Para aceitar Lightning Address no bot, seria necessário criar uma **camada de conversão**:

```python
def resolve_lightning_address(address: str) -> str:
    """
    Converte Lightning Address → BOLT11
    """
    username, domain = address.split("@")
    
    # 1. Resolver Lightning Address
    url = f"https://{domain}/.well-known/lnurlp/{username}"
    response = requests.get(url)
    lnurl_data = response.json()
    
    # 2. Fazer request de pagamento  
    callback = lnurl_data['callback']
    amount_msat = amount_sats * 1000
    
    pay_response = requests.get(f"{callback}?amount={amount_msat}")
    pay_data = pay_response.json()
    
    # 3. Retornar BOLT11
    return pay_data['pr']  # BOLT11 invoice

# Uso no bot
bolt11 = resolve_lightning_address("user@walletofsatoshi.com")
voltz_api.pay_invoice(bolt11)  # ✅ Funciona na Voltz
```

## 📊 Wallets que Suportam Lightning Address

**Envio (podem pagar para Lightning Address):**
- ✅ Wallet of Satoshi
- ✅ Phoenix  
- ✅ Alby
- ✅ BlueWallet
- ✅ Breez
- ✅ Blixt
- ✅ Zeus
- ✅ Muun (recente)

**Recebimento (oferecem Lightning Address):**
- ✅ user@walletofsatoshi.com
- ✅ user@getalby.com  
- ✅ user@strike.me
- ✅ user@ln.tips (LightningTipBot)
- ✅ user@stacker.news
- ✅ user@zbd.gg

## 🎯 Recomendações

### Opção 1: Manter Apenas BOLT11 ✅ Recomendado
- **Prós:** Funciona diretamente, sem complexidade adicional
- **Contras:** UX menos amigável (QR codes, invoices longos)
- **Implementação:** Zero mudanças necessárias

### Opção 2: Adicionar Suporte Lightning Address
- **Prós:** UX melhor, compatibilidade com wallets modernos
- **Contras:** Código adicional, mais pontos de falha
- **Implementação:** Camada de conversão Lightning Address → BOLT11

### Opção 3: Atualizar Mensagens do Bot
- **Ação:** Esclarecer nas mensagens que apenas BOLT11 é aceito
- **Exemplo:** "Cole seu invoice Lightning (BOLT11). Lightning Address não suportado."

## 📋 Documentação Referência

- **LUD-16:** https://github.com/lnurl/luds/blob/luds/16.md
- **Lightning Address:** https://lightningaddress.com/  
- **LNURL RFC:** https://github.com/lnurl/luds
- **Voltz API:** /home/mau/bot/ghostbackend/voltz/VOLTZREADME.md

## ✅ Conclusão Final

**A Voltz NÃO aceita Lightning Address diretamente.**

O bot Ghost atual está **correto** ao solicitar apenas BOLT11 invoices. Lightning Address precisaria de implementação adicional para conversão LNURL → BOLT11 antes de usar a Voltz API.

**Status do sistema:** ✅ **FUNCIONANDO CORRETAMENTE**
