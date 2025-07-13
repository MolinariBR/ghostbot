from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from api.api_rest_cotacao import get_cotacao_rest  # Corrigido nome da função
from config.config import BASE_URL

# 1 Passo - Menu de compra

MENU_OPCOES = [['Comprar', 'Vender'], ['Termos', 'Ajuda']]
menu_markup = ReplyKeyboardMarkup(MENU_OPCOES, resize_keyboard=True)

MENU_MOEDAS = [["BTC", "USDT", "DEPIX"], ["Voltar"]]
moedas_markup = ReplyKeyboardMarkup(MENU_MOEDAS, resize_keyboard=True)

async def mostrar_menu_compra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is not None:
        await update.message.reply_text(
            "Escolha uma opção:",
            reply_markup=menu_markup
        )
# 2 Passo - Escolher moeda
async def tratar_opcao_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text if update.message else None
    # Verificar se update.effective_chat não é None
    if update.effective_chat is None:
        return
    
    # Verifica se está aguardando endereço Lightning
    if context.user_data and context.user_data.get("aguardando_endereco_lightning"):
        await processar_endereco_lightning(update, context)
        return
    
    # Passo 2 - Escolher moeda
    if texto == "Comprar":
        if update.message is not None:
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
        if update.message is not None:
            await update.message.reply_text(
                "Selecione a rede para BTC:",
                reply_markup=redes_markup
            )
        return
    if texto == "DEPIX":
        redes_depix = [["Liquid"], ["Voltar"]]
        redes_markup = ReplyKeyboardMarkup(redes_depix, resize_keyboard=True)
        if update.message is not None:
            await update.message.reply_text(
                "Selecione a rede para DEPIX:",
                reply_markup=redes_markup
            )
        return
    if texto == "USDT":
        redes_usdt = [["Liquid", "Polygon"], ["Voltar"]]
        redes_markup = ReplyKeyboardMarkup(redes_usdt, resize_keyboard=True)
        if update.message is not None:
            await update.message.reply_text(
                "Selecione a rede para USDT:",
                reply_markup=redes_markup
            )
        return
    # Passo 4 - Valor do investimento
    valores_fixos = [["10.00", "25.00", "50.00"], ["250.00", "500.00", "850.00"], ["Voltar"]]
    valores_markup = ReplyKeyboardMarkup(valores_fixos, resize_keyboard=True, one_time_keyboard=True)
    if texto in ["Ochain", "Liquid", "Lightning", "Polygon"]:
        if update.message is not None:
            await update.message.reply_text(
                "Informe o valor do investimento ou escolha uma opção:",
                reply_markup=valores_markup
            )
            await update.message.reply_text(
                "Você também pode digitar um valor personalizado (mínimo 10.00, máximo 4999.99)")
        return
    if texto == "Voltar":
        if update.message is not None:
            await update.message.reply_text(
                "Selecione a moeda:",
                reply_markup=moedas_markup
            )
        return
    # Validação do valor personalizado
    try:
        if texto is not None:
            valor = float(texto.replace(",", "."))
        else:
            valor = None
        amount_in_cents = int(valor * 100) if valor is not None else None
        if amount_in_cents is not None and 1000 <= amount_in_cents <= 499999:
            valor_real = amount_in_cents / 100
            if context.user_data is not None:
                context.user_data["valor_real"] = valor_real  # Salva o valor no contexto
            if update.message is not None:
                await update.message.reply_text(f"Valor selecionado: {valor_real:.2f}")
            # Passo 5 - Resumo da compra integrado ao backend Python
            moeda_raw = context.user_data.get("moeda", "BTC") if context.user_data else "BTC"
            moeda_raw = moeda_raw.lower()
            if moeda_raw == "btc":
                moeda = "bitcoin"
            elif moeda_raw == "usdt":
                moeda = "usdt"
            elif moeda_raw == "depix":
                moeda = "depix"
            else:
                moeda = moeda_raw
            rede = context.user_data.get("rede", "Lightning") if context.user_data else "Lightning"
            chatid = str(update.effective_chat.id)
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
            if not data or not data.get("success"):
                if update.message is not None:
                    await update.message.reply_text(f"Erro ao validar pedido: {data.get('error') if data else 'Erro desconhecido'}")
                return
            validador = data.get("validador") if data else None
            gtxid = data.get("gtxid") if data else None
            # Calcula o valor que o cliente recebe
            valor_recebe = None
            if validador and "cotacao" in validador and "comissao" in validador and "parceiro" in validador:
                valor_brl = float(valor_real)
                comissao_data = validador.get("comissao")
                parceiro_val = validador.get("parceiro")
                cotacao_data = validador.get("cotacao")
                
                if comissao_data and "comissao" in comissao_data and parceiro_val is not None and cotacao_data and "valor" in cotacao_data:
                    comissao = float(comissao_data["comissao"])
                    parceiro = float(parceiro_val)
                    cotacao = float(cotacao_data["valor"])
                    valor_recebe = valor_brl - comissao - parceiro
                    # Se cotacao > 0, converte para moeda escolhida
                    if cotacao > 0:
                        valor_recebe_moeda = valor_recebe / cotacao
                    else:
                        valor_recebe_moeda = 0.0
                else:
                    valor_recebe_moeda = None
            else:
                valor_recebe_moeda = None
            
            # Salva os dados importantes no contexto
            if context.user_data is not None:
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
            )
            if validador:
                comissao_data = validador.get("comissao")
                parceiro_val = validador.get("parceiro")
                cotacao_data = validador.get("cotacao")
                limite_val = validador.get("limite")
                
                if comissao_data and "comissao" in comissao_data:
                    resumo += f"Comissão: {comissao_data['comissao']:.2f}\n"
                if parceiro_val is not None:
                    resumo += f"Parceiro: {parceiro_val:.2f}\n"
                if cotacao_data and "valor" in cotacao_data:
                    resumo += f"Cotação: {cotacao_data['valor']:.2f}\n"
                if limite_val is not None:
                    resumo += f"Limite: {limite_val}\n"
            if valor_recebe_moeda is not None:
                resumo += f"Você Recebe: {valor_recebe_moeda:.8f} {moeda.upper()}"
            if update.message is not None:
                await update.message.reply_text(resumo)
            # Passo 6 - Confirmar Pedido
            confirmar_markup = ReplyKeyboardMarkup([["Confirmar Pedido"], ["Voltar"]], resize_keyboard=True)
            if update.message is not None:
                await update.message.reply_text(
                    "Confirme o pedido para prosseguir:",
                    reply_markup=confirmar_markup
                )
            return
        elif amount_in_cents is not None and amount_in_cents < 1000:
            if update.message is not None:
                await update.message.reply_text("Valor mínimo permitido é 1000 centavos (10.00)")
            return
        elif amount_in_cents is not None and amount_in_cents > 499999:
            if update.message is not None:
                await update.message.reply_text(
                    "Para compras acima do limite máximo, fale diretamente com nosso atendente: @GhosttP2P_bot"
                )
            return
    except ValueError:
        pass
    # Passo 6 - Confirmação do pedido
    if texto == "Confirmar Pedido":
        # Recupera dados do último pedido do contexto
        moeda = context.user_data.get("moeda", "bitcoin") if context.user_data else "bitcoin"
        rede = context.user_data.get("rede", "Lightning") if context.user_data else "Lightning"
        valor_real = context.user_data.get("valor_real") if context.user_data else None
        gtxid = context.user_data.get("gtxid") if context.user_data else None
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
            if result and result.get("success"):
                if update.message is not None:
                    await update.message.reply_text("Pedido registrado com sucesso! Aguarde instruções de pagamento.")
            else:
                if update.message is not None:
                    await update.message.reply_text(f"Erro ao registrar pedido: {result.get('error') if result else 'Erro desconhecido'}")
        except Exception as e:
            if update.message is not None:
                await update.message.reply_text(f"Erro inesperado ao registrar pedido: {str(e)}")
        # Passo 7 - Forma de Pagamento
        formas_pagamento = [["PIX", "TED", "BOLETO"], ["Voltar"]]
        pagamento_markup = ReplyKeyboardMarkup(formas_pagamento, resize_keyboard=True)
        if update.message is not None:
            await update.message.reply_text(
                "Selecione a forma de pagamento:",
                reply_markup=pagamento_markup
            )
        return
    # Passo 7 - Forma de Pagamento
    if texto == "TED" or texto == "BOLETO":
        if update.message is not None:
            await update.message.reply_text(
                "Para pagamentos via TED ou BOLETO, fale diretamente com nosso atendente: @GhosttP2P_bot"
            )
        return
    if texto == "PIX":
        # Recupera dados do pedido do contexto
        gtxid = context.user_data.get("gtxid") if context.user_data else None
        chatid = update.effective_chat.id
        valor = context.user_data.get("valor_real") if context.user_data else None
        
        # Debug: Mostra todos os dados atuais
        print(f"[DEBUG] Dados do pedido no PIX:")
        print(f"- gtxid: {gtxid}")
        print(f"- valor: {valor}")
        print(f"- context.user_data: {context.user_data}")
        
        if not all([gtxid, valor]):
            if update.message is not None:
                await update.message.reply_text(
                    f"Erro: Dados do pedido não encontrados. Por favor, inicie um novo pedido.\n\nDados faltando:\n- gtxid: {'OK' if gtxid else 'Faltando'}\n- valor: {'OK' if valor else 'Faltando'}\n\nDados atuais: {context.user_data}"
                )
        if update.message is not None:
            await update.message.reply_text("Gerando código PIX...")
        
        try:
            from api.bot_deposit import criar_deposito_pix
            
            # Verificar se gtxid e valor não são None antes de chamar a função
            if gtxid is not None and valor is not None:
                # Chama a função para criar o PIX
                resultado = criar_deposito_pix(
                    gtxid=str(gtxid),
                    chatid=str(chatid),
                    valor=float(valor),
                    moeda="BRL"
                )
                
                if resultado and resultado.get("success"):
                    # Obtém os dados do PIX da resposta
                    pix_data = resultado.get("data", {})
                    
                    # Extrai o transaction_id
                    transaction_id = pix_data.get('transaction_id', '')
                    
                    # Primeiro envia a imagem do QR Code
                    qr_image_url = pix_data.get('qr_image_url')
                    if qr_image_url:
                        try:
                            if update.message is not None:
                                await update.message.reply_photo(
                                    photo=qr_image_url,
                                    caption="🔍 Escaneie o QR Code para efetuar o pagamento"
                                )
                        except Exception as e:
                            print(f"[ERRO] Não foi possível enviar a imagem do QR Code: {str(e)}")
                            if update.message is not None:
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
                    if update.message is not None:
                        await update.message.reply_text(
                            mensagem,
                            parse_mode='Markdown',
                            disable_web_page_preview=True
                        )
                    
                    # 8º PASSO: Ativa o validador de depósito PIX
                    if context.user_data is not None:
                        context.user_data["depix_id"] = transaction_id
                    
                    # Inicia a verificação do pagamento em background
                    asyncio.create_task(
                        verificar_pagamento_pix(update, context, transaction_id, tentativas=5)
                    )
                    
                else:
                    if update.message is not None:
                        await update.message.reply_text(
                            f"❌ Erro ao gerar PIX: {resultado.get('error') if resultado else 'Erro desconhecido'}"
                        )
            else:
                if update.message is not None:
                    await update.message.reply_text("❌ Dados inválidos para gerar PIX")
                    
        except Exception as e:
            if update.message is not None:
                await update.message.reply_text(
                    f"❌ Ocorreu um erro inesperado: {str(e)}"
                )
        # Aqui pode seguir para o fluxo PIX
        return
    if texto == "Voltar":
        # Volta para o resumo da compra ou etapa anterior
        # Recomenda-se reexibir o resumo e o menu de confirmação
        confirmar_markup = ReplyKeyboardMarkup([["Confirmar Pedido"], ["Voltar"]], resize_keyboard=True)
        if update.message is not None:
            await update.message.reply_text(
                "Confirme o pedido para prosseguir:",
                reply_markup=confirmar_markup
            )
        return




