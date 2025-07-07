#!/usr/bin/env python3

import requests
import time
import json

def diagnosticar_servidor():
    print("🔍 DIAGNÓSTICO DO SERVIDOR")
    print("=" * 40)
    
    endpoints = [
        ("Página principal", "GET", "https://useghost.squareweb.app/", None),
        ("REST Deposits", "GET", "https://useghost.squareweb.app/rest/deposit.php?chatid=123", None),
        ("Voltz Status", "GET", "https://useghost.squareweb.app/voltz/voltz_status.php", None),
        ("Voltz REST", "GET", "https://useghost.squareweb.app/voltz/voltz_rest.php", None),
        ("Lightning Trigger", "POST", "https://useghost.squareweb.app/api/lightning_trigger.php", {"depix_id": "teste"}),
        ("Webhook Depix", "POST", "https://useghost.squareweb.app/depix/webhook.php", {"id": "teste", "blockchainTxID": "abc123"})
    ]
    
    resultados = []
    
    for nome, metodo, url, payload in endpoints:
        print(f"\n🔗 Testando: {nome}")
        print(f"   URL: {url}")
        
        try:
            headers = {"Content-Type": "application/json"}
            if "webhook" in url:
                headers["Authorization"] = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJSUzI1NiIsImVudiI6InByb2QiLCJleHAiOjE3ODI3NjUzNzcsImlhdCI6MTc1MTY2MTM3NywianRpIjoiNTY4OTlhZTdjMGJlIiwic2NvcGUiOlsiZGVwb3NpdCIsIndpdGhkcmF3Il0sInN1YiI6Imdob3N0IiwidHlwIjoiSldUIn0.fcobx8C6rPyYAYKo1WBhwyvErWHlX_ZOaZM3QvrOtBS5EGip8ofxX2h7lnJjZozNvu_6qI7SK3EsS8sPGYAkBWHvON3huWzXN--NkZV9HK4G5VMIYESdDqTvS7xnBcEJFlKjpq6wbN1siYu8Zp6b7RTfeRBlG4lNYiFVe3DWBJW2lcfTAOhMnpFQ4DPClxek-htU-pDtZcBwwgMfpBVGBIeiGVRV4YAvKFUeKItNijbBIwZtP3qsxslR-W8aaJUQ35OkPkBfrrw6OKz94Ng4xVs9uOZJ64ZBwVNzjKX_r6OIXtjVRbaErU-R4scdMlKYz-yj7bu0NhtmJTccruYyN5ITWtcTwxL9avhEp_ej8Ve3rWaf3ezsKejEol2iVakrHU9JDgLzmWxo7PXxTeipw5GlkXXo5IgtxxI-ViIHzPO3L816ZxdGhMlLS6fHEcZC1slWALUQgFxrS2VOLAfV105K63g4_X7_JKbEH0w7tOpaqd0Fl3VvodtKzH33JPNSfj9AD7hhJwhX6tDQvOtSpoRu10uRwPcVv_wfuqsgyaT6kfBJ5WKUdpyWFvSWWKjI5S907cjj8uXbazycBMQtZaL_aIRuqCEY3x_d8J_UlfS-vPwjC99RsXxMztXIzyQNdper7wIhVA604JiP5kvGN3ipzwIGNYT3jakbDviYNE0"
            
            inicio = time.time()
            
            if metodo == "GET":
                response = requests.get(url, headers=headers, timeout=8)
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=8)
            
            tempo = time.time() - inicio
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   ⏱️ Tempo: {tempo:.2f}s")
            print(f"   📝 Resposta: {response.text[:100]}...")
            
            resultados.append({
                'nome': nome,
                'status': 'OK',
                'codigo': response.status_code,
                'tempo': tempo,
                'erro': None
            })
            
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT (>8s)")
            resultados.append({
                'nome': nome,
                'status': 'TIMEOUT',
                'codigo': None,
                'tempo': 8.0,
                'erro': 'Timeout'
            })
            
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ ERRO DE CONEXÃO: {e}")
            resultados.append({
                'nome': nome,
                'status': 'ERRO_CONEXAO',
                'codigo': None,
                'tempo': None,
                'erro': str(e)
            })
            
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            resultados.append({
                'nome': nome,
                'status': 'ERRO',
                'codigo': None,
                'tempo': None,
                'erro': str(e)
            })
    
    # Resumo
    print(f"\n📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 40)
    
    ok_count = len([r for r in resultados if r['status'] == 'OK'])
    timeout_count = len([r for r in resultados if r['status'] == 'TIMEOUT'])
    erro_count = len([r for r in resultados if r['status'] in ['ERRO', 'ERRO_CONEXAO']])
    
    print(f"✅ Funcionando: {ok_count}")
    print(f"⏰ Timeout: {timeout_count}")
    print(f"❌ Erro: {erro_count}")
    
    if timeout_count > 0:
        print(f"\n⚠️ PROBLEMAS IDENTIFICADOS:")
        for r in resultados:
            if r['status'] == 'TIMEOUT':
                print(f"   • {r['nome']}: Timeout (>8s)")
        
        print(f"\n💡 POSSÍVEIS CAUSAS:")
        print(f"   • Voltz Lightning Node está offline")
        print(f"   • Scripts PHP estão em loop infinito")
        print(f"   • Sobrecarga no servidor")
        print(f"   • Timeout de conexão com APIs externas")
        
        print(f"\n🔧 SOLUÇÕES SUGERIDAS:")
        print(f"   • Verificar logs do servidor")
        print(f"   • Reiniciar serviços Lightning")
        print(f"   • Aumentar timeout nos scripts")
        print(f"   • Testar com dados menores")

if __name__ == "__main__":
    diagnosticar_servidor()
