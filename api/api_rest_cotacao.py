import json

import requests
from config.config import BASE_URL
from typing import Optional

def get_cotacao_rest(moeda: str, vs: str = "brl", valor: float = 0.0, chatid: Optional[str] = None, compras: int = 0, metodo: str = "pix") -> dict:
    params = {
        "moeda": moeda,
        "vs": vs,  # Adicionando vs=brl por padrão
        "valor": valor,
        "chatid": str(chatid) if chatid is not None else "",
        "compras": compras,
        "metodo": metodo
    }
    url = f"{BASE_URL}/api_cotacao.php"
    response = requests.get(url, params=params, timeout=10)
    print(f"[DEBUG] Status code: {response.status_code}")
    print(f"[DEBUG] Response text: {response.text}")
    try:
        response.raise_for_status()
    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
    return response.json()

def registrar_pedido_rest(moeda, rede, valor, gtxid, chatid, metodo):
    """
    Envia pedido para o backend REST e retorna o resultado.
    """
    url = f"{BASE_URL}/api_cotacao.php"
    
    # Garantir que o valor seja um número válido
    try:
        valor_float = float(valor)
        if valor_float <= 0:
            print(f"[ERRO] Valor inválido: {valor}")
            return {"success": False, "error": "Valor deve ser maior que zero"}
    except (ValueError, TypeError) as e:
        print(f"[ERRO] Erro ao converter valor {valor}: {e}")
        return {"success": False, "error": f"Valor inválido: {valor}"}
    
    params = {
        "moeda": moeda,
        "rede": rede,
        "valor": f"{valor_float:.2f}",  # Formata com 2 casas decimais
        "valor_brl": f"{valor_float:.2f}",  # Formata com 2 casas decimais
        "gtxid": gtxid,
        "chatid": str(chatid),
        "metodo": metodo,
        "action": "registrar",
        "vs": "brl",
        "compras": "1"
    }
    
    print(f"[DEBUG] Enviando requisição para: {url}")
    print(f"[DEBUG] Parâmetros: {params}")
    
    try:
        # Envia como parâmetros de consulta (query string) em vez de JSON no corpo
        response = requests.post(url, params=params, timeout=10)
        print(f"[DEBUG] Status code: {response.status_code}")
        print(f"[DEBUG] Headers: {response.headers}")
        print(f"[DEBUG] Conteúdo da resposta: {response.text}")
        
        if not response.text.strip():
            print("[ERRO] Resposta vazia do servidor")
            return {"success": False, "error": "Resposta vazia do servidor"}
            
        result = response.json()
        print(f"[DEBUG] Resposta decodificada: {result}")
        return result
    except json.JSONDecodeError as je:
        print(f"[ERRO] Falha ao decodificar JSON: {je}")
        return {"success": False, "error": f"Erro ao processar resposta do servidor: {str(je)}"}
    except requests.exceptions.RequestException as re:
        print(f"[ERRO] Erro na requisição: {re}")
        return {"success": False, "error": f"Erro de conexão: {str(re)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Exemplo de uso
if __name__ == "__main__":
    print(get_cotacao_rest("bitcoin", valor=1000, chatid="12345", compras=2, metodo="pix"))
    print(get_cotacao_rest("usdt", valor=500, chatid="12345", compras=0, metodo="pix"))
    print(get_cotacao_rest("depix", valor=50, chatid="12345", compras=1, metodo="pix"))
