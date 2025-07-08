
from api.voltz import VoltzAPI
voltz = VoltzAPI(backend_url='http://localhost:8000')
print('1. Criando depósito...')
result = voltz.create_deposit_request('test_bot', 'user123', 3000, 0.05, 'BTC', 50000)
print('Resultado:', result)
print('2. Verificando status...')
status = voltz.check_deposit_status(result['depix_id'])
print('Status:', status)

