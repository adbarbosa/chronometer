"""
Módulo para gerenciamento do ícone da aplicação.
Fornece uma função unificada para obter o ícone em diferentes plataformas.
"""
from PyQt6.QtGui import QIcon

from chronometer.resources import resource_path

# Caminhos para os ícones
ICON_DIR = resource_path("icon")
ICO_ICON_PATH = ICON_DIR / "chronometer-stopwatch-svgrepo-com.ico"
SVG_ICON_PATH = ICON_DIR / "chronometer-stopwatch-svgrepo-com.svg"


def get_app_icon() -> QIcon:
    """
    Retorna o ícone da aplicação, tentando primeiro o formato .ico (Windows)
    e depois o .svg (Linux) como fallback.

    Returns:
        QIcon: O ícone da aplicação ou um ícone vazio se não existir nenhum recurso.
    """
    for path in (ICO_ICON_PATH, SVG_ICON_PATH):
        if path.exists():
            icon = QIcon(str(path))
            if not icon.isNull():
                return icon
    return QIcon()
