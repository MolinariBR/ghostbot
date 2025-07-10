<?php
/**
 * Cron Job: Atualização de blockchainTxID
 * 
 * Função: Busca depósitos que têm depix_id mas não têm blockchainTxID,
 * consulta a API da Eulen Depix e atualiza o banco com o hash da transação.
 * 
 * Execução: Deve ser executado periodicamente via cron (ex: a cada 5 minutos)
 * Banco: SQLite - data/deposit.db
 * 
 * @author Sistema Ghost Bot
 * @version 2.0
 * @date 2025-07-06
 */

// Inclui o cliente da API Depix
require_once __DIR__ . '/../depix/depix_client.php';



// === CONFIGURAÇÃO DO BANCO DE DADOS ===
$dbPath = __DIR__ . '/../data/deposit.db';
try {
    $db = new SQLite3($dbPath);
    $db->busyTimeout(5000); // 5 segundos de timeout para evitar locks
} catch (Exception $e) {
    echo "ERRO: Falha ao conectar ao banco SQLite: " . $e->getMessage() . "\n";
    exit(1);
}

// === BUSCA DEPÓSITOS PENDENTES ===
// Critérios:
// 1. depix_id preenchido (integração com Depix feita)
// 2. blockchainTxID vazio (ainda não obtido da API)
$sql = "SELECT id, depix_id FROM deposit 
        WHERE depix_id IS NOT NULL 
        AND depix_id != '' 
        AND (blockchainTxID IS NULL OR blockchainTxID = '')";

$res = $db->query($sql);
if (!$res) {
    echo "ERRO: Falha na consulta ao banco: " . $db->lastErrorMsg() . "\n";
    $db->close();
    exit(1);
}

echo "INFO: Iniciando busca de blockchainTxID - " . date('c') . "\n";

// === PROCESSAMENTO DOS DEPÓSITOS ===
$countTotal = 0;
$countUpdated = 0;
$countErrors = 0;

while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
    $depix_id = $row['depix_id'];
    $id = $row['id'];
    $countTotal++;
    
    try {
        // Consulta a API da Depix para obter o status do depósito
        $apiRes = depixApiRequest('deposit-status?id=' . urlencode($depix_id), 'GET');
        $txid = $apiRes['body']['response']['blockchainTxID'] ?? '';
        
        if ($txid) {
            // blockchainTxID encontrado - atualiza no banco
            $stmt = $db->prepare("UPDATE deposit SET blockchainTxID = :txid WHERE id = :id");
            $stmt->bindValue(':txid', $txid, SQLITE3_TEXT);
            $stmt->bindValue(':id', $id, SQLITE3_TEXT);
            $stmt->execute();
            
            $countUpdated++;
            echo "SUCCESS: Atualizado id=$id depix_id=$depix_id blockchainTxID=$txid - " . date('c') . "\n";
        } else {
            // blockchainTxID ainda não disponível na API
            echo "WAITING: Sem blockchainTxID para id=$id depix_id=$depix_id - " . date('c') . "\n";
        }
        
    } catch (Exception $e) {
        // Erro na consulta da API
        $countErrors++;
        echo "ERROR: Falha ao consultar depix_id=$depix_id: " . $e->getMessage() . " - " . date('c') . "\n";
    }
    
    // Delay para não sobrecarregar a API (300ms = 0.3 segundos)
    usleep(300000);
}

// === FINALIZAÇÃO E RELATÓRIO ===
echo "INFO: Processamento finalizado - " . date('c') . "\n";
echo "STATS: Total=$countTotal | Atualizados=$countUpdated | Erros=$countErrors\n";

// Fecha conexão com o banco
$db->close();

// Log para arquivo (opcional - descomente se necessário)
// file_put_contents(__DIR__ . '/../logs/cron_blockchaintxid.log', 
//     date('c') . " - Total: $countTotal, Atualizados: $countUpdated, Erros: $countErrors\n", 
//     FILE_APPEND
// );