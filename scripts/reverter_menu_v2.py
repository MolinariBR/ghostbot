#!/usr/bin/env python3
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
