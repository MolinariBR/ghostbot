#!/usr/bin/env python3
"""
Sistema de Comissões por Moeda e Faixa de Valor
==============================================

Este módulo implementa o cálculo de comissões baseado nas regras específicas
para cada moeda (BTC, DEPIX, USDT) conforme as faixas de valores.

Regras de Comissão:
-------------------
💰 BTC:
- De R$10,00 a R$500,00: 10% + R$1,00
- De R$500,01 a R$1000,00: 6% + R$1,00
- De R$1000,01 a R$4999,99: 5% + R$1,00

💳 DEPIX:
- A partir de R$100,00: 1,9% + R$1,00

🪙 USDT:
- A partir de R$100,00: 1,9% + R$1,00
"""

from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ComissaoCalculator:
    """
    Calculadora de comissões baseada em regras por moeda e faixa de valor.
    """
    
    # Regras de comissão por moeda
    REGRAS_COMISSAO = {
        'BTC': [
            {
                'min': Decimal('10.00'),
                'max': Decimal('500.00'),
                'percentual': Decimal('0.10'),  # 10%
                'fixo': Decimal('1.00')
            },
            {
                'min': Decimal('500.01'),
                'max': Decimal('1000.00'),
                'percentual': Decimal('0.06'),  # 6%
                'fixo': Decimal('1.00')
            },
            {
                'min': Decimal('1000.01'),
                'max': Decimal('4999.99'),
                'percentual': Decimal('0.05'),  # 5%
                'fixo': Decimal('1.00')
            }
        ],
        'DEPIX': [
            {
                'min': Decimal('100.00'),
                'max': None,  # Sem limite máximo
                'percentual': Decimal('0.019'),  # 1,9%
                'fixo': Decimal('1.00')
            }
        ],
        'USDT': [
            {
                'min': Decimal('100.00'),
                'max': None,  # Sem limite máximo
                'percentual': Decimal('0.019'),  # 1,9%
                'fixo': Decimal('1.00')
            }
        ]
    }
    
    @classmethod
    def calcular_comissao(cls, valor: float, moeda: str) -> Optional[Dict]:
        """
        Calcula a comissão baseada no valor e moeda.
        
        Args:
            valor: Valor em BRL
            moeda: Moeda (BTC, DEPIX, USDT)
            
        Returns:
            Dict com informações da comissão ou None se não aplicável
        """
        try:
            valor_decimal = Decimal(str(valor))
            moeda_upper = moeda.upper()
            
            if moeda_upper not in cls.REGRAS_COMISSAO:
                logger.warning(f"Moeda '{moeda}' não suportada para cálculo de comissão")
                return None
            
            regras = cls.REGRAS_COMISSAO[moeda_upper]
            
            # Encontra a regra aplicável
            for regra in regras:
                min_val = regra['min']
                max_val = regra['max']
                
                # Verifica se o valor está na faixa
                if valor_decimal >= min_val and (max_val is None or valor_decimal <= max_val):
                    # Calcula a comissão
                    comissao_percentual = valor_decimal * regra['percentual']
                    comissao_fixa = regra['fixo']
                    comissao_total = comissao_percentual + comissao_fixa
                    
                    # Valor líquido após desconto da comissão
                    valor_liquido = valor_decimal - comissao_total
                    
                    return {
                        'valor_original': float(valor_decimal),
                        'moeda': moeda_upper,
                        'faixa': {
                            'min': float(min_val),
                            'max': float(max_val) if max_val else None
                        },
                        'comissao': {
                            'percentual': float(regra['percentual'] * 100),  # Para exibir como %
                            'percentual_valor': float(comissao_percentual),
                            'fixo': float(comissao_fixa),
                            'total': float(comissao_total)
                        },
                        'valor_liquido': float(valor_liquido),
                        'percentual_efetivo': float((comissao_total / valor_decimal) * 100)
                    }
            
            # Se chegou aqui, valor fora das faixas
            logger.warning(f"Valor R$ {valor} fora das faixas para {moeda}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao calcular comissão: {e}")
            return None
    
    @classmethod
    def obter_faixas_moeda(cls, moeda: str) -> List[Dict]:
        """
        Obtém as faixas de comissão para uma moeda específica.
        
        Args:
            moeda: Moeda (BTC, DEPIX, USDT)
            
        Returns:
            Lista com as faixas de comissão
        """
        moeda_upper = moeda.upper()
        
        if moeda_upper not in cls.REGRAS_COMISSAO:
            return []
        
        faixas = []
        for regra in cls.REGRAS_COMISSAO[moeda_upper]:
            faixas.append({
                'min': float(regra['min']),
                'max': float(regra['max']) if regra['max'] else None,
                'percentual': float(regra['percentual'] * 100),
                'fixo': float(regra['fixo'])
            })
        
        return faixas
    
    @classmethod
    def validar_valor_minimo(cls, valor: float, moeda: str) -> bool:
        """
        Valida se o valor atende ao mínimo para a moeda.
        
        Args:
            valor: Valor em BRL
            moeda: Moeda (BTC, DEPIX, USDT)
            
        Returns:
            True se o valor é válido, False caso contrário
        """
        moeda_upper = moeda.upper()
        
        if moeda_upper not in cls.REGRAS_COMISSAO:
            return False
        
        regras = cls.REGRAS_COMISSAO[moeda_upper]
        valor_minimo = regras[0]['min']  # Primeira regra tem o menor valor
        
        return Decimal(str(valor)) >= valor_minimo
    
    @classmethod
    def obter_valor_minimo(cls, moeda: str) -> Optional[float]:
        """
        Obtém o valor mínimo para uma moeda.
        
        Args:
            moeda: Moeda (BTC, DEPIX, USDT)
            
        Returns:
            Valor mínimo ou None se moeda não suportada
        """
        moeda_upper = moeda.upper()
        
        if moeda_upper not in cls.REGRAS_COMISSAO:
            return None
        
        regras = cls.REGRAS_COMISSAO[moeda_upper]
        return float(regras[0]['min'])
    
    @classmethod
    def formatar_resumo_comissao(cls, resultado: Dict) -> str:
        """
        Formata um resumo da comissão calculada.
        
        Args:
            resultado: Resultado do cálculo de comissão
            
        Returns:
            String formatada com resumo
        """
        if not resultado:
            return "❌ Comissão não calculada"
        
        moeda = resultado['moeda']
        valor_original = resultado['valor_original']
        comissao = resultado['comissao']
        valor_liquido = resultado['valor_liquido']
        
        resumo = f"""💰 **{moeda}** - Resumo da Comissão

💵 **Valor Original:** R$ {valor_original:.2f}

📊 **Comissão Aplicada:**
▸ Taxa: {comissao['percentual']:.1f}% + R$ {comissao['fixo']:.2f}
▸ Valor Percentual: R$ {comissao['percentual_valor']:.2f}
▸ Valor Fixo: R$ {comissao['fixo']:.2f}
▸ **Total da Comissão:** R$ {comissao['total']:.2f}

💎 **Valor Líquido:** R$ {valor_liquido:.2f}

📈 **Taxa Efetiva:** {resultado['percentual_efetivo']:.2f}%"""
        
        return resumo

