"""
Módulo para gerenciamento do ícone da aplicação.
Fornece uma função unificada para obter o ícone em diferentes plataformas.
"""
from pathlib import Path
from PyQt6.QtGui import QIcon

# Caminhos para os ícones
ICON_DIR = Path(__file__).resolve().parent / "icon"
ICO_ICON_PATH = ICON_DIR / "chronometer-stopwatch-svgrepo-com.ico"
SVG_ICON_PATH = ICON_DIR / "chronometer-stopwatch-svgrepo-com.svg"


def get_app_icon() -> QIcon:
    """
    Retorna o ícone da aplicação, tentando primeiro o formato .ico (Windows)
    e depois o .svg (Linux) como fallback.
    
    Returns:
        QIcon: O ícone da aplicação ou ícone padrão se nenhum estiver disponível.
    """
    if ICO_ICON_PATH.exists():
        return QIcon(str(ICO_ICON_PATH))
    elif SVG_ICON_PATH.exists():
        return QIcon(str(SVG_ICON_PATH))
    else:
        return QIcon()  # Ícone padrão
