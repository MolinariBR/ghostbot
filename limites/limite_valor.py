#!/usr/bin/env python3
"""
Configurações de Limites de Valor para Transações do Ghost Bot
Define os limites mínimos e máximos para diferentes tipos de transação.
"""

class LimitesValor:
    """
    Classe para definir limites de valor para transações do bot.
    """
    
    # ========================================
    # LIMITES PIX
    # ========================================
    
    # Limites para compra via PIX
    PIX_COMPRA_MIN = 10.00      # Valor mínimo: R$ 10,00
    PIX_COMPRA_MAX = 4999.99    # Valor máximo: R$ 4.999,99
    
    # Limites para venda via PIX
    PIX_VENDA_MIN = 10.00       # Valor mínimo: R$ 10,00
    PIX_VENDA_MAX = 4999.99     # Valor máximo: R$ 4.999,99
    
    # ========================================
    # LIMITES PROGRESSIVOS (ESCALONADOS)
    # ========================================
    
    # Limites progressivos baseados no número de compras
    LIMITE_ESCADA = [
        500.00,   # 1ª compra
        850.00,   # 2ª compra
        1000.00,  # 3ª compra
        2000.00,  # 4ª compra
        2500.00,  # 5ª compra
        3000.00,  # 6ª compra
        3500.00,  # 7ª compra
        4000.00,  # 8ª compra
        4500.00,  # 9ª compra
        4999.99   # 10ª compra ou mais
    ]
    
    # Limite máximo para usuários com CPF validado
    LIMITE_MAXIMO_CPF = 4999.99
    # ========================================
    # LIMITES LIGHTNING (COMENTADO - NÃO USADO)
    # ========================================
    
    # # Limites para Lightning Network (em satoshis)
    # LIGHTNING_MIN_SATS = 1000      # 1.000 satoshis (~R$ 3,50)
    # LIGHTNING_MAX_SATS = 1500000   # 1.500.000 satoshis (~R$ 5.250,00)
    
    # # Limites Lightning em reais (conversão aproximada)
    # LIGHTNING_MIN_BRL = 3.50       # Valor mínimo em reais
    # LIGHTNING_MAX_BRL = 5250.00    # Valor máximo em reais
    
    # ========================================
    # LIMITES TED/DOC (COMENTADO - NÃO USADO)
    # ========================================
    
    # # Limites para transferência bancária
    # TED_MIN = 100.00       # Valor mínimo: R$ 100,00
    # TED_MAX = 50000.00     # Valor máximo: R$ 50.000,00
    
    # ========================================
    # MÉTODOS DE VALIDAÇÃO
    # ========================================
    
    @classmethod
    def validar_pix_compra(cls, valor: float) -> dict:
        """
        Valida se o valor está dentro dos limites para compra via PIX.
        
        Args:
            valor (float): Valor a ser validado
            
        Returns:
            dict: Resultado da validação com status e mensagem
        """
        if valor < cls.PIX_COMPRA_MIN:
            return {
                "valido": False,
                "erro": "VALOR_MINIMO",
                "mensagem": f"Valor mínimo para compra via PIX: R$ {cls.PIX_COMPRA_MIN:.2f}",
                "dica": f"Digite um valor entre R$ {cls.PIX_COMPRA_MIN:.2f} e R$ {cls.PIX_COMPRA_MAX:.2f}",
                "limite_min": cls.PIX_COMPRA_MIN,
                "limite_max": cls.PIX_COMPRA_MAX
            }
        
        if valor > cls.PIX_COMPRA_MAX:
            return {
                "valido": False,
                "erro": "VALOR_MAXIMO",
                "mensagem": f"Valor máximo para compra via PIX: R$ {cls.PIX_COMPRA_MAX:.2f}",
                "dica": f"Digite um valor entre R$ {cls.PIX_COMPRA_MIN:.2f} e R$ {cls.PIX_COMPRA_MAX:.2f}",
                "limite_min": cls.PIX_COMPRA_MIN,
                "limite_max": cls.PIX_COMPRA_MAX
            }
        
        return {
            "valido": True,
            "mensagem": "Valor dentro dos limites permitidos",
            "limite_min": cls.PIX_COMPRA_MIN,
            "limite_max": cls.PIX_COMPRA_MAX
        }
    
    @classmethod
    def validar_pix_venda(cls, valor: float) -> dict:
        """
        Valida se o valor está dentro dos limites para venda via PIX.
        
        Args:
            valor (float): Valor a ser validado
            
        Returns:
            dict: Resultado da validação com status e mensagem
        """
        if valor < cls.PIX_VENDA_MIN:
            return {
                "valido": False,
                "erro": "VALOR_MINIMO",
                "mensagem": f"Valor mínimo para venda via PIX: R$ {cls.PIX_VENDA_MIN:.2f}",
                "dica": f"Digite um valor entre R$ {cls.PIX_VENDA_MIN:.2f} e R$ {cls.PIX_VENDA_MAX:.2f}",
                "limite_min": cls.PIX_VENDA_MIN,
                "limite_max": cls.PIX_VENDA_MAX
            }
        
        if valor > cls.PIX_VENDA_MAX:
            return {
                "valido": False,
                "erro": "VALOR_MAXIMO",
                "mensagem": f"Valor máximo para venda via PIX: R$ {cls.PIX_VENDA_MAX:.2f}",
                "dica": f"Digite um valor entre R$ {cls.PIX_VENDA_MIN:.2f} e R$ {cls.PIX_VENDA_MAX:.2f}",
                "limite_min": cls.PIX_VENDA_MIN,
                "limite_max": cls.PIX_VENDA_MAX
            }
        
        return {
            "valido": True,
            "mensagem": "Valor dentro dos limites permitidos",
            "limite_min": cls.PIX_VENDA_MIN,
            "limite_max": cls.PIX_VENDA_MAX
        }
    
    # @classmethod
    # def validar_lightning(cls, valor_sats: int) -> dict:
    #     """
    #     Valida se o valor em satoshis está dentro dos limites Lightning.
    #     
    #     Args:
    #         valor_sats (int): Valor em satoshis
    #         
    #     Returns:
    #         dict: Resultado da validação com status e mensagem
    #     """
    #     if valor_sats < cls.LIGHTNING_MIN_SATS:
    #         return {
    #             "valido": False,
    #             "erro": "VALOR_MINIMO",
    #             "mensagem": f"Valor mínimo Lightning: {cls.LIGHTNING_MIN_SATS:,} satoshis",
    #             "limite_min": cls.LIGHTNING_MIN_SATS,
    #             "limite_max": cls.LIGHTNING_MAX_SATS
    #         }
    #     
    #     if valor_sats > cls.LIGHTNING_MAX_SATS:
    #         return {
    #             "valido": False,
    #             "erro": "VALOR_MAXIMO",
    #             "mensagem": f"Valor máximo Lightning: {cls.LIGHTNING_MAX_SATS:,} satoshis",
    #             "limite_min": cls.LIGHTNING_MIN_SATS,
    #             "limite_max": cls.LIGHTNING_MAX_SATS
    #         }
    #     
    #     return {
    #         "valido": True,
    #         "mensagem": "Valor dentro dos limites Lightning",
    #         "limite_min": cls.LIGHTNING_MIN_SATS,
    #         "limite_max": cls.LIGHTNING_MAX_SATS
    #     }
    
    # @classmethod
    # def validar_ted(cls, valor: float) -> dict:
    #     """
    #     Valida se o valor está dentro dos limites para TED.
    #     
    #     Args:
    #         valor (float): Valor a ser validado
    #         
    #     Returns:
    #         dict: Resultado da validação com status e mensagem
    #     """
    #     if valor < cls.TED_MIN:
    #         return {
    #             "valido": False,
    #             "erro": "VALOR_MINIMO",
    #             "mensagem": f"Valor mínimo para TED: R$ {cls.TED_MIN:.2f}",
    #             "limite_min": cls.TED_MIN,
    #             "limite_max": cls.TED_MAX
    #         }
    #     
    #     if valor > cls.TED_MAX:
    #         return {
    #             "valido": False,
    #             "erro": "VALOR_MAXIMO",
    #             "mensagem": f"Valor máximo para TED: R$ {cls.TED_MAX:.2f}",
    #             "limite_min": cls.TED_MIN,
    #             "limite_max": cls.TED_MAX
    #         }
    #     
    #     return {
    #         "valido": True,
    #         "mensagem": "Valor dentro dos limites TED",
    #         "limite_min": cls.TED_MIN,
    #         "limite_max": cls.TED_MAX
    #     }
    
    @classmethod
    def obter_limites_formatados(cls) -> dict:
        """
        Retorna todos os limites formatados para exibição.
        
        Returns:
            dict: Limites formatados por tipo de transação
        """
        return {
            "pix": {
                "compra": {
                    "min": f"R$ {cls.PIX_COMPRA_MIN:.2f}",
                    "max": f"R$ {cls.PIX_COMPRA_MAX:.2f}",
                    "range": f"R$ {cls.PIX_COMPRA_MIN:.2f} - R$ {cls.PIX_COMPRA_MAX:.2f}"
                },
                "venda": {
                    "min": f"R$ {cls.PIX_VENDA_MIN:.2f}",
                    "max": f"R$ {cls.PIX_VENDA_MAX:.2f}",
                    "range": f"R$ {cls.PIX_VENDA_MIN:.2f} - R$ {cls.PIX_VENDA_MAX:.2f}"
                }
            }
            # Lightning e TED comentados (desabilitados)
            # "lightning": {
            #     "satoshis": {
            #         "min": f"{cls.LIGHTNING_MIN_SATS:,} sats",
            #         "max": f"{cls.LIGHTNING_MAX_SATS:,} sats",
            #         "range": f"{cls.LIGHTNING_MIN_SATS:,} - {cls.LIGHTNING_MAX_SATS:,} sats"
            #     },
            #     "reais": {
            #         "min": f"R$ {cls.LIGHTNING_MIN_BRL:.2f}",
            #         "max": f"R$ {cls.LIGHTNING_MAX_BRL:.2f}",
            #         "range": f"R$ {cls.LIGHTNING_MIN_BRL:.2f} - R$ {cls.LIGHTNING_MAX_BRL:.2f}"
            #     }
            # },
            # "ted": {
            #     "min": f"R$ {cls.TED_MIN:.2f}",
            #     "max": f"R$ {cls.TED_MAX:.2f}",
            #     "range": f"R$ {cls.TED_MIN:.2f} - R$ {cls.TED_MAX:.2f}"
            # }
        }
    
    @classmethod
    def calcular_limite_progressivo(cls, num_compras: int, cpf: str = None) -> float:
        """
        Calcula o limite progressivo baseado no número de compras realizadas.
        
        Args:
            num_compras (int): Número de compras já realizadas pelo usuário
            cpf (str, optional): CPF do usuário (se fornecido, libera limite máximo)
            
        Returns:
            float: Limite disponível para a próxima compra
        """
        # Se CPF fornecido e válido, retorna limite máximo
        if cpf and cls.validar_cpf_basico(cpf):
            return cls.LIMITE_MAXIMO_CPF
        
        # Converte para índice baseado em 0 (num_compras já realizadas)
        # Para a próxima compra, usamos num_compras como índice
        idx = min(num_compras, len(cls.LIMITE_ESCADA) - 1)
        idx = max(idx, 0)  # Garante que não seja negativo
        
        return cls.LIMITE_ESCADA[idx]
    
    @classmethod
    def validar_cpf_basico(cls, cpf: str) -> bool:
        """
        Validação básica de CPF (apenas formato e dígitos).
        
        Args:
            cpf (str): CPF a ser validado
            
        Returns:
            bool: True se CPF é válido, False caso contrário
        """
        import re
        
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se não são todos números iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Validação dos dígitos verificadores
        def calcular_digito(cpf_parcial):
            soma = 0
            for i, digit in enumerate(cpf_parcial):
                soma += int(digit) * (len(cpf_parcial) + 1 - i)
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Valida primeiro dígito
        if int(cpf[9]) != calcular_digito(cpf[:9]):
            return False
        
        # Valida segundo dígito
        if int(cpf[10]) != calcular_digito(cpf[:10]):
            return False
        
        return True
    
    @classmethod
    def validar_compra_progressiva(cls, valor: float, num_compras: int, cpf: str = None) -> dict:
        """
        Valida uma compra considerando limites PIX + limites progressivos.
        
        Args:
            valor (float): Valor da compra
            num_compras (int): Número de compras já realizadas
            cpf (str, optional): CPF do usuário
            
        Returns:
            dict: Resultado da validação combinada
        """
        # Primeiro, valida limites PIX básicos
        validacao_pix = cls.validar_pix_compra(valor)
        if not validacao_pix['valido']:
            return validacao_pix
        
        # Calcula limite progressivo atual
        limite_progressivo = cls.calcular_limite_progressivo(num_compras, cpf)
        
        # Verifica se valor está dentro do limite progressivo
        if valor > limite_progressivo:
            return {
                "valido": False,
                "erro": "LIMITE_PROGRESSIVO",
                "mensagem": f"Limite para esta compra: R$ {limite_progressivo:.2f}",
                "dica": f"Digite um valor até R$ {limite_progressivo:.2f} ou forneça seu CPF para aumentar o limite",
                "limite_progressivo": limite_progressivo,
                "num_compras": num_compras,
                "cpf_necessario": cpf is None and limite_progressivo < cls.LIMITE_MAXIMO_CPF
            }
        
        return {
            "valido": True,
            "mensagem": "Valor dentro dos limites permitidos",
            "limite_progressivo": limite_progressivo,
            "num_compras": num_compras,
            "limite_pix_min": cls.PIX_COMPRA_MIN,
            "limite_pix_max": cls.PIX_COMPRA_MAX
        }
    
    @classmethod
    def obter_info_limite_progressivo(cls, num_compras: int, cpf: str = None) -> dict:
        """
        Obtém informações sobre o limite progressivo atual.
        
        Args:
            num_compras (int): Número de compras já realizadas
            cpf (str, optional): CPF do usuário
            
        Returns:
            dict: Informações sobre o limite atual
        """
        limite_atual = cls.calcular_limite_progressivo(num_compras, cpf)
        
        # Próximo limite (se houver)
        proximo_limite = None
        if num_compras + 1 < len(cls.LIMITE_ESCADA):
            proximo_limite = cls.LIMITE_ESCADA[num_compras + 1]
        
        return {
            "limite_atual": limite_atual,
            "proximo_limite": proximo_limite,
            "num_compras": num_compras,
            "tem_cpf": cpf is not None and cls.validar_cpf_basico(cpf),
            "limite_maximo": cls.LIMITE_MAXIMO_CPF,
            "compras_para_proximo": 1 if proximo_limite else 0
        }

