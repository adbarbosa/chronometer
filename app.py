import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QGuiApplication

from chronometer import __version__
from chronometer.config import ConfigManager
from chronometer.i18n import setup_i18n
from chronometer.main_window import MainWindow
from chronometer.icon_manager import get_app_icon


def main() -> None:
    # Configurar internacionalização antes de criar a UI
    # Usar idioma guardado nas configurações, ou detetar do sistema
    saved_lang = ConfigManager.get_language()
    setup_i18n(saved_lang)
    
    # FIX PARA WINDOWS: Definir AppID para que o ícone apareça na barra de tarefas
    import ctypes
    if sys.platform == 'win32':
        app_id = "adbtech.chronometer"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Chronometer")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(get_app_icon())
    
    # FIX PARA LINUX/WAYLAND: Definir desktop file name para associar o ícone
    # Isso é CRUCIAL para o Wayland mostrar o ícone corretamente
    QGuiApplication.setDesktopFileName("adbtech.chronometer")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
