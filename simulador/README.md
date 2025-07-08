# Simulador do Bot Lightning Ghost

Este diretório contém um simulador completo do bot Lightning que replica exatamente o fluxo do bot real, permitindo testes locais no VS Code.

## 📁 Arquivos

- `bot_simulator.py` - Simulador principal do bot completo
- `cron_tester.py` - Teste específico do endpoint cron Lightning
- `setup.py` - Configuração inicial do ambiente
- `README.md` - Este arquivo

## 🚀 Como usar

### 1. Setup inicial
```bash
cd /home/mau/bot/ghost/simulador
python3 setup.py
```

### 2. Executar simulação completa
```bash
# Teste padrão (R$ 50,00, chat_id padrão)
python3 bot_simulator.py

# Teste com valor específico
python3 bot_simulator.py 100.50

# Teste com valor e chat_id específicos
python3 bot_simulator.py 75.25 7910260237
```

### 3. Testar apenas o cron
```bash
# Teste do cron com chat_id padrão
python3 cron_tester.py

# Teste com chat_id específico
python3 cron_tester.py 7910260237
```

## 🔄 Fluxo simulado

O simulador replica exatamente o fluxo do bot real:

1. **Comando Lightning** - Usuário digita `/lightning 50.00`
2. **Validação** - Verifica valor mínimo/máximo
3. **Cotação BTC** - Obtém cotação atual via CoinGecko
4. **Cálculos** - Calcula sats, taxas, valor líquido
5. **Criação depósito** - Registra no banco local
6. **Backend** - Envia para API REST
7. **Confirmação PIX** - Simula webhook de confirmação
8. **Cron Lightning** - Executa cron real do servidor
9. **Solicitação endereço** - Bot pede endereço Lightning
10. **Processamento** - Valida e processa endereço
11. **Invoice** - Gera e envia Lightning Invoice

## 🧪 Testes específicos

### Cron Tester
O `cron_tester.py` executa bateria de testes:

- ✅ Verifica depósitos pendentes
- ✅ Testa cron básico
- ✅ Testa cron com chat_id
- ✅ Testa lightning_notifier
- ✅ Identifica problemas críticos

### Bot Simulator
O `bot_simulator.py` simula fluxo completo:

- 🤖 Simula interação usuário-bot
- 💰 Usa cotação BTC real
- 🗄️ Cria registros no banco local
- 🌐 Chama APIs reais do servidor
- ⚡ Processa Lightning Network
- 📊 Gera logs detalhados

## 📊 Logs

Todos os testes geram logs detalhados:
- `logs_sim_YYYYMMDD_HHMMSS.txt` - Logs do simulador completo
- Logs em tempo real no terminal

## 🔧 Troubleshooting

### Erro 500 no cron
```bash
python3 cron_tester.py
```
Identifica especificamente problemas no endpoint cron.

### Banco de dados
O simulador usa o mesmo banco do backend:
- `/home/mau/bot/ghostbackend/data/deposit.db`
- Criado automaticamente pelo setup

### APIs externas
- CoinGecko para cotação BTC
- Endpoints reais do servidor Ghost
- Lightning Address validation

## 🎯 Casos de uso

1. **Debug cron Lightning** - Identifica por que cron retorna erro 500
2. **Teste fluxo completo** - Valida todo processo Lightning
3. **Desenvolvimento local** - Testa mudanças sem afetar produção
4. **Monitoramento** - Verifica se endpoints estão funcionando

## ⚙️ Configuração

### URLs do servidor
```python
self.backend_url = "https://useghost.squareweb.app"
```

### Chat ID padrão
```python
self.chat_id = "7910260237"
```

### Banco de dados
```python
self.local_db = "/home/mau/bot/ghostbackend/data/deposit.db"
```

## 🎉 Status Atual - PROBLEMA RESOLVIDO!

✅ **CRON LIGHTNING FUNCIONANDO** (08/07/2025)

```bash
# Teste do cron - TODOS PASSARAM
python3 cron_tester.py
```

### Problemas corrigidos:
- ✅ Erro 500 no endpoint cron
- ✅ Chamadas incorretas de funções globais (`$this->calculateSatsAmount` → `calculateSatsAmount`)  
- ✅ SQL com colunas inexistentes (`lightning_status`, `error_message`, `updated_at`)
- ✅ Fluxo Lightning interrompido

### Resultado atual:
```
🎉 TODOS OS TESTES PASSARAM!
depositos..................... ✅ 12 confirmados, 30 pendentes
cron_basico................... ✅ SUCESSO  
cron_chat_id.................. ✅ SUCESSO
notifier...................... ✅ SUCESSO
```

## 🔄 Próximos passos

1. **Testar bot real** - Verificar se bot agora solicita endereço Lightning
2. **Validar fluxo ponta-a-ponta** - Do PIX até pagamento Lightning
3. **Melhorar logs** - Para facilitar futuros debugs

## 📈 Status esperado

Quando tudo estiver funcionando:

```
🧪 TESTE COMPLETO DO CRON LIGHTNING
============================================================
1️⃣ VERIFICANDO DEPÓSITOS PENDENTES
📈 Encontrados X depósitos para chat_id 7910260237

2️⃣ TESTANDO CRON BÁSICO  
✅ Resposta JSON válida

3️⃣ TESTANDO CRON COM CHAT_ID
✅ Resposta JSON válida
📈 Encontrados Y depósitos pendentes

4️⃣ TESTANDO LIGHTNING NOTIFIER
✅ Notifier funcionando

============================================================
📊 RESUMO DOS TESTES
============================================================
depositos.......................... ✅ X confirmados, Y pendentes
cron_basico........................ ✅ SUCESSO
cron_chat_id....................... ✅ SUCESSO  
notifier........................... ✅ SUCESSO

🎉 TODOS OS TESTES PASSARAM!
```
