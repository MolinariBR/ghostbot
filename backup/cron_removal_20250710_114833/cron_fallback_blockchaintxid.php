<?php
// cron_fallback_blockchaintxid.php
// Script para rodar periodicamente (via cron) e tentar atualizar blockchainTxID de depósitos pendentes

require_once __DIR__ . '/configuracoes.php';

// Configurações
$DEPIX_API_URL = 'https://depix.eulen.app/api/deposit-status';
$DEPIX_API_TOKEN = getenv('DEPIX_API_TOKEN') ?: 'SEU_TOKEN_DEPX_AQUI';
$FALLBACK_API_URL = 'https://useghost.squareweb.app/api/fallback_blockchaintxid.php';
$FALLBACK_API_KEY = getenv('API_FALLBACK_KEY') ?: 'SUA_CHAVE_FORTE_AQUI';

// Conexão com o banco
try {
    $pdo = new PDO('sqlite:' . __DIR__ . '/database/deposit.db');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (Exception $e) {
    echo "[ERRO] Falha ao conectar no banco: ".$e->getMessage()."\n";
    exit(1);
}

// Busca depósitos com depix_id e blockchainTxID vazio
$stmt = $pdo->query("SELECT depix_id FROM deposit WHERE depix_id IS NOT NULL AND (blockchainTxID IS NULL OR blockchainTxID = '')");
$pendentes = $stmt->fetchAll(PDO::FETCH_COLUMN);

foreach ($pendentes as $depix_id) {
    // Consulta DePix
    $ch = curl_init($DEPIX_API_URL.'?id='.urlencode($depix_id));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $DEPIX_API_TOKEN
    ]);
    $resp = curl_exec($ch);
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($httpcode !== 200 || !$resp) {
        echo "[WARN] Falha ao consultar DePix para $depix_id\n";
        continue;
    }
    $data = json_decode($resp, true);
    $txid = $data['response']['blockchainTxID'] ?? null;
    if (!$txid) {
        echo "[INFO] Sem blockchainTxID para $depix_id\n";
        continue;
    }
    // Chama o endpoint de fallback
    $payload = json_encode(['depix_id' => $depix_id, 'blockchainTxID' => $txid]);
    $ch = curl_init($FALLBACK_API_URL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'X-API-KEY: ' . $FALLBACK_API_KEY
    ]);
    $resp = curl_exec($ch);
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    echo date('c') . " depix_id=$depix_id txid=$txid HTTP=$httpcode resp=$resp\n";
}