# ========================================
# FUNÇÕES DE CONVENIÊNCIA
# ========================================

def validar_valor_pix_compra(valor: float) -> dict:
    """
    Função de conveniência para validar valor de compra via PIX.
    
    Args:
        valor (float): Valor a ser validado
        
    Returns:
        dict: Resultado da validação
    """
    return LimitesValor.validar_pix_compra(valor)

def validar_valor_pix_venda(valor: float) -> dict:
    """
    Função de conveniência para validar valor de venda via PIX.
    
    Args:
        valor (float): Valor a ser validado
        
    Returns:
        dict: Resultado da validação
    """
    return LimitesValor.validar_pix_venda(valor)

def obter_limites_pix() -> dict:
    """
    Retorna os limites PIX formatados.
    
    Returns:
        dict: Limites PIX formatados
    """
    limites = LimitesValor.obter_limites_formatados()
    return limites["pix"]

def obter_mensagem_limites_pix_compra() -> str:
    """
    Retorna mensagem formatada com limites para compra PIX.
    
    Returns:
        str: Mensagem com limites
    """
    return (
        f"💰 *Limites para Compra via PIX*\n\n"
        f"🔹 Valor mínimo: R$ {LimitesValor.PIX_COMPRA_MIN:.2f}\n"
        f"🔹 Valor máximo: R$ {LimitesValor.PIX_COMPRA_MAX:.2f}\n\n"
        f"📝 Informe um valor entre R$ {LimitesValor.PIX_COMPRA_MIN:.2f} e R$ {LimitesValor.PIX_COMPRA_MAX:.2f}"
    )

