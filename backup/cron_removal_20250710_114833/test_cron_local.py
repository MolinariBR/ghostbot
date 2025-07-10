#!/usr/bin/env python3
"""
Teste local do cron Lightning executando PHP diretamente
"""

import subprocess
import os
import json

def testar_cron_local():
    """Executa o cron Lightning localmente via PHP CLI"""
    print("🧪 Teste Local do Cron Lightning")
    print("="*40)
    
    # Criar script PHP de teste
    script_teste = """<?php
// Simular ambiente de execução do cron
$_SERVER['REQUEST_METHOD'] = 'GET';
$_GET['chat_id'] = '7910260237';

// Capturar output
ob_start();

try {
    // Incluir o cron
    require_once '/home/mau/bot/ghostbackend/api/lightning_cron_endpoint_final.php';
    
    // Criar instância e executar
    $processor = new LightningCronProcessor();
    $result = $processor->executeCron('7910260237');
    
    // Limpar buffer anterior
    ob_clean();
    
    // Retornar resultado JSON
    header('Content-Type: application/json');
    echo json_encode($result, JSON_PRETTY_PRINT);
    
} catch (Exception $e) {
    // Limpar buffer
    ob_clean();
    
    // Retornar erro
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage(),
        'trace' => $e->getTraceAsString()
    ], JSON_PRETTY_PRINT);
} catch (Error $e) {
    // Limpar buffer  
    ob_clean();
    
    // Retornar erro fatal
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Fatal Error: ' . $e->getMessage(),
        'trace' => $e->getTraceAsString()
    ], JSON_PRETTY_PRINT);
}

// Finalizar output
ob_end_flush();
?>"""
    
    # Salvar script temporário
    script_path = '/tmp/test_cron_local.php'
    with open(script_path, 'w') as f:
        f.write(script_teste)
    
    print(f"📄 Script criado: {script_path}")
    
    try:
        # Executar via PHP CLI
        print("🔄 Executando via PHP CLI...")
        result = subprocess.run(['php', script_path], 
                              capture_output=True, text=True, timeout=30)
        
        print(f"📊 Return Code: {result.returncode}")
        
        if result.stdout:
            print("📤 STDOUT:")
            try:
                # Tentar parsear como JSON
                data = json.loads(result.stdout)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(result.stdout)
        
        if result.stderr:
            print("📤 STDERR:")
            print(result.stderr)
        
        # Limpar arquivo temporário
        os.unlink(script_path)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - O script demorou mais de 30 segundos")
        os.unlink(script_path)
        return False
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        if os.path.exists(script_path):
            os.unlink(script_path)
        return False

def main():
    sucesso = testar_cron_local()
    
    print("\n" + "="*40)
    if sucesso:
        print("✅ Teste local concluído com sucesso!")
    else:
        print("❌ Teste local falhou!")
    
    return 0 if sucesso else 1

if __name__ == "__main__":
    exit(main())
