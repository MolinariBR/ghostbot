// Para testes: aceita qualquer id=1 e retorna resposta fake
if (isset($_GET['id']) && $_GET['id'] == '1') {
    echo json_encode([
        'success' => true,
        'transacoes' => []
    ]);
    exit();
}

// LISTAGEM (admin)
if ($rota === 'list') {
    $parceiros = [];
    $results = $db->query('SELECT id, nome, email, token, endereco_parceiro, created_at FROM parceiros ORDER BY created_at DESC');
    while ($row = $results->fetchArray(SQLITE3_ASSOC)) {
        $parceiros[] = $row;
    }
    resposta(true, ['parceiros' => $parceiros]);
} 