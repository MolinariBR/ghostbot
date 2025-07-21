<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit();
}
header('Content-Type: application/json');
require_once __DIR__ . '/../depix/depix_client.php';

$input = json_decode(file_get_contents('php://input'), true) ?: [];
$id = (int)($input['id'] ?? 0);
$valor = floatval($input['valor'] ?? 0);
$destinatario = trim($input['destinatario'] ?? '');
if (!$id || $valor <= 0) {
    echo json_encode(['success' => false, 'error' => 'id e valor obrigatórios']);
    exit;
}

// Validar parceiro
$db = new SQLite3(__DIR__ . '/../data/parceiros.db');
$res = $db->querySingle("SELECT id FROM parceiros WHERE id = $id", true);
if (!$res) {
    echo json_encode(['success' => false, 'error' => 'Parceiro não encontrado']);
    exit;
}

// Gerar Pix/Depix
require_once __DIR__ . '/../depix/depix_client.php';
try {
    $res = criarPagamentoDepixSimples(intval($valor * 100), $destinatario ?: 'manual');
    if (isset($res['qrCopyPaste'], $res['qrImageUrl'], $res['id'])) {
        // Salvar transação
        $stmt = $db->prepare("INSERT INTO parceiro_transacoes (parceiro_id, valor_reais, valor_centavos, depix_id, qr_code, copia_cola, status, created_at) VALUES (:pid, :vr, :vc, :depix, :qr, :copia, 'pending', CURRENT_TIMESTAMP)");
        $stmt->bindValue(':pid', $id, SQLITE3_INTEGER);
        $stmt->bindValue(':vr', $valor, SQLITE3_FLOAT);
        $stmt->bindValue(':vc', intval($valor*100), SQLITE3_INTEGER);
        $stmt->bindValue(':depix', $res['id'], SQLITE3_TEXT);
        $stmt->bindValue(':qr', $res['qrImageUrl'], SQLITE3_TEXT);
        $stmt->bindValue(':copia', $res['qrCopyPaste'], SQLITE3_TEXT);
        $stmt->execute();
        echo json_encode([
            'success' => true,
            'qr_image_url' => $res['qrImageUrl'],
            'qr_copy_paste' => $res['qrCopyPaste'],
            'transaction_id' => $res['id']
        ]);
    } else {
        echo json_encode(['success' => false, 'error' => $res['error'] ?? 'Erro ao criar Pix']);
    }
} catch (Exception $e) {
    echo json_encode(['success' => false, 'error' => 'Erro interno: ' . $e->getMessage()]);
} 