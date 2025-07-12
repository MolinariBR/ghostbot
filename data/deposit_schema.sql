CREATE TABLE IF NOT EXISTS deposit (
    depix_id TEXT PRIMARY KEY,
    chatid TEXT NOT NULL,
    amount_in_cents INTEGER NOT NULL,
    send REAL NOT NULL,
    rede TEXT NOT NULL,
    status TEXT DEFAULT "pending",
    created_at TEXT NOT NULL,
    blockchainTxID TEXT
);
CREATE INDEX IF NOT EXISTS idx_deposit_chatid ON deposit(chatid);
CREATE INDEX IF NOT EXISTS idx_deposit_status ON deposit(status);
CREATE INDEX IF NOT EXISTS idx_deposit_data ON deposit(created_at);
