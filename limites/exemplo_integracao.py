"""
Exemplo de Integração dos Limites de Valor com os Menus do Bot
Demonstra como usar o módulo de limites nos handlers de compra e venda.
"""

# Exemplo de como usar nos menus de compra
def exemplo_integracao_menu_compra():
    """
    Exemplo de como integrar a validação de limites no menu de compra.
    """
    from limites import validar_valor_pix_compra, obter_mensagem_limites_pix_compra
    
    # Quando o usuário enviar um valor para compra
    async def processar_valor_compra(update, context, valor_str):
        try:
            # Converter string para float
            valor = float(valor_str.replace(',', '.'))
            
            # Validar o valor usando o módulo de limites
            validacao = validar_valor_pix_compra(valor)
            
            if not validacao["valido"]:
                # Valor inválido - mostrar erro e limites
                mensagem_erro = (
                    f"❌ *Valor Inválido*\n\n"
                    f"{validacao['mensagem']}\n\n"
                    f"{obter_mensagem_limites_pix_compra()}"
                )
                await update.message.reply_text(mensagem_erro, parse_mode='Markdown')
                return None
            
            # Valor válido - prosseguir com a compra
            await update.message.reply_text(
                f"✅ Valor de R$ {valor:.2f} confirmado!\n"
                f"Prosseguindo com a compra..."
            )
            return valor
            
        except ValueError:
            # Valor não é um número válido
            await update.message.reply_text(
                f"❌ Formato inválido!\n\n"
                f"{obter_mensagem_limites_pix_compra()}"
            )
            return None

# Exemplo de uso no handler de compra atual
def exemplo_atualizacao_handler_compra():
    """
    Exemplo de como atualizar o handler de compra existente.
    """
    code_example = '''
    # No arquivo menus/menu_compra.py
    from limites import validar_valor_pix_compra, obter_mensagem_limites_pix_compra
    
    async def processar_valor_compra(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para processar valor de compra com validação de limites."""
        valor_texto = update.message.text.strip()
        
        try:
            # Limpar e converter valor
            valor_limpo = valor_texto.replace('R$', '').replace(' ', '').replace(',', '.')
            valor = float(valor_limpo)
            
            # Validar limites
            validacao = validar_valor_pix_compra(valor)
            
            if not validacao["valido"]:
                # Mostrar erro específico baseado no tipo
                if validacao["erro"] == "VALOR_MINIMO":
                    mensagem = (
                        f"📉 *Valor Muito Baixo*\\n\\n"
                        f"O valor mínimo para compra é **R$ {validacao['limite_min']:.2f}**\\n\\n"
                        f"💡 Tente um valor maior que R$ {validacao['limite_min']:.2f}"
                    )
                elif validacao["erro"] == "VALOR_MAXIMO":
                    mensagem = (
                        f"📈 *Valor Muito Alto*\\n\\n"
                        f"O valor máximo para compra é **R$ {validacao['limite_max']:.2f}**\\n\\n"
                        f"💡 Para valores maiores, entre em contato conosco"
                    )
                
                await update.message.reply_text(mensagem, parse_mode='Markdown')
                return VALOR_COMPRA  # Voltar para solicitar valor novamente
            
            # Valor válido - armazenar e prosseguir
            context.user_data['valor_compra'] = valor
            
            # Mostrar confirmação e próximo passo
            await update.message.reply_text(
                f"✅ *Valor Confirmado*\\n\\n"
                f"💰 Valor: R$ {valor:.2f}\\n"
                f"📝 Gerando dados para pagamento..."
            )
            
            # Prosseguir para próximo estado (gerar PIX, etc.)
            return CONFIRMAR_COMPRA
            
        except (ValueError, AttributeError):
            # Formato inválido
            await update.message.reply_text(
                f"❌ *Formato Inválido*\\n\\n"
                f"📝 Digite apenas números\\n"
                f"Exemplo: 100.50 ou 100,50\\n\\n"
                f"{obter_mensagem_limites_pix_compra()}",
                parse_mode='Markdown'
            )
            return VALOR_COMPRA
    '''
    
    print("Exemplo de código para integração:")
    print(code_example)

if __name__ == "__main__":
    exemplo_atualizacao_handler_compra()
