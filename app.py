import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from chronometer.main_window import MainWindow


ICON_PATH = Path(__file__).resolve().parent / "icon" / "chronometer-stopwatch-svgrepo-com.ico"


def main() -> None:
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
