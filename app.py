import sys

from PyQt6.QtWidgets import QApplication

from chronometer.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
