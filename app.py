import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from chronometer import __version__
from chronometer.config import ConfigManager
from chronometer.i18n import setup_i18n
from chronometer.main_window import MainWindow


ICON_PATH = Path(__file__).resolve().parent / "icon" / "chronometer-stopwatch-svgrepo-com.ico"


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
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
