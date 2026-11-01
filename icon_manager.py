"""
Módulo para gerenciamento do ícone da aplicação.
Fornece uma função unificada para obter o ícone em diferentes plataformas.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

from chronometer.resources import resource_path
from chronometer.theme import CONTROL, REFRESH_ICON_SCALES, build_refresh_icon_svg

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


def get_refresh_icon(dark: bool) -> QIcon:
    """Cria um ícone de atualizar independente do tema do sistema, em várias escalas."""
    renderer = QSvgRenderer(build_refresh_icon_svg(dark).encode("utf-8"))
    icon = QIcon()
    for scale in REFRESH_ICON_SCALES:
        size = CONTROL["refresh_icon"] * scale
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        pixmap.setDevicePixelRatio(scale)
        icon.addPixmap(pixmap)
    return icon
