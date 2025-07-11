#!/usr/bin/env python3
# SCRIPT DE MIGRAÇÃO - MENU COMPRA V1 → V2
# Substitui o menu antigo pelo novo no bot principal

import os
import shutil
from datetime import datetime

def fazer_backup():
    """Faz backup do menu antigo"""
    backup_dir = "/home/mau/bot/ghost/backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/menu_compra_backup_{timestamp}.py"
    
    try:
        shutil.copy("/home/mau/bot/ghost/menus/menu_compra.py", backup_file)
        print(f"✅ Backup criado: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Erro no backup: {e}")
        return False

def atualizar_bot_principal():
    """Atualiza bot.py para usar o menu V2"""
    bot_file = "/home/mau/bot/ghost/bot.py"
    
    try:
        # Lê o arquivo atual
        with open(bot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substitui imports
        content = content.replace(
            "from menus.menu_compra import get_compra_conversation, set_menu_principal",
            "from menus.menu_compra_v2 import get_compra_conversation_v2 as get_compra_conversation, set_menu_principal_v2 as set_menu_principal"
        )
        
        # Adiciona comentário de migração
        if "# MIGRAÇÃO MENU V2" not in content:
            migration_comment = f"""
# MIGRAÇÃO MENU V2 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Menu de compra migrado para versão V2 (limpa e otimizada)
# Backup do menu antigo disponível em /home/mau/bot/ghost/backup/
"""
            content = migration_comment + content
        
        # Salva o arquivo atualizado
        with open(bot_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ bot.py atualizado para usar Menu V2")
        return True
        
    except Exception as e:
        print(f"❌ Erro atualizando bot.py: {e}")
        return False

def criar_script_reversao():
    """Cria script para reverter a migração se necessário"""
    script_content = '''#!/usr/bin/env python3
# SCRIPT DE REVERSÃO - MENU V2 → V1
# Reverte para o menu antigo em caso de problemas

import os
import shutil
from datetime import datetime

def reverter_migracao():
    """Reverte para o menu antigo"""
    try:
        # Encontra o backup mais recente
        backup_dir = "/home/mau/bot/ghost/backup"
        backups = [f for f in os.listdir(backup_dir) if f.startswith("menu_compra_backup_")]
        
        if not backups:
            print("❌ Nenhum backup encontrado!")
            return False
        
        backup_mais_recente = sorted(backups)[-1]
        backup_path = os.path.join(backup_dir, backup_mais_recente)
        
        # Restaura o menu antigo
        shutil.copy(backup_path, "/home/mau/bot/ghost/menus/menu_compra.py")
        print(f"✅ Menu antigo restaurado de: {backup_path}")
        
        # Atualiza bot.py
        bot_file = "/home/mau/bot/ghost/bot.py"
        with open(bot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            "from menus.menu_compra_v2 import get_compra_conversation_v2 as get_compra_conversation, set_menu_principal_v2 as set_menu_principal",
            "from menus.menu_compra import get_compra_conversation, set_menu_principal"
        )
        
        with open(bot_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ bot.py revertido para menu V1")
        print("🔄 Reinicie o bot para aplicar as mudanças")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na reversão: {e}")
        return False

if __name__ == "__main__":
    print("🔄 REVERTENDO MIGRAÇÃO MENU V2 → V1")
    print("=" * 50)
    
    if reverter_migracao():
        print("✅ Reversão concluída com sucesso!")
    else:
        print("❌ Falha na reversão!")
'''
    
    try:
        with open("/home/mau/bot/ghost/scripts/reverter_menu_v2.py", 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        os.chmod("/home/mau/bot/ghost/scripts/reverter_menu_v2.py", 0o755)
        print("✅ Script de reversão criado: /home/mau/bot/ghost/scripts/reverter_menu_v2.py")
        return True
        
    except Exception as e:
        print(f"❌ Erro criando script de reversão: {e}")
        return False

def main():
    """Executa a migração completa"""
    print("🚀 INICIANDO MIGRAÇÃO MENU COMPRA V1 → V2")
    print("=" * 60)
    
    # Cria diretório de scripts se não existir
    os.makedirs("/home/mau/bot/ghost/scripts", exist_ok=True)
    
    # Passo 1: Backup
    print("\n📦 PASSO 1: Fazendo backup do menu atual...")
    if not fazer_backup():
        print("❌ Falha no backup! Abortando migração.")
        return False
    
    # Passo 2: Atualizar bot principal
    print("\n🔄 PASSO 2: Atualizando bot.py...")
    if not atualizar_bot_principal():
        print("❌ Falha na atualização! Verifique manualmente.")
        return False
    
    # Passo 3: Criar script de reversão
    print("\n📜 PASSO 3: Criando script de reversão...")
    criar_script_reversao()
    
    print("\n" + "=" * 60)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("\n📋 RESUMO:")
    print("   ✅ Backup do menu antigo criado")
    print("   ✅ bot.py atualizado para Menu V2")
    print("   ✅ Script de reversão disponível")
    
    print("\n🔄 PRÓXIMOS PASSOS:")
    print("   1. Reinicie o bot: python -m ghost.bot")
    print("   2. Teste o fluxo de compra")
    print("   3. Se houver problemas: python scripts/reverter_menu_v2.py")
    
    print("\n📁 ARQUIVOS:")
    print("   📦 Backup: /home/mau/bot/ghost/backup/")
    print("   🆕 Menu V2: /home/mau/bot/ghost/menus/menu_compra_v2.py")
    print("   🔄 Reversão: /home/mau/bot/ghost/scripts/reverter_menu_v2.py")
    
    return True

if __name__ == "__main__":
    main()
