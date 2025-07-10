#!/usr/bin/env python3
"""
Teste de Cenários de Erro do Ghost Bot
Testa falhas e recuperações do sistema
"""

import requests
import json
import time
from test_fluxo_compra_completo import TesteFluxoCompleto

class TesteCenariosErro(TesteFluxoCompleto):
    def __init__(self):
        super().__init__()
        self.cenarios_testados = []
    
    def testar_lightning_address_invalido(self):
        """Testa Lightning Address inválido"""
        print("\n🧪 TESTE: Lightning Address Inválido")
        
        addresses_invalidos = [
            "email_invalido@exemplo.com",
            "sem_dominio",
            "@apenas_dominio.com",
            "usuario@",
            "usuario@dominio_inexistente.xyz123",
            ""
        ]
        
        resultados = []
        for address in addresses_invalidos:
            try:
                self.lightning_address = address
                resultado = self.lightning_handler.is_lightning_address(address)
                resultados.append({
                    'address': address,
                    'valido': resultado,
                    'esperado': False
                })
                print(f"{'✅' if not resultado else '❌'} {address}: {resultado}")
            except Exception as e:
                resultados.append({
                    'address': address,
                    'erro': str(e),
                    'esperado': False
                })
                print(f"⚠️ {address}: Erro - {e}")
        
        return resultados
    
    def testar_valores_limite(self):
        """Testa valores nos limites"""
        print("\n🧪 TESTE: Valores Limite")
        
        valores_teste = [
            ("0.01", False),    # Muito baixo
            ("9.99", False),    # Abaixo do mínimo
            ("10.00", True),    # Mínimo válido
            ("10.01", True),    # Acima do mínimo
            ("9999.99", True),  # Abaixo do máximo
            ("10000.00", True), # Máximo válido
            ("10000.01", False), # Acima do máximo
            ("99999.99", False)  # Muito alto
        ]
        
        resultados = []
        for valor, esperado in valores_teste:
            try:
                self.valor_compra = valor
                resultado = self.validar_limites_valor()
                resultados.append({
                    'valor': valor,
                    'valido': resultado,
                    'esperado': esperado,
                    'correto': resultado == esperado
                })
                status = "✅" if resultado == esperado else "❌"
                print(f"{status} R$ {valor}: {resultado} (esperado: {esperado})")
            except Exception as e:
                resultados.append({
                    'valor': valor,
                    'erro': str(e),
                    'esperado': esperado
                })
                print(f"⚠️ R$ {valor}: Erro - {e}")
        
        return resultados
    
    def testar_api_cotacao_falha(self):
        """Testa falha nas APIs de cotação"""
        print("\n🧪 TESTE: Falha de API de Cotação")
        
        # Simula falha forçando URL inválida
        self.api_cotacao.base_url = "https://api_inexistente.com"
        
        try:
            valor_btc = self.calcular_valor_btc_real()
            print(f"✅ Fallback funcionou: {valor_btc:.8f} BTC")
            return True
        except Exception as e:
            print(f"❌ Fallback falhou: {e}")
            return False
    
    def testar_backend_indisponivel(self):
        """Testa backend indisponível"""
        print("\n🧪 TESTE: Backend Indisponível")
        
        # Salva URL original
        url_original = self.backend_url
        
        try:
            # Testa com URL inválida
            self.backend_url = "https://backend_inexistente.com"
            resultado = self.criar_pedido_backend()
            
            # Restaura URL original
            self.backend_url = url_original
            
            if not resultado:
                print("✅ Erro de backend tratado corretamente")
                return True
            else:
                print("❌ Erro de backend não foi detectado")
                return False
                
        except Exception as e:
            # Restaura URL original
            self.backend_url = url_original
            print(f"✅ Exceção tratada: {e}")
            return True
    
    def testar_webhook_invalido(self):
        """Testa webhook com payload inválido"""
        print("\n🧪 TESTE: Webhook Inválido")
        
        payloads_invalidos = [
            {},  # Vazio
            {"id": ""},  # ID vazio
            {"id": "123", "status": "invalid_status"},  # Status inválido
            {"invalid_field": "value"},  # Campos inválidos
            "string_ao_invés_de_objeto"  # Tipo inválido
        ]
        
        resultados = []
        for payload in payloads_invalidos:
            try:
                if isinstance(payload, str):
                    # Testa payload como string
                    response = requests.post(
                        f"{self.backend_url}/square_webhook.php",
                        data=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=5
                    )
                else:
                    response = requests.post(
                        f"{self.backend_url}/square_webhook.php",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=5
                    )
                
                resultados.append({
                    'payload': payload,
                    'status_code': response.status_code,
                    'resposta': response.text[:100]
                })
                
                print(f"📋 Payload: {str(payload)[:50]}...")
                print(f"   Status: {response.status_code}")
                
            except Exception as e:
                resultados.append({
                    'payload': payload,
                    'erro': str(e)
                })
                print(f"⚠️ Payload: {str(payload)[:50]}... - Erro: {e}")
        
        return resultados
    
    def executar_todos_cenarios_erro(self):
        """Executa todos os cenários de erro"""
        print("🧪 EXECUTANDO TESTES DE CENÁRIOS DE ERRO")
        print("="*60)
        
        # Executa cada cenário
        cenarios = [
            ("Lightning Address Inválido", self.testar_lightning_address_invalido),
            ("Valores Limite", self.testar_valores_limite),
            ("API Cotação Falha", self.testar_api_cotacao_falha),
            ("Backend Indisponível", self.testar_backend_indisponivel),
            ("Webhook Inválido", self.testar_webhook_invalido)
        ]
        
        resultados_finais = {}
        
        for nome, metodo in cenarios:
            print(f"\n{'='*60}")
            print(f"🧪 EXECUTANDO: {nome}")
            print(f"{'='*60}")
            
            try:
                resultado = metodo()
                resultados_finais[nome] = {
                    'sucesso': True,
                    'resultado': resultado
                }
                print(f"✅ {nome}: Concluído")
                
            except Exception as e:
                resultados_finais[nome] = {
                    'sucesso': False,
                    'erro': str(e)
                }
                print(f"❌ {nome}: Erro - {e}")
        
        # Relatório final
        self.gerar_relatorio_cenarios(resultados_finais)
        
        return resultados_finais
    
    def gerar_relatorio_cenarios(self, resultados):
        """Gera relatório dos cenários de erro"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE CENÁRIOS DE ERRO")
        print("="*60)
        
        total_cenarios = len(resultados)
        sucessos = sum(1 for r in resultados.values() if r['sucesso'])
        falhas = total_cenarios - sucessos
        
        print(f"📋 Total de cenários: {total_cenarios}")
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print(f"📈 Taxa de sucesso: {sucessos/total_cenarios*100:.1f}%")
        
        print("\n📋 RESUMO POR CENÁRIO:")
        for nome, resultado in resultados.items():
            status = "✅" if resultado['sucesso'] else "❌"
            print(f"{status} {nome}")
            if not resultado['sucesso']:
                print(f"   💥 Erro: {resultado['erro']}")
        
        print("="*60)

if __name__ == "__main__":
    teste_erro = TesteCenariosErro()
    teste_erro.executar_todos_cenarios_erro()
