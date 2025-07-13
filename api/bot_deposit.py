import requests
import json
from config.config import BASE_URL

def criar_deposito_pix(gtxid: str, chatid: str, valor: float, moeda: str = "BRL") -> dict:
    """
    Cria um depósito PIX no sistema
    
    Args:
        gtxid (str): ID único da transação
        chatid (str): ID do chat do Telegram
        valor (float): Valor do depósito
        moeda (str, optional): Moeda do depósito. Padrão: "BRL"
        
    Returns:
        dict: Resposta da API com os dados do PIX ou erro
    """
    # Remove a duplicação do /api/ já que BASE_URL já inclui
    url = f"{BASE_URL}/bot_deposit.php"
    
    # Converte o valor para float e formata como string sem casas decimais
    # pois o servidor espera um valor inteiro (em centavos)
    valor_em_centavos = int(float(valor) * 100)
    
    # Cria o payload para o corpo da requisição
    payload = {
        "action": "create_pix",
        "gtxid": str(gtxid),  # Garante que é string
        "chatid": str(chatid),  # Garante que é string
        "amount_in_cents": int(valor_em_centavos),  # Valor em centavos como inteiro
        "moeda": str(moeda).upper(),  # Garante maiúsculas
        "metodo": "pix"
    }
    
    try:
        # Log dos dados que estão sendo enviados
        print(f"[DEBUG] Enviando requisição para: {url}")
        print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
        
        # Faz a requisição com timeout de 30 segundos
        # Envia o payload como JSON no corpo da requisição
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Log da resposta bruta
        print(f"[DEBUG] Status Code: {response.status_code}")
        print(f"[DEBUG] Headers: {response.headers}")
        print(f"[DEBUG] Response Text: {response.text}")
        
        # Tenta fazer o parse do JSON
        try:
            json_response = response.json()
            print(f"[DEBUG] JSON Response: {json.dumps(json_response, indent=2)}")
            return json_response
        except json.JSONDecodeError:
            print("[DEBUG] A resposta não é um JSON válido")
            return {
                "success": False,
                "error": f"Resposta inválida do servidor: {response.text}"
            }
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Erro na requisição: {str(e)}")
        return {
            "success": False,
            "error": f"Erro na comunicação com o servidor: {str(e)}"
        }