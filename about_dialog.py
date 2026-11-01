"""Diálogo Sobre com o tema do painel e informação do projeto."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices

from chronometer import __version__
from chronometer.icon_manager import get_app_icon
from chronometer.theme import ABOUT, build_about_style

GITHUB_URL = "https://github.com/adbarbosa/chronometer"


class AboutDialog(QDialog):
    """Apresenta informação do projeto num diálogo modal."""

    def __init__(self, parent=None):
        """Usa o ícone comum e o tema atual da janela principal."""
        super().__init__(parent)
        self.setWindowIcon(get_app_icon())
        self.setModal(True)
        self.setMinimumSize(*ABOUT["size"])
        self.setStyleSheet(build_about_style(bool(getattr(parent, "dark_mode", False))))
        self._build_ui()
        self._retranslate_ui()

    def _build_ui(self) -> None:
        """Constrói os elementos do diálogo com dimensões centralizadas."""
        layout = QVBoxLayout()
        layout.setContentsMargins(*ABOUT["margins"])
        layout.setSpacing(ABOUT["spacing"])

        header_layout = QHBoxLayout()
        header_layout.setSpacing(ABOUT["header_spacing"])
        icon_label = QLabel()
        icon_label.setPixmap(get_app_icon().pixmap(ABOUT["icon_size"], ABOUT["icon_size"]))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        self.title_label = QLabel(f"Chronometer v{__version__}")
        self.title_label.setObjectName("about_title")
        title_layout.addWidget(self.title_label)
        self.tagline_label = QLabel()
        self.tagline_label.setObjectName("about_tagline")
        self.tagline_label.setWordWrap(True)
        title_layout.addWidget(self.tagline_label)
        title_layout.addStretch()
        header_layout.addLayout(title_layout, 1)
        layout.addLayout(header_layout)

        separator = QLabel()
        separator.setObjectName("about_separator")
        separator.setFixedHeight(ABOUT["separator_height"])
        layout.addWidget(separator)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)
        self.features_title_label = QLabel()
        self.features_title_label.setObjectName("about_features")
        layout.addWidget(self.features_title_label)

        features_layout = QVBoxLayout()
        features_layout.setContentsMargins(*ABOUT["feature_margins"])
        features_layout.setSpacing(ABOUT["feature_spacing"])
        self.feature_labels = []
        for _index in range(4):
            label = QLabel()
            label.setWordWrap(True)
            features_layout.addWidget(label)
            self.feature_labels.append(label)
        layout.addLayout(features_layout)
        layout.addStretch(1)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(ABOUT["button_spacing"])
        self.btn_website = QPushButton()
        self.btn_website.setMinimumHeight(ABOUT["button_height"])
        self.btn_website.clicked.connect(self._open_github)
        button_layout.addWidget(self.btn_website)
        button_layout.addStretch(1)
        self.btn_close = QPushButton()
        self.btn_close.setMinimumHeight(ABOUT["button_height"])
        self.btn_close.setMinimumWidth(ABOUT["close_width"])
        self.btn_close.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_close)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _retranslate_ui(self) -> None:
        """Aplica as mensagens do idioma atual."""
        self.setWindowTitle(_("Sobre"))
        self.tagline_label.setText(_("Cronómetro para Apresentações"))
        self.description_label.setText(
            _("Um cronómetro simples e eficiente para gerir tempos de apresentações "
              "com painel de controlo e visor em segundo monitor.")
        )
        self.features_title_label.setText(_("Funcionalidades:"))
        features = [
            _("Presets de duração (1 a 5 minutos, depois 10, 15, 20, 25, 30, 45 e 60 minutos)"),
            _("Suporte a múltiplos monitores com fullscreen"),
            _("Avisos visuais por cor (branco → laranja → vermelho)"),
            _("Internacionalização (Português e Inglês)"),
        ]
        for label, text in zip(self.feature_labels, features):
            label.setText(f"• {text}")
        self.btn_website.setText(_("Abrir no GitHub"))
        self.btn_close.setText(_("Fechar"))

    def _open_github(self) -> None:
        """Abre o repositório no navegador predefinido."""
        QDesktopServices.openUrl(QUrl(GITHUB_URL))
