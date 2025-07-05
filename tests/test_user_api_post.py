import requests
import json

def test_user_api_post():
    """
    Testa o endpoint user_api.php enviando dados simulados de usuário.
    """
    url = "https://useghost.squareweb.app/api/user_api.php"
    payload = {
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
    assert response.status_code == 200, f"Status code inesperado: {response.status_code}"
    data = response.json()
    assert data.get("status") == "ok", f"Resposta inesperada: {data}"
    print("Teste de POST para user_api.php executado com sucesso.")

if __name__ == "__main__":
    test_user_api_post()
