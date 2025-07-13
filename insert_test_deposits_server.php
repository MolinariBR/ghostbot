<?php
/**
 * Script para inserir depix_ids de teste no servidor de produção
 * 
 * Este script deve ser executado diretamente no servidor de produção
 * para inserir os depix_ids fornecidos pelo usuário com diferentes status
 * para testar o validador de PIX no bot.
 * 
 * Como usar:
 * 1. Faça upload deste arquivo para o servidor de produção
 * 2. Execute: php insert_test_deposits_server.php
 * 3. Delete o arquivo após a execução por segurança
 */

// Configuração do banco de dados (ajuste o caminho conforme necessário)
$db_path = __DIR__ . '/data/deposit.db';

if (!file_exists($db_path)) {
    echo "❌ Banco de dados não encontrado: $db_path\n";
    echo "🔍 Verificando caminhos alternativos...\n";
    
    // Tenta caminhos alternativos
    $alternative_paths = [
        __DIR__ . '/ghostbackend/data/deposit.db',
        __DIR__ . '/../data/deposit.db',
        '/var/www/html/data/deposit.db',
        '/home/runner/app/data/deposit.db'
    ];
    
    foreach ($alternative_paths as $path) {
        if (file_exists($path)) {
            $db_path = $path;
            echo "✅ Banco encontrado em: $db_path\n";
            break;
        }
    }
    
    if (!file_exists($db_path)) {
        echo "❌ Banco de dados não encontrado em nenhum caminho conhecido.\n";
        echo "📋 Caminhos verificados:\n";
        foreach ($alternative_paths as $path) {
            echo "   - $path\n";
        }
        exit(1);
    }
}

try {
    $pdo = new PDO('sqlite:' . $db_path);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    echo "✅ Conectado ao banco de dados: $db_path\n";
    
    // Depix IDs fornecidos pelo usuário
    $test_deposits = [
        [
            'depix_id' => '5ee0b16967f9e0f7d6eead010f1af9acf7be09a7203abe515958a84d5848e761',
            'status' => 'pending',
            'blockchainTxID' => null,
            'description' => 'Pendente - sem blockchainTxID'
        ],
        [
            'depix_id' => '965cd29f947c0a548c8199bbacb42a294aec3cd8f8f6cd935c45f52b6a8ddb2b',
            'status' => 'paid',
            'blockchainTxID' => 'txid_confirmado_123456789',
            'description' => 'Pago - com blockchainTxID'
        ],
        [
            'depix_id' => 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
            'status' => 'waiting_address',
            'blockchainTxID' => 'txid_aguardando_endereco_987654321',
            'description' => 'Aguardando endereço Lightning'
        ],
        [
            'depix_id' => 'f1e2d3c4b5a6789012345678901234567890fedcba1234567890fedcba123456',
            'status' => 'completed',
            'blockchainTxID' => 'txid_completo_456789123',
            'description' => 'Completo - pagamento finalizado'
        ]
    ];
    
    echo "\n📋 Inserindo depósitos de teste...\n";
    echo str_repeat("-", 60) . "\n";
    
    $inserted_count = 0;
    $skipped_count = 0;
    
    foreach ($test_deposits as $deposit) {
        // Verifica se já existe
        $stmt = $pdo->prepare('SELECT id FROM deposit WHERE depix_id = ?');
        $stmt->execute([$deposit['depix_id']]);
        
        if ($stmt->fetch()) {
            echo "⏭️  Pulado: {$deposit['depix_id']} (já existe)\n";
            $skipped_count++;
            continue;
        }
        
        // Insere o depósito
        $stmt = $pdo->prepare('INSERT INTO deposit (
            chatid, moeda, rede, amount_in_cents, taxa, address, forma_pagamento, 
            send, blockchainTxID, depix_id, status, created_at, user_id, comprovante
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)');
        
        $result = $stmt->execute([
            '123456789',           // chatid
            'BRL',                 // moeda
            'PIX',                 // rede
            10000,                 // amount_in_cents (R$ 100,00)
            500,                   // taxa (R$ 5,00)
            'test@example.com',    // address
            'PIX',                 // forma_pagamento
            9500,                  // send (amount - taxa)
            $deposit['blockchainTxID'], // blockchainTxID
            $deposit['depix_id'],  // depix_id
            $deposit['status'],    // status
            date('Y-m-d H:i:s'),   // created_at
            'test_user',           // user_id
            'Teste Validador PIX'  // comprovante
        ]);
        
        if ($result) {
            $id = $pdo->lastInsertId();
            echo "✅ Inserido ID {$id}: {$deposit['depix_id']}\n";
            echo "   Status: {$deposit['status']}\n";
            echo "   Blockchain TxID: " . ($deposit['blockchainTxID'] ?: 'null') . "\n";
            echo "   Descrição: {$deposit['description']}\n";
            $inserted_count++;
        } else {
            echo "❌ Erro ao inserir: {$deposit['depix_id']}\n";
        }
        
        echo "\n";
    }
    
    echo str_repeat("=", 60) . "\n";
    echo "📊 Resumo:\n";
    echo "   ✅ Inseridos: $inserted_count\n";
    echo "   ⏭️  Pulados: $skipped_count\n";
    echo "   📋 Total processados: " . count($test_deposits) . "\n";
    
    // Lista os depósitos inseridos
    echo "\n📋 Depósitos de teste no banco:\n";
    echo str_repeat("-", 60) . "\n";
    
    $stmt = $pdo->prepare('SELECT id, depix_id, status, blockchainTxID, created_at FROM deposit WHERE depix_id IN (?, ?, ?, ?) ORDER BY id');
    $stmt->execute([
        '5ee0b16967f9e0f7d6eead010f1af9acf7be09a7203abe515958a84d5848e761',
        '965cd29f947c0a548c8199bbacb42a294aec3cd8f8f6cd935c45f52b6a8ddb2b',
        'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
        'f1e2d3c4b5a6789012345678901234567890fedcba1234567890fedcba123456'
    ]);
    
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        echo "ID: {$row['id']} | Depix ID: {$row['depix_id']} | Status: {$row['status']} | TxID: " . ($row['blockchainTxID'] ?: 'null') . "\n";
    }
    
    echo "\n✅ Script concluído com sucesso!\n";
    echo "🧪 Agora você pode testar o validador com os depix_ids inseridos.\n";
    echo "🔒 IMPORTANTE: Delete este arquivo após a execução por segurança!\n";
    
} catch (Exception $e) {
    echo "❌ Erro: " . $e->getMessage() . "\n";
    exit(1);
}
?> 