# Instância global
comissao_calculator = ComissaoCalculator()

# Funções de conveniência
def calcular_comissao(valor: float, moeda: str) -> Optional[Dict]:
    """Função de conveniência para cálculo de comissão."""
    return ComissaoCalculator.calcular_comissao(valor, moeda)

def obter_faixas_moeda(moeda: str) -> List[Dict]:
    """Função de conveniência para obter faixas de uma moeda."""
    return ComissaoCalculator.obter_faixas_moeda(moeda)

def validar_valor_minimo(valor: float, moeda: str) -> bool:
    """Função de conveniência para validar valor mínimo."""
    return ComissaoCalculator.validar_valor_minimo(valor, moeda)

def obter_valor_minimo(moeda: str) -> Optional[float]:
    """Função de conveniência para obter valor mínimo."""
    return ComissaoCalculator.obter_valor_minimo(moeda)

def formatar_resumo_comissao(resultado: Dict) -> str:
    """Função de conveniência para formatar resumo."""
    return ComissaoCalculator.formatar_resumo_comissao(resultado)

# Exemplo de uso
if __name__ == "__main__":
    # Testes das diferentes moedas e faixas
    print("🧪 TESTES DO SISTEMA DE COMISSÕES")
    print("=" * 50)
    
    # Teste BTC - diferentes faixas
    test_values = [
        (100, 'BTC'),   # Faixa 1: 10%
        (500, 'BTC'),   # Faixa 1: 10%
        (750, 'BTC'),   # Faixa 2: 6%
        (1500, 'BTC'),  # Faixa 3: 5%
        (200, 'DEPIX'), # DEPIX: 1,9%
        (300, 'USDT'),  # USDT: 1,9%
    ]
    
    for valor, moeda in test_values:
        resultado = calcular_comissao(valor, moeda)
        if resultado:
            print(f"\n{formatar_resumo_comissao(resultado)}")
        else:
            print(f"\n❌ Não foi possível calcular comissão para R$ {valor} em {moeda}")
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
