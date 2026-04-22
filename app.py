import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from chronometer import __version__
from chronometer.main_window import MainWindow


ICON_PATH = Path(__file__).resolve().parent / "icon" / "chronometer-stopwatch-svgrepo-com.ico"


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Chronometer")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