async def consultar_deposito_por_depix_id(depix_id: str) -> Dict[str, Any]:
    """
    Consulta os dados do depósito no backend.
    
    Args:
        depix_id: ID do depósito PIX
        
    Returns:
        Dicionário com os dados do depósito
    """
    try:
        url = f"{BASE_URL}/deposit.php"
        params = {"action": "get", "depix_id": depix_id}
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def verificar_pagamento_pix(update: Update, context: ContextTypes.DEFAULT_TYPE, depix_id: str, tentativas: int = 5) -> bool:
    """
    Verifica o status do pagamento PIX com tentativas limitadas.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do Telegram
        depix_id: ID do depósito PIX
        tentativas: Número máximo de tentativas (padrão: 5)
        
    Returns:
        True se o blockchainTxID foi encontrado, False caso contrário
    """
    if update.message is None:
        return False
    
    # Mensagem inicial
    await update.message.reply_text(
        "🔍 Verificando confirmação do pagamento PIX...\n"
        "⏳ Aguarde enquanto validamos sua transação."
    )
    
    for i in range(tentativas):
        try:
            # Consulta os dados do depósito diretamente
            deposito_data = await consultar_deposito_por_depix_id(depix_id)
            
            if deposito_data.get("blockchainTxID"):
                # Sucesso! blockchainTxID encontrado
                await update.message.reply_text(
                    "✅ Pagamento confirmado!\n"
                    "🔗 Blockchain TxID encontrado.\n"
                    "📬 Por favor, envie seu endereço Lightning (Lightning Address ou Invoice) para receber seus satoshis."
                )
                
                # Ativa o handler para endereços Lightning
                if context.user_data is not None:
                    context.user_data["aguardando_endereco_lightning"] = True
                    context.user_data["depix_id_confirmado"] = depix_id
                
                return True
            else:
                # Ainda sem blockchainTxID
                status = deposito_data.get("status", "pending")
                await update.message.reply_text(
                    f"⏳ Aguardando confirmação do PIX...\n"
                    f"Status: {status}\n"
                    f"Tentativa {i+1}/{tentativas}"
                )
            
            # Aguarda 30 segundos antes da próxima tentativa (exceto na última)
            if i < tentativas - 1:
                await asyncio.sleep(30)
                
        except Exception as e:
            await update.message.reply_text(
                f"⚠️ Erro na verificação: {str(e)}\n"
                f"Tentativa {i+1}/{tentativas}"
            )
            if i < tentativas - 1:
                await asyncio.sleep(30)
    
    # Falha após todas as tentativas
    await orientar_para_atendimento(update, context)
    return False