def obter_mensagem_limites_pix_venda() -> str:
    """
    Retorna mensagem formatada com limites para venda PIX.
    
    Returns:
        str: Mensagem com limites
    """
    return (
        f"💰 *Limites para Venda via PIX*\n\n"
        f"🔹 Valor mínimo: R$ {LimitesValor.PIX_VENDA_MIN:.2f}\n"
        f"🔹 Valor máximo: R$ {LimitesValor.PIX_VENDA_MAX:.2f}\n\n"
        f"📝 Informe um valor entre R$ {LimitesValor.PIX_VENDA_MIN:.2f} e R$ {LimitesValor.PIX_VENDA_MAX:.2f}"
    )

def validar_compra_com_limite_progressivo(valor: float, num_compras: int, cpf: str = None) -> dict:
    """
    Função de conveniência para validar compra com limite progressivo.
    
    Args:
        valor (float): Valor da compra
        num_compras (int): Número de compras já realizadas
        cpf (str, optional): CPF do usuário
        
    Returns:
        dict: Resultado da validação
    """
    return LimitesValor.validar_compra_progressiva(valor, num_compras, cpf)

def calcular_limite_atual(num_compras: int, cpf: str = None) -> float:
    """
    Função de conveniência para calcular limite atual.
    
    Args:
        num_compras (int): Número de compras já realizadas
        cpf (str, optional): CPF do usuário
        
    Returns:
        float: Limite atual
    """
    return LimitesValor.calcular_limite_progressivo(num_compras, cpf)

