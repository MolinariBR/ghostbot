-- Script para criar a tabela pedidos_bot no servidor
CREATE TABLE IF NOT EXISTS pedidos_bot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gtxid TEXT NOT NULL,
    chatid TEXT NOT NULL,
    moeda TEXT NOT NULL,
    rede TEXT NOT NULL,
    valor REAL NOT NULL,
    comissao REAL NOT NULL,
    parceiro REAL NOT NULL,
    cotacao REAL NOT NULL,
    recebe REAL NOT NULL,
    forma_pagamento TEXT NOT NULL,
    depix_id TEXT,
    status TEXT DEFAULT 'novo',
    pagamento_verificado INTEGER DEFAULT 0,
    tentativas_verificacao INTEGER DEFAULT 0,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    blockchainTxID TEXT
); 