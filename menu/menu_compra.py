from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import aiohttp
from api.api_rest_cotacao import get_cotacao_rest  # Corrigido nome da função

# 1 Passo - Menu de compra

MENU_OPCOES = [['Comprar', 'Vender'], ['Termos', 'Ajuda']]
menu_markup = ReplyKeyboardMarkup(MENU_OPCOES, resize_keyboard=True)

MENU_MOEDAS = [["BTC", "USDT", "DEPIX"], ["Voltar"]]
moedas_markup = ReplyKeyboardMarkup(MENU_MOEDAS, resize_keyboard=True)

async def mostrar_menu_compra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Escolha uma opção:",
        reply_markup=menu_markup
    )
# 2 Passo - Escolher moeda
async def tratar_opcao_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    # Passo 2 - Escolher moeda
    if texto == "Comprar":
        await update.message.reply_text(
            "Selecione a moeda:",
            reply_markup=moedas_markup
        )
        return
    if texto == "Voltar":
        await mostrar_menu_compra(update, context)
        return
    # Passo 3 - Menu de rede
    if texto == "BTC":
        redes_btc = [["Ochain", "Liquid", "Lightning"], ["Voltar"]]
        redes_markup = ReplyKeyboardMarkup(redes_btc, resize_keyboard=True)
        await update.message.reply_text(
            "Selecione a rede para BTC:",
            reply_markup=redes_markup
        )
        return
    if texto == "DEPIX":
        redes_depix = [["Liquid"], ["Voltar"]]
        redes_markup = ReplyKeyboardMarkup(redes_depix, resize_keyboard=True)
        await update.message.reply_text(
            "Selecione a rede para DEPIX:",
            reply_markup=redes_markup
        )
        return
    if texto == "USDT":
        redes_usdt = [["Liquid", "Polygon"], ["Voltar"]]
        redes_markup = ReplyKeyboardMarkup(redes_usdt, resize_keyboard=True)
        await update.message.reply_text(
            "Selecione a rede para USDT:",
            reply_markup=redes_markup
        )
        return
    # Passo 4 - Valor do investimento
    valores_fixos = [["10.00", "25.00", "50.00"], ["250.00", "500.00", "850.00"], ["Voltar"]]
    valores_markup = ReplyKeyboardMarkup(valores_fixos, resize_keyboard=True, one_time_keyboard=True)
    if texto in ["Ochain", "Liquid", "Lightning", "Polygon"]:
        await update.message.reply_text(
            "Informe o valor do investimento ou escolha uma opção:",
            reply_markup=valores_markup
        )
        await update.message.reply_text(
            "Você também pode digitar um valor personalizado (mínimo 10.00, máximo 4999.99)")
        return
    if texto == "Voltar":
        # Volta para o menu de redes
        await update.message.reply_text(
            "Selecione a moeda:",
            reply_markup=moedas_markup
        )
        return
    # Validação do valor personalizado
    try:
        valor = float(texto.replace(",", "."))
        amount_in_cents = int(valor * 100)
        if 1000 <= amount_in_cents <= 499999:
            valor_real = amount_in_cents / 100
            context.user_data["valor_real"] = valor_real  # Salva o valor no contexto
            await update.message.reply_text(f"Valor selecionado: {valor_real:.2f}")
            # Passo 5 - Resumo da compra integrado ao backend Python
            moeda_raw = context.user_data.get("moeda", "BTC").lower()
            if moeda_raw == "btc":
                moeda = "bitcoin"
            elif moeda_raw == "usdt":
                moeda = "usdt"
            elif moeda_raw == "depix":
                moeda = "depix"
            else:
                moeda = moeda_raw
            rede = context.user_data.get("rede", "Lightning")
            chatid = update.effective_chat.id
            compras = 1  # Exemplo, pode ser ajustado conforme fluxo
            metodo = "pix"  # Exemplo, pode ser ajustado conforme fluxo
            # Chamada ao backend REST Python
            data = get_cotacao_rest(
                moeda=moeda,
                vs="brl",
                valor=valor_real,
                chatid=chatid,
                compras=compras,
                metodo=metodo
            )
            if not data.get("success"):
                await update.message.reply_text(f"Erro ao validar pedido: {data.get('error')}")
                return
            validador = data["validador"]
            gtxid = data["gtxid"]
            # Calcula o valor que o cliente recebe
            valor_recebe = None
            if "cotacao" in validador and "comissao" in validador and "parceiro" in validador:
                valor_brl = float(valor_real)
                comissao = float(validador["comissao"]["comissao"])
                parceiro = float(validador["parceiro"])
                cotacao = float(validador["cotacao"]["valor"])
                valor_recebe = valor_brl - comissao - parceiro
                # Se cotacao > 0, converte para moeda escolhida
                if cotacao > 0:
                    valor_recebe_moeda = valor_recebe / cotacao
                else:
                    valor_recebe_moeda = 0.0
            else:
                valor_recebe_moeda = None
            
            # Salva os dados importantes no contexto
            context.user_data["gtxid"] = gtxid
            context.user_data["valor_real"] = valor_real
            context.user_data["moeda"] = moeda
            context.user_data["rede"] = rede
            
            resumo = (
                f"RESUMO DA COMPRA\n"
                f"ID: {gtxid}\n"
                f"Moeda: {moeda}\n"
                f"Rede: {rede}\n"
                f"Valor: {valor_real:.2f}\n"
                f"Comissão: {validador['comissao']['comissao']:.2f}\n"
                f"Parceiro: {validador['parceiro']:.2f}\n"
                f"Cotação: {validador['cotacao']['valor']:.2f}\n"
                f"Limite: {validador['limite']}\n"
                f"Você Recebe: {valor_recebe_moeda:.8f} {moeda.upper()}"
            )
            await update.message.reply_text(resumo)
            # Passo 6 - Confirmar Pedido
            confirmar_markup = ReplyKeyboardMarkup([["Confirmar Pedido"], ["Voltar"]], resize_keyboard=True)
            await update.message.reply_text(
                "Confirme o pedido para prosseguir:",
                reply_markup=confirmar_markup
            )
            return
        elif amount_in_cents < 1000:
            await update.message.reply_text("Valor mínimo permitido é 1000 centavos (10.00)")
            return
        elif amount_in_cents > 499999:
            await update.message.reply_text(
                "Para compras acima do limite máximo, fale diretamente com nosso atendente: @GhosttP2P_bot"
            )
            return
    except ValueError:
        pass
    # Passo 6 - Confirmação do pedido
    if texto == "Confirmar Pedido":
        # Recupera dados do último pedido do contexto
        moeda = context.user_data.get("moeda", "bitcoin")
        rede = context.user_data.get("rede", "Lightning")
        valor_real = context.user_data.get("valor_real")
        gtxid = context.user_data.get("gtxid")
        chatid = update.effective_chat.id
        metodo = "pix"
        # Chama endpoint REST para registrar pedido
        try:
            # Supondo que existe função registrar_pedido_rest (deve ser implementada em api_rest_cotacao.py)
            from api.api_rest_cotacao import registrar_pedido_rest
            result = registrar_pedido_rest(
                moeda=moeda,
                rede=rede,
                valor=valor_real,
                gtxid=gtxid,
                chatid=chatid,
                metodo=metodo
            )
            if result.get("success"):
                await update.message.reply_text("Pedido registrado com sucesso! Aguarde instruções de pagamento.")
            else:
                await update.message.reply_text(f"Erro ao registrar pedido: {result.get('error')}")
        except Exception as e:
            await update.message.reply_text(f"Erro inesperado ao registrar pedido: {str(e)}")
        # Passo 7 - Forma de Pagamento
        formas_pagamento = [["PIX", "TED", "BOLETO"], ["Voltar"]]
        pagamento_markup = ReplyKeyboardMarkup(formas_pagamento, resize_keyboard=True)
        await update.message.reply_text(
            "Selecione a forma de pagamento:",
            reply_markup=pagamento_markup
        )
        return
    # Passo 7 - Forma de Pagamento
    if texto == "TED" or texto == "BOLETO":
        await update.message.reply_text(
            "Para pagamentos via TED ou BOLETO, fale diretamente com nosso atendente: @GhosttP2P_bot"
        )
        return
    if texto == "PIX":
        # Recupera dados do pedido do contexto
        gtxid = context.user_data.get("gtxid")
        chatid = update.effective_chat.id
        valor = context.user_data.get("valor_real")
        
        # Debug: Mostra todos os dados atuais
        print(f"[DEBUG] Dados do pedido no PIX:")
        print(f"- gtxid: {gtxid}")
        print(f"- valor: {valor}")
        print(f"- context.user_data: {context.user_data}")
        
        if not all([gtxid, valor]):
            await update.message.reply_text(
                f"Erro: Dados do pedido não encontrados. Por favor, inicie um novo pedido.\n\nDados faltando:\n- gtxid: {'OK' if gtxid else 'Faltando'}\n- valor: {'OK' if valor else 'Faltando'}\n\nDados atuais: {context.user_data}"
            )
        await update.message.reply_text("Gerando código PIX...")
        
        try:
            from api.bot_deposit import criar_deposito_pix
            
            # Chama a função para criar o PIX
            resultado = criar_deposito_pix(
                gtxid=gtxid,
                chatid=str(chatid),
                valor=valor,
                moeda="BRL"
            )
            
            if resultado.get("success"):
                # Obtém os dados do PIX da resposta
                pix_data = resultado.get("data", {})
                
                # Extrai o transaction_id
                transaction_id = pix_data.get('transaction_id', '')
                
                # Primeiro envia a imagem do QR Code
                qr_image_url = pix_data.get('qr_image_url')
                if qr_image_url:
                    try:
                        await update.message.reply_photo(
                            photo=qr_image_url,
                            caption="🔍 Escaneie o QR Code para efetuar o pagamento"
                        )
                    except Exception as e:
                        print(f"[ERRO] Não foi possível enviar a imagem do QR Code: {str(e)}")
                        await update.message.reply_text(
                            "⚠️ Não foi possível carregar a imagem do QR Code. "
                            "Use o código PIX copia e cola para efetuar o pagamento."
                        )
                
                # Depois envia as informações detalhadas
                mensagem = (
                    "*PAGAMENTO VIA PIX*\n\n"
                    f"*💵 Valor:* R$ {float(valor):.2f}\n"
                    f"*🆔 ID da Transação:* `{transaction_id}`\n"
                    "*📋 Código PIX (copia e cola):*\n"
                    f"`{pix_data.get('qr_copy_paste', 'N/A')}`\n\n"
                    "_⏳ Este PIX expira em 30 minutos._"
                )
                
                # Envia a mensagem formatada
                await update.message.reply_text(
                    mensagem,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
            else:
                await update.message.reply_text(
                    f"❌ Erro ao gerar PIX: {resultado.get('error', 'Erro desconhecido')}"
                )
                
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ocorreu um erro inesperado: {str(e)}"
            )
        # Aqui pode seguir para o fluxo PIX
        return
    if texto == "Voltar":
        # Volta para o resumo da compra ou etapa anterior
        # Recomenda-se reexibir o resumo e o menu de confirmação
        confirmar_markup = ReplyKeyboardMarkup([["Confirmar Pedido"], ["Voltar"]], resize_keyboard=True)
        await update.message.reply_text(
            "Confirme o pedido para prosseguir:",
            reply_markup=confirmar_markup
        )
        return