async def orientar_para_atendimento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Orienta o usuário para falar com o atendente quando a verificação falha.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do Telegram
    """
    if update.message is not None:
        await update.message.reply_text(
            "❌ Não foi possível confirmar automaticamente seu pagamento.\n\n"
            "🔧 Por favor, entre em contato com nosso atendente:\n"
            "👤 @GhosttP2P_bot\n\n"
            "📋 Informe seu ID de transação para que possamos ajudá-lo."
        )

async def solicitar_endereco_lightning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Solicita o endereço Lightning do cliente após confirmação do PIX.
    
    Args:
        update: Objeto Update do Telegram
        context: Contexto do Telegram
    """
    if update.message is not None:
        await update.message.reply_text(
            "📬 Envie seu endereço Lightning para receber seus satoshis.\n\n"
            "💡 Você pode enviar:\n"
            "• Lightning Address (ex: user@domain.com)\n"
            "• Invoice Lightning (ex: lnbc1...)\n\n"
            "⚠️ Aguarde a confirmação antes de enviar o endereço."
        )

async def processar_endereco_lightning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processa o endereço Lightning enviado pelo cliente.
    
    Args:
        update: Update do Telegram
        context: Contexto do Telegram
    """
    if update.message is None or update.effective_chat is None:
        return
    
    texto = update.message.text
    if not texto:
        return
    
    # Verifica se está aguardando endereço Lightning
    if context.user_data is None or not context.user_data.get("aguardando_endereco_lightning"):
        await update.message.reply_text(
            "⚠️ Aguarde a confirmação do pagamento antes de enviar seu endereço Lightning."
        )
        return
    
    depix_id = context.user_data.get("depix_id_confirmado")
    if not depix_id:
        await update.message.reply_text(
            "❌ Erro: ID da transação não encontrado. Por favor, inicie um novo pedido."
        )
        return
    
    # Valida se é um endereço Lightning válido (formato básico)
    if not (texto.startswith("lnbc") or "@" in texto or texto.startswith("lightning:")):
        await update.message.reply_text(
            "❌ Formato inválido. Envie um Lightning Address (user@domain.com) ou Invoice Lightning (lnbc1...)."
        )
        return
    
    # Confirma o endereço recebido
    await update.message.reply_text(
        f"✅ Endereço Lightning recebido!\n"
        f"📬 {texto}\n\n"
        "🔄 Processando pagamento...\n"
        "⏳ Aguarde a confirmação da transação Lightning."
    )
    
    # Limpa o estado de aguardando endereço
    if context.user_data is not None:
        context.user_data["aguardando_endereco_lightning"] = False
        context.user_data["endereco_lightning"] = texto
    
    # Aqui o backend processará automaticamente via trigger_txid.php
    # O bot apenas confirma o recebimento do endereço
