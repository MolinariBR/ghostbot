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
