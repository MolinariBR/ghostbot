# Este arquivo torna o diretório 'menus' um pacote Python
# Permite a importação dos módulos de menu de forma organizada

# Importa as funções do menu de compra
from .menu_compra import get_compra_conversation, set_menu_principal as set_compra_menu_principal

# Importa as funções do menu de venda
from .menu_venda import get_venda_conversation, set_menu_principal as set_venda_menu_principal

# Função para configurar os menus principais
def setup_menus(menu_principal_func):
    """Configura os menus principais para todos os submódulos."""
    set_compra_menu_principal(menu_principal_func)
    set_venda_menu_principal(menu_principal_func)
