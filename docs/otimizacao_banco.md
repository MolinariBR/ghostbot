# Otimização de Consultas ao Banco de Dados

## Análise Atual

O sistema utiliza SQLite com consultas frequentes nas tabelas `deposit` e `cotacoes`. Principais pontos de otimização identificados:

## 1. Índices Recomendados

### Tabela `deposit`
```sql
-- Índice para consultas por depix_id (usado frequentemente)
CREATE INDEX IF NOT EXISTS idx_deposit_depix_id ON deposit(depix_id);

-- Índice para consultas por blockchainTxID
CREATE INDEX IF NOT EXISTS idx_deposit_blockchain_txid ON deposit(blockchainTxID);

-- Índice para consultas por status
CREATE INDEX IF NOT EXISTS idx_deposit_status ON deposit(status);

-- Índice composto para monitoramento (cron_job_update.php)
CREATE INDEX IF NOT EXISTS idx_deposit_pending ON deposit(depix_id, blockchainTxID) 
WHERE depix_id IS NOT NULL AND blockchainTxID IS NULL;

-- Índice composto para confirmações (monitor_deposit.php)
CREATE INDEX IF NOT EXISTS idx_deposit_monitoring ON deposit(blockchainTxID, status) 
WHERE blockchainTxID IS NOT NULL AND status != 'confirmado';

-- Índice para created_at (usado no voltz_status.php)
CREATE INDEX IF NOT EXISTS idx_deposit_created_at ON deposit(created_at);
```

### Tabela `cotacoes`
```sql
-- Índice composto para verificação de cotações recentes
CREATE INDEX IF NOT EXISTS idx_cotacoes_recentes ON cotacoes(moeda_origem, moeda_destino, origem, data_atualizacao);
```

## 2. Otimização de Consultas

### A. Consultas com LIMIT e ORDER BY
**Problema atual**: Consultas sem índices adequados para ordenação.

**Antes:**
```php
$stmt = $pdo->prepare('SELECT * FROM deposit WHERE depix_id = ? ORDER BY created_at DESC LIMIT 1');
```

**Depois:** (já otimizada com índice)
```php
$stmt = $pdo->prepare('SELECT * FROM deposit WHERE depix_id = ? ORDER BY created_at DESC LIMIT 1');
```

### B. Consultas com IS NULL/IS NOT NULL
**Problema atual**: SQLite não otimiza bem condições NULL sem índices específicos.

**Solução**: Usar índices parciais (ver índices acima).

### C. Consultas de contagem
**Antes:**
```php
$query = $db->prepare('SELECT COUNT(*) as total FROM cotacoes WHERE moeda_origem = ? AND moeda_destino = ? AND data_atualizacao >= datetime("now", "-1 minute") AND origem = ?');
```

**Depois:** (com índice composto já é otimizada)

## 3. Cache e Polling Inteligente

### A. Cache de Cotações
```php
// Implementar cache em memória para cotações
class CotacaoCache {
    private static $cache = [];
    private static $ttl = 60; // 1 minuto
    
    public static function get($moeda_origem, $moeda_destino, $origem) {
        $key = "{$moeda_origem}_{$moeda_destino}_{$origem}";
        
        if (isset(self::$cache[$key]) && 
            time() - self::$cache[$key]['timestamp'] < self::$ttl) {
            return self::$cache[$key]['value'];
        }
        
        return null;
    }
    
    public static function set($moeda_origem, $moeda_destino, $origem, $value) {
        $key = "{$moeda_origem}_{$moeda_destino}_{$origem}";
        self::$cache[$key] = [
            'value' => $value,
            'timestamp' => time()
        ];
    }
}
```

### B. Polling Otimizado
**Problema atual**: Cron jobs fazem polling constante.

**Solução**: Implementar backoff exponencial e intervalos inteligentes.

```php
// Script de monitoramento otimizado
class MonitoramentoOtimizado {
    private $intervalos = [
        'novo' => 30,      // 30 segundos para transações novas
        'pendente' => 60,  // 1 minuto para pendentes
        'antigo' => 300    // 5 minutos para antigas
    ];
    
    public function getIntervalo($created_at) {
        $idade = time() - strtotime($created_at);
        
        if ($idade < 300) return $this->intervalos['novo'];
        if ($idade < 1800) return $this->intervalos['pendente'];
        return $this->intervalos['antigo'];
    }
}
```

## 4. Otimização de Conexões

### A. Pool de Conexões
```php
class DatabasePool {
    private static $connections = [];
    private static $maxConnections = 5;
    
    public static function getConnection() {
        if (count(self::$connections) < self::$maxConnections) {
            $db = new SQLite3('/path/to/database.db');
            $db->busyTimeout(30000); // 30 segundos timeout
            self::$connections[] = $db;
            return $db;
        }
        
        // Retorna conexão existente
        return self::$connections[array_rand(self::$connections)];
    }
}
```

