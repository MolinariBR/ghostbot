-- Tabela para controle de limites por usuário
CREATE TABLE IF NOT EXISTS chatid_limites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chatid TEXT UNIQUE NOT NULL,
    num_compras INTEGER DEFAULT 0,
    limite_atual REAL DEFAULT 500.00,
    tem_cpf BOOLEAN DEFAULT FALSE,
    cpf TEXT DEFAULT NULL,
    primeiro_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_comprado REAL DEFAULT 0.00,
    compras_hoje INTEGER DEFAULT 0,
    ultimo_reset_diario DATE DEFAULT CURRENT_DATE
);

-- Índices para otimização
CREATE INDEX IF NOT EXISTS idx_chatid ON chatid_limites(chatid);
CREATE INDEX IF NOT EXISTS idx_ultimo_reset ON chatid_limites(ultimo_reset_diario);
