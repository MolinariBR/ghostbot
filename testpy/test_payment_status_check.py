import requests

def test_payment_status_check():
    # Exemplo de depix_id válido para teste
    depix_id = "test123456789"
    url = f"https://useghost.squareweb.app/payment_status/check.php?depix_id={depix_id}"
    response = requests.get(url, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 200, "Status HTTP diferente de 200"
    data = response.json()
    assert 'success' in data, "Campo 'success' ausente na resposta"
    assert 'status' in data or 'message' in data, "Campo 'status' ou 'message' ausente na resposta"
    print("Teste concluído com sucesso!")

if __name__ == "__main__":
    test_payment_status_check()
