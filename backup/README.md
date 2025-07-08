# 🗄️ Backup - Scripts de Desenvolvimento e Diagnóstico

Este diretório contém arquivos de desenvolvimento, debug, diagnóstico e utilitários que não são essenciais para o funcionamento principal do bot em produção.

## 📁 Estrutura dos Arquivos

### 🔍 Scripts de Diagnóstico
- `diagnostico_lightning.py` - Diagnóstico completo do sistema Lightning
- `diagnostico_servidor.py` - Diagnóstico do servidor e conectividade
- `diagnostico_voltz.py` - Diagnóstico da integração Voltz

### 🐛 Scripts de Debug
- `debug_lightning_handler.py` - Debug específico do handler Lightning
- `debug_query_endpoint.py` - Debug de consultas aos endpoints
- `debug_valores_handler.py` - Debug de manipulação de valores

### 📊 Scripts de Resumo
- `resumo_correcoes.py` - Resumo das correções implementadas
- `resumo_final.py` - Resumo final do projeto

### 🎯 Scripts de Exemplo
- `exemplo_bot_real.py` - Exemplo de uso do bot com dados reais

### 🔧 Utilitários de Desenvolvimento
- `buscar_depix_real.py` - Busca informações DePIX reais
- `criar_lightning_rapido.py` - Criação rápida de Lightning
- `criar_lightning_servidor.py` - Criação Lightning no servidor
- `investigacao_logs.py` - Investigação e análise de logs

### 🎭 Scripts de Simulação
- `simular_pix_confirmado.py` - Simula confirmação de PIX
- `simular_webhook_depix.py` - Simula webhooks DePIX

### ✅ Scripts de Verificação
- `verificar_depositos.py` - Verificação de depósitos
- `verificar_saldo_voltz.py` - Verificação de saldo Voltz

## 🚀 Como Usar

### Execução Individual
```bash
cd /home/mau/bot/ghost/backup
python3 nome_do_script.py
```

### Diagnóstico Completo
```bash
# Lightning Network
python3 diagnostico_lightning.py

# Servidor
python3 diagnostico_servidor.py

# Voltz
python3 diagnostico_voltz.py
```

### Debug Específico
```bash
# Handler Lightning
python3 debug_lightning_handler.py

# Endpoints
python3 debug_query_endpoint.py

# Valores
python3 debug_valores_handler.py
```

### Simulações
```bash
# Simular PIX confirmado
python3 simular_pix_confirmado.py

# Simular webhook DePIX
python3 simular_webhook_depix.py
```

## ⚙️ Configuração

Estes scripts utilizam as mesmas configurações do bot principal:

1. **Dependências:** `pip install -r ../requirements.txt`
2. **Configurações:** Definidas em `../config.py`
3. **Tokens:** Carregados de `../tokens.py`
4. **Base de dados:** Acesso ao banco em `../data/`

## 📋 Categorização por Função

| 🏷️ Categoria | 📄 Quantidade | 🎯 Finalidade |
|--------------|---------------|---------------|
| **Diagnóstico** | 3 | Análise completa do sistema |
| **Debug** | 3 | Depuração específica de componentes |
| **Resumo** | 2 | Documentação de correções |
| **Exemplo** | 1 | Demonstração de uso |
| **Utilitários** | 4 | Ferramentas de desenvolvimento |
| **Simulação** | 2 | Testes de fluxo sem dados reais |
| **Verificação** | 2 | Validação de estados |

## ⚠️ Observações Importantes

1. **Não são scripts de produção** - Usados apenas para desenvolvimento e debug
2. **Podem conter dados sensíveis** - Revisar antes de compartilhar
3. **Dependem do ambiente de desenvolvimento** - Alguns podem não funcionar em produção
4. **Mantidos para referência** - Úteis para debugging futuro e manutenção

## 🔄 Manutenção

- **Backup periódico:** Arquivos importantes preservados
- **Limpeza ocasional:** Remover scripts obsoletos
- **Documentação:** Manter este README atualizado
- **Versionamento:** Incluído no controle de versão para histórico

## 🎯 Benefícios da Organização

1. **Diretório principal limpo** - Apenas código de produção
2. **Desenvolvimento organizado** - Scripts de dev centralizados
3. **Facilita manutenção** - Debug e diagnóstico acessíveis
4. **Preserva histórico** - Correções e evoluções documentadas

---
**Arquivos organizados em:** 7 de julho de 2025  
**Total de arquivos:** 17  
**Finalidade:** Desenvolvimento, debug e diagnóstico  
**Status:** Backup preservado para referência futura