### B. Configurações SQLite Otimizadas
```sql
-- Configurações de performance
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = memory;
PRAGMA mmap_size = 268435456; -- 256MB
```

## 5. Monitoramento e Logs

### A. Log de Performance
```php
class QueryProfiler {
    public static function profile($query, $params, $callback) {
        $start = microtime(true);
        $result = $callback();
        $end = microtime(true);
        
        $duration = ($end - $start) * 1000; // ms
        
        if ($duration > 100) { // Log queries > 100ms
            error_log("SLOW QUERY ({$duration}ms): {$query} - Params: " . json_encode($params));
        }
        
        return $result;
    }
}
```

### B. Métricas de Sistema
```php
// Adicionar ao cron para monitorar performance
function logSystemMetrics() {
    $stats = [
        'db_size' => filesize('/path/to/database.db'),
        'memory_usage' => memory_get_usage(true),
        'load_average' => sys_getloadavg(),
        'timestamp' => date('c')
    ];
    
    error_log("SYSTEM_METRICS: " . json_encode($stats));
}
```

## 6. Implementação Gradual

### Fase 1: Índices Críticos
1. Criar índices para `depix_id` e `blockchainTxID`
2. Configurar SQLite com WAL mode
3. Implementar timeouts de conexão

### Fase 2: Cache
1. Implementar cache de cotações
2. Otimizar consultas de contagem
3. Adicionar profiling de queries

### Fase 3: Polling Inteligente
1. Implementar intervalos adaptativos
2. Adicionar backoff exponencial
3. Monitoramento de performance

## 7. Scripts de Implementação

### Script de criação de índices:
```sql
-- /home/mau/bot/ghostbackend/scripts/create_indexes.sql
-- Executar: sqlite3 /path/to/database.db < create_indexes.sql

-- Configurações de performance
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;

-- Índices críticos
CREATE INDEX IF NOT EXISTS idx_deposit_depix_id ON deposit(depix_id);
CREATE INDEX IF NOT EXISTS idx_deposit_blockchain_txid ON deposit(blockchainTxID);
CREATE INDEX IF NOT EXISTS idx_deposit_status ON deposit(status);
CREATE INDEX IF NOT EXISTS idx_deposit_created_at ON deposit(created_at);
CREATE INDEX IF NOT EXISTS idx_cotacoes_recentes ON cotacoes(moeda_origem, moeda_destino, origem, data_atualizacao);

-- Análise da tabela para otimizar índices
ANALYZE;

-- Verificar índices criados
.indexes deposit
.indexes cotacoes
```

### Script de benchmark:
```php
// /home/mau/bot/ghostbackend/scripts/benchmark_queries.php
<?php
require_once '../config/db.php';

function benchmarkQuery($description, $query, $params = []) {
    global $db;
    
    $start = microtime(true);
    $stmt = $db->prepare($query);
    
    foreach ($params as $i => $param) {
        $stmt->bindValue($i + 1, $param);
    }
    
    $result = $stmt->execute();
    $rows = 0;
    while ($result->fetchArray()) {
        $rows++;
    }
    
    $end = microtime(true);
    $duration = ($end - $start) * 1000;
    
    echo sprintf("%-50s: %6.2fms (%d rows)\n", $description, $duration, $rows);
}

echo "=== BENCHMARK DE CONSULTAS ===\n\n";

// Testar consultas críticas
benchmarkQuery("SELECT por depix_id", "SELECT * FROM deposit WHERE depix_id = ?", ['test123']);
benchmarkQuery("SELECT pendentes (blockchainTxID)", "SELECT * FROM deposit WHERE blockchainTxID IS NULL");
benchmarkQuery("SELECT para monitoramento", "SELECT * FROM deposit WHERE blockchainTxID IS NOT NULL AND status != 'confirmado'");
benchmarkQuery("SELECT cotações recentes", "SELECT * FROM cotacoes WHERE data_atualizacao >= datetime('now', '-1 minute')");

echo "\n=== FIM BENCHMARK ===\n";
?>
```

## Impacto Esperado

- **Redução de 70-90%** no tempo de consultas com índices
- **Diminuição de 50%** na carga do servidor com cache
- **Melhoria de 60%** na responsividade do sistema
- **Redução significativa** no uso de CPU dos cron jobs

## Monitoramento Contínuo

1. Logs de queries lentas (>100ms)
2. Métricas de uso de memória
3. Tamanho do banco de dados
4. Frequência de consultas por endpoint
5. Taxa de cache hit/miss
