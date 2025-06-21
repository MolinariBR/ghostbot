# Módulo de compatibilidade para Python 3.13+
# Fornece compatibilidade com imghdr que foi removido no Python 3.13

def what(file, h=None):
    """Versão simplificada de imghdr.what() para compatibilidade com Python 3.13+."""
    if h is None:
        with open(file, 'rb') as f:
            h = f.read(32)
    
    if not h:
        return None
    
    # Verifica os primeiros bytes para identificar o tipo de imagem
    if h.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    elif h.startswith(b'\xff\xd8'):
        return 'jpeg'
    elif h.startswith(b'GIF87a') or h.startswith(b'GIF89a'):
        return 'gif'
    elif h.startswith(b'BM'):
        return 'bmp'
    elif h.startswith(b'II*\x00') or h.startswith(b'MM\x00*'):
        return 'tiff'
    elif h.startswith(b'\x00\x00\x01\x00'):
        return 'ico'
    elif h.startswith(b'\x00\x00\x02\x00'):
        return 'cur'
    
    return None

# Cria um módulo falso de imghdr para compatibilidade
import sys
import types

imghdr = types.ModuleType('imghdr')
imghdr.what = what
sys.modules['imghdr'] = imghdr
