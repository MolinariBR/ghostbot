CREATE TABLE IF NOT EXISTS deposit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    depix_id TEXT UNIQUE NOT NULL,
    chatid TEXT NOT NULL,
    amount_in_cents INTEGER NOT NULL,
    send REAL NOT NULL,
    rede TEXT NOT NULL,
    status TEXT DEFAULT "pending",
    created_at TEXT NOT NULL,
    blockchainTxID TEXT,
    taxa REAL,
    moeda TEXT,
    address TEXT,
    forma_pagamento TEXT,
    notified INTEGER DEFAULT 0,
    metodo_pagamento TEXT,
    comprovante TEXT,
    user_id TEXT,
    cpf TEXT
);
CREATE INDEX IF NOT EXISTS idx_deposit_chatid ON deposit(chatid);
CREATE INDEX IF NOT EXISTS idx_deposit_status ON deposit(status);
CREATE INDEX IF NOT EXISTS idx_deposit_data ON deposit(created_at);
