import sys
import locale
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from chronometer import __version__
from chronometer.i18n import setup_i18n
from chronometer.main_window import MainWindow


ICON_PATH = Path(__file__).resolve().parent / "icon" / "chronometer-stopwatch-svgrepo-com.ico"


def main() -> None:
    # Configurar internacionalização antes de criar a UI
    lang = locale.getdefaultlocale()[0] or "pt_PT"
    setup_i18n(lang)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Chronometer")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
