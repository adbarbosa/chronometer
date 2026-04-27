"""Diálogo 'Sobre Chronometer' com informação do projeto e link para GitHub."""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices
from pathlib import Path

from chronometer import __version__


ICON_PATH = Path(__file__).resolve().parent / "icon" / "chronometer-stopwatch-svgrepo-com.svg"

# URL do repositório
GITHUB_URL = "https://github.com/adbarbosa/chronometer"


class AboutDialog(QDialog):
    """Diálogo modal 'Sobre Chronometer' com informação e link do projeto."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Sobre"))
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setModal(True)
        self.setFixedSize(500, 380)
        self.setStyleSheet("background-color: #f5f5f5; color: #333333;")

        self._build_ui()
        self._retranslate_ui()

    def _build_ui(self) -> None:
        """Constrói a UI do diálogo."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Ícone e título
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        icon_label = QLabel()
        pixmap = QIcon(str(ICON_PATH)).pixmap(64, 64)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        self.title_label = QLabel(f"Chronometer v{__version__}")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a1a1a;")
        title_layout.addWidget(self.title_label)

        self.tagline_label = QLabel()
        self.tagline_label.setStyleSheet("font-size: 12px; color: #555555;")
        self.tagline_label.setWordWrap(True)
        title_layout.addWidget(self.tagline_label)
        title_layout.addStretch()

        header_layout.addLayout(title_layout, 1)
        layout.addLayout(header_layout)

        # Separador visual
        separator = QLabel()
        separator.setStyleSheet("background-color: #ddd; min-height: 1px;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Descrição
        self.description_label = QLabel()
        self.description_label.setStyleSheet("font-size: 11px; color: #444444;")
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        # Features
        self.features_title_label = QLabel()
        self.features_title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(self.features_title_label)

        features_layout = QVBoxLayout()
        features_layout.setContentsMargins(20, 0, 0, 0)
        features_layout.setSpacing(4)

        self.feature_labels = []
        feature_keys = ["feature1", "feature2", "feature3", "feature4"]
        for key in feature_keys:
            feature_label = QLabel()
            feature_label.setStyleSheet("font-size: 10px; color: #333333;")
            feature_label.setWordWrap(True)
            features_layout.addWidget(feature_label)
            self.feature_labels.append((key, feature_label))

        layout.addLayout(features_layout)

        # Espaço em branco
        layout.addStretch(1)

        # Botões inferiores
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_website = QPushButton()
        self.btn_website.setMinimumHeight(36)
        self.btn_website.setStyleSheet(
            "QPushButton {"
            "  background-color: #007AFF;"
            "  color: white;"
            "  border: none;"
            "  border-radius: 4px;"
            "  padding: 0px 20px;"
            "  font-size: 12px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "  background-color: #0051D5;"
            "}"
        )
        self.btn_website.clicked.connect(self._open_github)
        button_layout.addWidget(self.btn_website)

        button_layout.addStretch(1)

        self.btn_close = QPushButton()
        self.btn_close.setMinimumHeight(36)
        self.btn_close.setMinimumWidth(100)
        self.btn_close.setStyleSheet(
            "QPushButton {"
            "  background-color: #e8e8e8;"
            "  color: #333333;"
            "  border: none;"
            "  border-radius: 4px;"
            "  padding: 0px 20px;"
            "  font-size: 12px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "  background-color: #d0d0d0;"
            "}"
        )
        self.btn_close.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_close)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _retranslate_ui(self) -> None:
        """Atualiza textos para o idioma atual."""
        self.setWindowTitle(_("Sobre"))
        self.tagline_label.setText(_("Cronómetro para Apresentações"))
        self.description_label.setText(
            _("Um cronómetro simples e eficiente para gerir tempos de apresentações "
              "com painel de controlo e visor em segundo monitor.")
        )
        self.features_title_label.setText(_("Funcionalidades:"))

        # Textos das features
        features_text = {
            "feature1": _("Presets de duração (10, 15, 20, 25, 30, 35, 45, 60 minutos)"),
            "feature2": _("Suporte a múltiplos monitores com fullscreen"),
            "feature3": _("Avisos visuais por cor (branco → laranja → vermelho)"),
            "feature4": _("Internacionalização (Português e Inglês)"),
        }

        for key, label_widget in self.feature_labels:
            label_widget.setText(f"• {features_text.get(key, '')}")

        self.btn_website.setText(_("Abrir no GitHub"))
        self.btn_close.setText(_("Fechar"))

    def _open_github(self) -> None:
        """Abre o URL do repositório GitHub no navegador."""
        QDesktopServices.openUrl(QUrl(GITHUB_URL))
