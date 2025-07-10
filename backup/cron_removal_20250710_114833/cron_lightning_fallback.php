#!/usr/bin/env php
<?php
/**
 * Cron job para processar fila de fallback Lightning
 * Executa a cada 5 minutos para tentar reprocessar pagamentos falhados
 */

require_once __DIR__ . '/voltz/voltz_fallback.php';

// Configurar logging
$log_file = __DIR__ . '/logs/lightning_fallback.log';
if (!file_exists(dirname($log_file))) {
    mkdir(dirname($log_file), 0755, true);
}

function logMessage($message) {
    global $log_file;
    $timestamp = date('Y-m-d H:i:s');
    file_put_contents($log_file, "[$timestamp] $message\n", FILE_APPEND | LOCK_EX);
    echo "[$timestamp] $message\n";
}

logMessage("=== Iniciando processamento da fila Lightning ===");

try {
    $fallback_system = new VoltzFallbackSystem();
    
    // Processar até 10 items por execução
    $result = $fallback_system->processFallbackQueue(10);
    
    logMessage("Processamento concluído:");
    logMessage("- Items verificados: {$result['total_checked']}");
    logMessage("- Items processados com sucesso: {$result['processed']}");
    
    if ($result['total_checked'] > 0) {
        foreach ($result['results'] as $item) {
            $status = $item['result']['success'] ? 'SUCCESS' : 'FAILED';
            $depix_id = $item['depix_id'];
            $error = $item['result']['error'] ?? '';
            
            logMessage("  - $depix_id: $status $error");
            
            // Se processou com sucesso, notificar via bot (implementar depois)
            if ($item['result']['success']) {
                // TODO: Implementar notificação de sucesso via Telegram
                logMessage("    Payment hash: {$item['result']['payment_hash']}");
            }
        }
    } else {
        logMessage("Nenhum item na fila de processamento");
    }
    
} catch (Exception $e) {
    logMessage("ERRO: " . $e->getMessage());
    logMessage("Trace: " . $e->getTraceAsString());
    exit(1);
}

logMessage("=== Processamento da fila Lightning concluído ===");
?>
