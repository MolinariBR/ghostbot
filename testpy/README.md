# 🧪 Diretório de Testes - Ghost Bot

Este diretório contém todos os arquivos de teste do projeto Ghost Bot, organizados para facilitar a manutenção e execução.

## 📁 Estrutura dos Testes

### 🔧 Testes Básicos
- `test_basic.py` - Testes básicos do sistema
- `test_quick.py` - Testes rápidos de funcionalidade
- `run_tests.py` - Script principal para executar testes

### ⚡ Testes Lightning Network
- `teste_completo_lightning.py` - Teste completo do fluxo Lightning
- `teste_lightning_especifico.py` - Testes específicos Lightning
- `teste_lightning_real.py` - Testes com Lightning real
- `teste_lightning_baixo.py` - Testes com valores baixos
- `teste_pix_lightning_corrigido.py` - Teste PIX→Lightning corrigido
- `criar_depositos_teste_lightning.py` - Criação de depósitos Lightning

### 🏦 Testes Voltz
- `test_fluxo_completo_voltz.py` - Fluxo completo integração Voltz
- `test_local_voltz.py` - Testes locais Voltz
- `test_simples_voltz.py` - Testes simples Voltz
- `teste_direto_voltz.py` - Testes diretos API Voltz
- `teste_voltz_direto.py` - Comunicação direta Voltz
- `teste_voltz_forcado.py` - Testes forçados Voltz

### 💳 Testes PIX/DePIX
- `teste_depix_real.py` - Testes com DePIX real
- `buscar_depix_criar_teste.py` - Busca e criação DePIX
- `test_pix.py` - Testes básicos PIX

### 🔗 Testes de Conectividade
- `teste_conectividade_api.py` - Teste de conectividade APIs
- `teste_webhook_simple.py` - Testes webhook simples

### 🗄️ Testes de Banco
- `teste_banco_simples.py` - Testes básicos do banco de dados
- `teste_ids_usuario.py` - Teste de IDs de usuário

### 🛠️ Testes de Handler
- `testar_handler_corrigido.py` - Teste do handler corrigido
- `testar_conversao_valores.py` - Teste conversão de valores

### 🎯 Testes Diversos
- `teste_direto.py` - Testes diretos do sistema
- `teste_local.py` - Testes locais
- `teste_simples.py` - Testes simples
- `teste_rapido.py` - Testes rápidos
- `teste_real_python.py` - Testes com dados reais
- `teste_fluxo_correto.py` - Teste do fluxo correto

### 🚀 Testes de Criação Rápida
- `criar_teste_rapido.py` - Criação rápida de testes
- `criar_depositos_teste_local.py` - Criação depósitos teste local

### 📜 Scripts Shell
- `teste_final_voltz.sh` - Script final teste Voltz
- `teste_real_completo.sh` - Script completo teste real
- `test_voltz_curl.sh` - Testes Voltz via cURL

## 🚀 Como Executar os Testes

### Execução Individual
```bash
cd /home/mau/bot/ghost/testpy
python3 nome_do_teste.py
```

### Execução via Script Principal
```bash
cd /home/mau/bot/ghost/testpy
python3 run_tests.py
```

### Execução de Scripts Shell
```bash
cd /home/mau/bot/ghost/testpy
./teste_final_voltz.sh
```

## ⚙️ Configuração

Certifique-se de que os seguintes requisitos estão atendidos:

1. **Python 3.7+** instalado
2. **Dependências** instaladas: `pip install -r ../requirements.txt`
3. **Configurações** do bot definidas em `../config.py`
4. **Banco de dados** disponível em `../data/`

## 📊 Categorização por Funcionalidade

| Categoria | Arquivos | Descrição |
|-----------|----------|-----------|
| **Core** | `test_basic.py`, `test_quick.py` | Funcionalidades básicas |
| **Lightning** | `teste_*lightning*.py` | Rede Lightning Network |
| **Voltz** | `test_*voltz*.py`, `teste_voltz_*.py` | Integração Voltz |
| **PIX** | `teste_*pix*.py`, `*depix*.py` | Pagamentos PIX/DePIX |
| **Banco** | `teste_banco_*.py` | Base de dados |
| **Handler** | `testar_handler_*.py` | Manipuladores de eventos |

## 🔄 Manutenção

- **Organização**: Todos os testes centralizados neste diretório
- **Nomenclatura**: Prefixos `test_` ou `teste_` para identificação
- **Backup**: Versões antigas preservadas se necessário
- **Limpeza**: Arquivos obsoletos removidos regularmente

---
**Diretório organizado em:** 7 de julho de 2025  
**Total de arquivos de teste:** 35  
**Última atualização:** 7 de julho de 2025