def obter_info_limites_usuario(num_compras: int, cpf: str = None) -> dict:
    """
    Função de conveniência para obter informações completas dos limites.
    
    Args:
        num_compras (int): Número de compras já realizadas
        cpf (str, optional): CPF do usuário
        
    Returns:
        dict: Informações completas dos limites
    """
    return LimitesValor.obter_info_limite_progressivo(num_compras, cpf)

def obter_mensagem_limite_progressivo(num_compras: int, cpf: str = None) -> str:
    """
    Retorna mensagem formatada com informações do limite progressivo.
    
    Args:
        num_compras (int): Número de compras já realizadas
        cpf (str, optional): CPF do usuário
        
    Returns:
        str: Mensagem formatada
    """
    info = LimitesValor.obter_info_limite_progressivo(num_compras, cpf)
    
    mensagem = f"📊 *Seus Limites Atuais*\n\n"
    mensagem += f"🔹 Limite atual: R$ {info['limite_atual']:.2f}\n"
    mensagem += f"🔹 Compras realizadas: {info['num_compras']}\n"
    
    if info['tem_cpf']:
        mensagem += f"✅ CPF verificado - Limite máximo liberado\n"
    else:
        mensagem += f"⚠️ CPF não fornecido\n"
    
    if info['proximo_limite']:
        mensagem += f"🎯 Próximo limite: R$ {info['proximo_limite']:.2f}\n"
        mensagem += f"📈 Faltam {info['compras_para_proximo']} compra(s) para aumentar o limite\n"
    else:
        mensagem += f"🏆 Limite máximo alcançado!\n"
    
    return mensagem

# ========================================
# EXEMPLO DE USO
# ========================================

if __name__ == "__main__":
    # Exemplo de uso do sistema de limites
    print("=== TESTE DO SISTEMA DE LIMITES ===\n")
    
    # Teste PIX Compra
    print("🔹 Teste PIX Compra:")
    valores_teste = [5.00, 10.00, 100.00, 4999.99, 5000.00]
    
    for valor in valores_teste:
        resultado = validar_valor_pix_compra(valor)
        status = "✅ VÁLIDO" if resultado["valido"] else "❌ INVÁLIDO"
        print(f"  R$ {valor:.2f} - {status}: {resultado['mensagem']}")
    
    print("\n" + "="*50 + "\n")
    
    # Exibir limites formatados
    print("📋 Limites Configurados:")
    limites = LimitesValor.obter_limites_formatados()
    
    print(f"🔹 PIX Compra: {limites['pix']['compra']['range']}")
    print(f"🔹 PIX Venda: {limites['pix']['venda']['range']}")
    print(f"🔹 Lightning: {limites['lightning']['satoshis']['range']}")
    print(f"🔹 TED: {limites['ted']['range']}")
