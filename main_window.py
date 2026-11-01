"""Janela principal de controlo do Chronometer."""

from PyQt6.QtWidgets import (
    QApplication,
    QAbstractSpinBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QStyle,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import QDateTime, QTimer, Qt, QUrl, QSize, pyqtSlot
from PyQt6.QtGui import QDesktopServices, QScreen

from chronometer import __version__
from chronometer.about_dialog import GITHUB_URL, AboutDialog
from chronometer.config import ConfigManager
from chronometer.countdown import Countdown
from chronometer.displays import DisplayInfo, DisplayManager
from chronometer.i18n import setup_i18n, get_current_language
from chronometer.theme import (
    CLOCK_INTERVAL, CONTROL, COUNTDOWN_INTERVAL, PREFERENCE_MESSAGE_MS, build_control_styles,
)
from chronometer.timer_window import TimerWindow
from chronometer.icon_manager import get_app_icon


DEFAULT_MINUTES = 10


class MainWindow(QMainWindow):
    """Painel de controlo e coordenação das duas janelas."""

    def __init__(self):
        """Carrega as preferências e prepara uma contagem de dez minutos parada."""
        super().__init__()
        self.setFixedSize(*CONTROL["size"])
        self.setWindowIcon(get_app_icon())

        self.countdown = Countdown(DEFAULT_MINUTES * 60)
        self.display_manager = DisplayManager()
        self._opened_monitor_id: str | None = None
        self._output_closed = False

        # Carregar preferência de tema
        self.dark_mode = ConfigManager.get_dark_mode()

        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(COUNTDOWN_INTERVAL)
        self.countdown_timer.timeout.connect(self._tick_countdown)

        self.clock_timer = QTimer(self)
        self.clock_timer.setInterval(CLOCK_INTERVAL)
        self.clock_timer.timeout.connect(self._update_datetime)

        # Inicializa a janela de saída
        self.output_window = TimerWindow()
        self.destroyed.connect(self.output_window.deleteLater)

        self._build_ui()
        self._build_menu_bar()
        self._connect_signals()
        self._apply_theme()
        self._update_displays()
        self._update_datetime()
        self._retranslate_ui()
        self.clock_timer.start()

        # Carregar preferência do último monitor
        self._load_saved_monitor_preference()

        # Selecionar idioma atual no combo
        self._select_current_language()

    @property
    def remaining_seconds(self) -> int:
        """Expõe o tempo calculado pelo modelo da contagem."""
        return self.countdown.remaining_seconds

    @property
    def loaded_preset_seconds(self) -> int:
        """Expõe a duração usada ao repor ou reiniciar uma contagem esgotada."""
        return self.countdown.loaded_seconds

    def _build_ui(self) -> None:
        """Constrói os controlos e o campo de duração manual."""
        layout = QVBoxLayout()
        layout.setContentsMargins(*CONTROL["margins"])
        layout.setSpacing(CONTROL["spacing"])

        monitor_row = QHBoxLayout()
        monitor_row.setSpacing(CONTROL["spacing"])
        self.combo_monitors = QComboBox()
        self.combo_monitors.setMinimumHeight(CONTROL["monitor_height"])
        self.btn_refresh_monitors = QPushButton()
        self.btn_refresh_monitors.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        )
        self.btn_refresh_monitors.setIconSize(QSize(CONTROL["refresh_icon"], CONTROL["refresh_icon"]))
        self.btn_output = QPushButton(_("Abrir"))
        self.btn_close_output = QPushButton(_("Fechar"))
        self.btn_refresh_monitors.setFixedSize(CONTROL["refresh_size"], CONTROL["refresh_size"])
        for _btn in (self.btn_output, self.btn_close_output):
            _btn.setMinimumHeight(CONTROL["monitor_height"])
        monitor_row.addWidget(self.combo_monitors, 1)
        monitor_row.addWidget(self.btn_refresh_monitors)
        monitor_row.addWidget(self.btn_output)
        monitor_row.addWidget(self.btn_close_output)
        self.label_status = QLabel("")
        self._populate_monitors()

        self.time_main_label = QLabel("00:00")
        self.time_main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.presets_container = QWidget()
        presets_layout = QGridLayout()
        presets_layout.setContentsMargins(*CONTROL["preset_margins"])
        presets_layout.setHorizontalSpacing(CONTROL["spacing"])
        presets_layout.setVerticalSpacing(CONTROL["spacing"])

        preset_minutes = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 45, 60]
        self.preset_buttons = []
        for index, minutes in enumerate(preset_minutes):
            button = QPushButton(f"{minutes}{_(' min')}")
            button.setMinimumHeight(CONTROL["preset_height"])
            row = index // 6
            col = index % 6
            presets_layout.addWidget(button, row, col)
            self.preset_buttons.append((button, minutes))

        self.presets_container.setLayout(presets_layout)

        manual_row = QHBoxLayout()
        manual_row.setSpacing(CONTROL["spacing"])
        self.spin_minutes = QSpinBox()
        self.spin_minutes.setRange(0, 180)
        self.spin_minutes.setValue(DEFAULT_MINUTES)
        self.spin_minutes.setSuffix(_(" min"))
        self.spin_minutes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_minutes.setMinimumHeight(CONTROL["preset_height"])
        self.spin_minutes.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.btn_minus = QPushButton("−")
        self.btn_minus.setFixedSize(CONTROL["step_width"], CONTROL["preset_height"])
        self.btn_plus = QPushButton("+")
        self.btn_plus.setFixedSize(CONTROL["step_width"], CONTROL["preset_height"])
        self.btn_set = QPushButton(_("Definir"))
        self.btn_set.setMinimumHeight(CONTROL["preset_height"])
        manual_row.addWidget(self.spin_minutes, 1)
        manual_row.addWidget(self.btn_minus)
        manual_row.addWidget(self.btn_plus)
        manual_row.addWidget(self.btn_set)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(CONTROL["spacing"])

        self.btn_start = QPushButton(_("Iniciar"))
        self.btn_stop = QPushButton(_("Parar"))
        self.btn_reset = QPushButton(_("Repor"))

        for btn in (self.btn_start, self.btn_stop, self.btn_reset):
            btn.setMinimumHeight(CONTROL["control_height"])
            controls_row.addWidget(btn)

        self.btn_attention = QPushButton(_("Chamar Atenção"))
        self.btn_attention.setMinimumHeight(CONTROL["control_height"])

        footer = QHBoxLayout()
        self.label_clock = QLabel("00:00:00")
        self.label_date = QLabel("01/01/2000")
        self.btn_dark_mode = QPushButton()
        self.btn_dark_mode.setFixedHeight(CONTROL["footer_height"])

        # Seletor de idioma
        self.combo_language = QComboBox()
        self.combo_language.setFixedHeight(CONTROL["footer_height"])
        self.combo_language.setMinimumWidth(CONTROL["language_width"])
        for lang_code, lang_name in ConfigManager.LANGUAGE_NAMES.items():
            self.combo_language.addItem(lang_name, lang_code)

        self.label_clock.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.addWidget(self.label_clock)
        footer.addStretch(1)
        footer.addWidget(self.combo_language)
        footer.addWidget(self.btn_dark_mode)
        footer.addStretch(1)
        footer.addWidget(self.label_date)

        layout.addWidget(self.label_status)
        layout.addLayout(monitor_row)
        layout.addWidget(self.time_main_label)
        layout.addWidget(self.presets_container)
        layout.addLayout(manual_row)
        layout.addLayout(controls_row)
        layout.addWidget(self.btn_attention)
        layout.addStretch(1)
        layout.addLayout(footer)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.statusBar().setSizeGripEnabled(False)

    def _connect_signals(self) -> None:
        """Liga as ações do utilizador e as alterações de monitores."""
        self.btn_output.clicked.connect(self.setup_monitors)
        self.btn_close_output.clicked.connect(self.close_output_window)
        self.btn_refresh_monitors.clicked.connect(self._populate_monitors)
        app = QApplication.instance()
        if app is not None:
            app.screenAdded.connect(self._populate_monitors)
            app.screenRemoved.connect(self._handle_screen_removed)
        self.output_window.visibility_changed.connect(self._on_output_visibility_changed)
        self.btn_dark_mode.clicked.connect(self.toggle_dark_mode)
        self.btn_start.clicked.connect(self.start_countdown)
        self.btn_stop.clicked.connect(self.stop_countdown)
        self.btn_reset.clicked.connect(self.reset_countdown)
        self.btn_attention.clicked.connect(self.call_attention)
        self.btn_minus.clicked.connect(self.spin_minutes.stepDown)
        self.btn_plus.clicked.connect(self.spin_minutes.stepUp)
        self.btn_set.clicked.connect(self._apply_manual_time)
        self.combo_language.currentIndexChanged.connect(self._on_language_changed)

        for button, minutes in self.preset_buttons:
            button.clicked.connect(lambda _checked=False, m=minutes: self.load_preset(m))

    def _build_menu_bar(self) -> None:
        """Constrói a barra de menu com opção de Ajuda."""
        menubar = self.menuBar()

        # Menu Ajuda
        self.help_menu = menubar.addMenu(_("Ajuda"))

        # Ação: Sobre
        self.about_action = self.help_menu.addAction(_("Sobre Chronometer"))
        self.about_action.triggered.connect(self.show_about_dialog)

        # Separador
        self.help_menu.addSeparator()

        # Ação: Website
        self.website_action = self.help_menu.addAction(_("Visitar Website"))
        self.website_action.triggered.connect(self._open_website)

    def show_about_dialog(self) -> None:
        """Mostra o diálogo 'Sobre Chronometer'."""
        dialog = AboutDialog(self)
        dialog.exec()

    def _open_website(self) -> None:
        """Abre o website do projeto no navegador."""
        QDesktopServices.openUrl(QUrl(GITHUB_URL))

    @staticmethod
    def _display_text(display: DisplayInfo) -> str:
        """Apresenta o nome, descrição e geometria de um monitor disponível."""
        geometry = display.screen.geometry()
        name = display.name or _("Monitor")
        description = f" - {display.description}" if display.description else ""
        return (
            f"{name}{description} ({geometry.width()}×{geometry.height()}"
            f" @ {geometry.x()},{geometry.y()})"
        )

    @pyqtSlot()
    def _populate_monitors(self) -> None:
        """Atualiza a lista sem perder o estado real da saída nem reter callbacks anónimos."""
        selected_id = self.combo_monitors.currentData()
        displays = self.display_manager.refresh()
        self.combo_monitors.clear()
        for display in displays:
            self.combo_monitors.addItem(self._display_text(display), display.identifier)
        index = self.display_manager.preferred_index(selected_id, 1)
        self.combo_monitors.setCurrentIndex(index)
        self._update_output_status()

    @pyqtSlot(QScreen)
    def _handle_screen_removed(self, removed_screen) -> None:
        """Tenta reabrir a saída visível se o seu monitor foi removido."""
        output_was_removed = self.output_window.screen() is removed_screen
        output_was_visible = self.output_window.isVisible()
        self._populate_monitors()
        if output_was_visible and output_was_removed and self.combo_monitors.count():
            self.setup_monitors()

    def _load_saved_monitor_preference(self) -> None:
        """Restaura a identidade guardada, o índice antigo ou a alternativa disponível."""
        index = self.display_manager.preferred_index(
            ConfigManager.get_last_monitor_id(), ConfigManager.get_last_monitor_index(),
        )
        self.combo_monitors.setCurrentIndex(index)

    def setup_monitors(self) -> None:
        """Associa a saída ao ecrã selecionado, abre-a e tenta guardar a preferência."""
        display = self.display_manager.open_output(self.output_window, self.combo_monitors.currentData())
        if display is None:
            self._populate_monitors()
            return
        self._opened_monitor_id = display.identifier
        self._output_closed = False
        self._update_output_status()
        self._report_save_result(ConfigManager.save_monitor_id(display.identifier))
        self._update_displays()

    @pyqtSlot(bool)
    def _on_output_visibility_changed(self, visible: bool) -> None:
        """Recebe mudanças de visibilidade, incluindo cliques no relógio e fecho pelo sistema."""
        self._output_closed = not visible
        self._update_output_status()

    def _update_output_status(self) -> None:
        """Constrói o estado a partir da saída, sem confundir seleção pendente com monitor aberto."""
        if self.output_window.isVisible():
            display = self.display_manager.find(self._opened_monitor_id)
            if display is not None:
                name = self._display_text(display)
            else:
                screen = self.output_window.screen()
                name = (screen.name() if screen is not None else "") or _("Monitor")
            text = _("Aberto em: {monitor_name}").format(monitor_name=name)
        elif self._output_closed:
            text = _("Output fechado.")
        else:
            text = _("{count} monitor(es) detectado(s)").format(count=len(self.display_manager.displays))
        self.label_status.setText(text)

    def _report_save_result(self, saved: bool) -> None:
        """Informa uma falha de persistência sem bloquear a apresentação."""
        if saved:
            self.statusBar().clearMessage()
        else:
            self.statusBar().showMessage(_("Preferências não guardadas. Tente novamente."), PREFERENCE_MESSAGE_MS)

    def load_preset(self, minutes: int) -> None:
        """Carrega uma duração (em minutos) e atualiza os ecrãs."""
        self.stop_countdown()
        self.countdown.load(minutes * 60)
        self.spin_minutes.setValue(minutes)
        self._update_displays()

    def _apply_manual_time(self) -> None:
        """Carrega e para a duração indicada no campo manual."""
        self.load_preset(self.spin_minutes.value())

    def start_countdown(self) -> None:
        """Inicia a contagem decrescente."""
        self.countdown.start()
        self._update_displays()

        self.output_window.stop_attention_flash()
        self.countdown_timer.start()

    def stop_countdown(self) -> None:
        """Para a contagem decrescente."""
        self.countdown.pause()
        self.countdown_timer.stop()
        self._update_displays()

    def reset_countdown(self) -> None:
        """Repõe o tempo da predefinição carregada."""
        self.stop_countdown()
        self.output_window.stop_attention_flash()
        self.countdown.reset()
        self._update_displays()

    def call_attention(self) -> None:
        """Faz piscar o ecrã de saída."""
        self.output_window.start_attention_flash()

    def close_output_window(self) -> None:
        """Esconde a janela de saída."""
        self.output_window.hide()
        self._on_output_visibility_changed(False)

    def toggle_dark_mode(self) -> None:
        """Alterna e guarda o modo escuro."""
        self.dark_mode = not self.dark_mode
        self._report_save_result(ConfigManager.save_dark_mode(self.dark_mode))
        self._apply_theme()

    def _select_current_language(self) -> None:
        """Seleciona o idioma atual no combo box."""
        current_lang = get_current_language()
        for i in range(self.combo_language.count()):
            if self.combo_language.itemData(i) == current_lang:
                self.combo_language.blockSignals(True)
                self.combo_language.setCurrentIndex(i)
                self.combo_language.blockSignals(False)
                break

    def _on_language_changed(self, index: int) -> None:
        """Callback quando o utilizador muda o idioma."""
        lang_code = self.combo_language.itemData(index)
        if lang_code:
            # Guardar preferência
            saved = ConfigManager.save_language(lang_code)
            # Reconfigurar i18n
            setup_i18n(lang_code)
            # Atualizar toda a UI
            self._retranslate_ui()
            self.output_window.retranslate_ui()
            self._select_current_language()
            self._report_save_result(saved)

    def _retranslate_ui(self) -> None:
        """Atualiza todos os textos da UI para o idioma atual."""
        self.setWindowTitle(f"Chronometer v{__version__} - {_('Controlo')}")

        # Menu e ações
        self.help_menu.setTitle(_("Ajuda"))
        self.about_action.setText(_("Sobre Chronometer"))
        self.website_action.setText(_("Visitar Website"))

        # Botões de monitor
        self.btn_output.setText(_("Abrir"))
        self.btn_close_output.setText(_("Fechar"))

        # Presets
        for button, minutes in self.preset_buttons:
            button.setText(f"{minutes}{_(' min')}")

        # Botão definir
        self.btn_set.setText(_("Definir"))
        self.spin_minutes.setSuffix(_(" min"))

        # Controlos
        self.btn_start.setText(_("Iniciar"))
        self.btn_stop.setText(_("Parar"))
        self.btn_reset.setText(_("Repor"))
        self.btn_attention.setText(_("Chamar Atenção"))

        # Botão de tema (atualiza com base no estado atual)
        if self.dark_mode:
            self.btn_dark_mode.setText(f"\u2600 {_('Modo Claro')}")
        else:
            self.btn_dark_mode.setText(f"\U0001f319 {_('Modo Escuro')}")

        self._update_output_status()

    def _apply_theme(self) -> None:
        """Aplica os estilos centralizados ao painel de controlo."""
        s = build_control_styles(self.dark_mode)

        # Atualizar texto do botão de tema
        if self.dark_mode:
            self.btn_dark_mode.setText(f"\u2600 {_('Modo Claro')}")
        else:
            self.btn_dark_mode.setText(f"\U0001f319 {_('Modo Escuro')}")

        self.centralWidget().setStyleSheet(s["background"])
        self.statusBar().setStyleSheet(s["status_bar"])
        self.label_status.setStyleSheet(s["status"])
        self.time_main_label.setStyleSheet(s["timer"])
        self.presets_container.setStyleSheet(s["presets_box"])

        for btn, _unused in self.preset_buttons:
            btn.setStyleSheet(s["preset_btn"])

        for btn in (self.btn_minus, self.btn_plus):
            btn.setStyleSheet(s["preset_btn"])
        self.btn_set.setStyleSheet(s["preset_btn"])
        self.spin_minutes.setStyleSheet(s["spinbox"])

        for btn in (self.btn_start, self.btn_stop, self.btn_reset):
            btn.setStyleSheet(s["control_btn"])

        for btn in (self.btn_output, self.btn_close_output):
            btn.setStyleSheet(s["monitor_btn"])
        self.btn_refresh_monitors.setStyleSheet(
            s["monitor_btn"] + s["refresh"]
        )

        self.combo_monitors.setStyleSheet(s["combo"])

        self.btn_attention.setStyleSheet(s["attention_btn"])
        self.btn_dark_mode.setStyleSheet(s["toggle_btn"])
        self.combo_language.setStyleSheet(s["combo"])
        self.label_clock.setStyleSheet(s["footer"])
        self.label_date.setStyleSheet(s["footer"])

    def _tick_countdown(self) -> None:
        """Atualiza a apresentação a partir do tempo decorrido, sem contar eventos."""
        self._update_displays()

    def _update_displays(self) -> None:
        """Apresenta a mesma leitura do tempo em ambas as janelas."""
        secs = self.remaining_seconds
        if secs < 0:
            minutes, seconds = divmod(-secs, 60)
            text = f"-{minutes:02d}:{seconds:02d}"
        else:
            minutes, seconds = divmod(secs, 60)
            text = f"{minutes:02d}:{seconds:02d}"
        self.time_main_label.setText(text)
        self.output_window.update_time_display(secs)

    def _update_datetime(self) -> None:
        """Atualiza a hora e a data locais do painel."""
        now = QDateTime.currentDateTime()
        self.label_clock.setText(now.toString("HH:mm:ss"))
        self.label_date.setText(now.toString("dd/MM/yyyy"))

    def closeEvent(self, event) -> None:  # pylint: disable=invalid-name
        """Fecha também a janela de saída."""
        self.countdown.pause()
        self.countdown_timer.stop()
        self.clock_timer.stop()
        self.output_window.stop_attention_flash()
        self.output_window.output_clock_timer.stop()
        self.output_window.close()
        event.accept()
