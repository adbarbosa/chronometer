from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import QDateTime, QTimer, Qt

from .theme import CLOCK_INTERVAL, COUNTDOWN_INTERVAL, build_control_styles
from .timer_window import TimerWindow


class MainWindow(QMainWindow):
    """Painel de Controle Principal"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Talk Chronometer - Control")
        self.setFixedSize(520, 520)

        self.remaining_seconds = 0
        self.loaded_preset_seconds = 0
        self.dark_mode = False

        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(COUNTDOWN_INTERVAL)
        self.countdown_timer.timeout.connect(self._tick_countdown)

        self.clock_timer = QTimer(self)
        self.clock_timer.setInterval(CLOCK_INTERVAL)
        self.clock_timer.timeout.connect(self._update_datetime)

        # Inicializa a janela de saída
        self.output_window = TimerWindow()

        self._build_ui()
        self._connect_signals()
        self._apply_theme()
        self._update_displays()
        self._update_datetime()
        self.clock_timer.start()

    def _build_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        monitor_row = QHBoxLayout()
        monitor_row.setSpacing(8)
        self.combo_monitors = QComboBox()
        self.combo_monitors.setMinimumHeight(32)
        self.btn_output = QPushButton("Abrir")
        self.btn_close_output = QPushButton("Fechar")
        self.btn_refresh_monitors = QPushButton("↻")
        self.btn_refresh_monitors.setFixedSize(36, 36)
        for _btn in (self.btn_output, self.btn_close_output):
            _btn.setMinimumHeight(32)
        monitor_row.addWidget(self.combo_monitors, 1)
        monitor_row.addWidget(self.btn_output)
        monitor_row.addWidget(self.btn_close_output)
        monitor_row.addWidget(self.btn_refresh_monitors)
        self.label_status = QLabel("")
        self._populate_monitors()

        self.time_main_label = QLabel("00:00")
        self.time_main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.presets_container = QWidget()
        presets_layout = QGridLayout()
        presets_layout.setContentsMargins(10, 10, 10, 10)
        presets_layout.setHorizontalSpacing(8)
        presets_layout.setVerticalSpacing(8)

        preset_minutes = [10, 15, 20, 25, 30, 35, 45, 60]
        self.preset_buttons = []
        for index, minutes in enumerate(preset_minutes):
            button = QPushButton(f"{minutes} min")
            button.setMinimumHeight(38)
            row = index // 4
            col = index % 4
            presets_layout.addWidget(button, row, col)
            self.preset_buttons.append((button, minutes))

        self.presets_container.setLayout(presets_layout)

        manual_row = QHBoxLayout()
        manual_row.setSpacing(8)
        self.btn_minus = QPushButton("−")
        self.btn_minus.setFixedSize(44, 38)
        self.spin_minutes = QSpinBox()
        self.spin_minutes.setRange(1, 180)
        self.spin_minutes.setValue(10)
        self.spin_minutes.setSuffix(" min")
        self.spin_minutes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_minutes.setMinimumHeight(38)
        self.btn_plus = QPushButton("+")
        self.btn_plus.setFixedSize(44, 38)
        self.btn_set = QPushButton("Definir")
        self.btn_set.setMinimumHeight(38)
        manual_row.addWidget(self.btn_minus)
        manual_row.addWidget(self.spin_minutes, 1)
        manual_row.addWidget(self.btn_plus)
        manual_row.addWidget(self.btn_set)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(8)

        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_reset = QPushButton("Reset")

        for btn in (self.btn_start, self.btn_stop, self.btn_reset):
            btn.setMinimumHeight(46)
            controls_row.addWidget(btn)

        self.btn_attention = QPushButton("Call Attention")
        self.btn_attention.setMinimumHeight(46)

        footer = QHBoxLayout()
        self.label_clock = QLabel("00:00:00")
        self.label_date = QLabel("01/01/2000")
        self.btn_dark_mode = QPushButton("\U0001f319 Dark Mode")
        self.btn_dark_mode.setFixedHeight(28)
        self.label_clock.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.addWidget(self.label_clock)
        footer.addStretch(1)
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

    def _connect_signals(self) -> None:
        self.btn_output.clicked.connect(self.setup_monitors)
        self.btn_close_output.clicked.connect(self.close_output_window)
        self.btn_refresh_monitors.clicked.connect(self._populate_monitors)
        self.btn_dark_mode.clicked.connect(self.toggle_dark_mode)
        self.btn_start.clicked.connect(self.start_countdown)
        self.btn_stop.clicked.connect(self.stop_countdown)
        self.btn_reset.clicked.connect(self.reset_countdown)
        self.btn_attention.clicked.connect(self.call_attention)
        self.btn_minus.clicked.connect(lambda: self.spin_minutes.stepDown())
        self.btn_plus.clicked.connect(lambda: self.spin_minutes.stepUp())
        self.btn_set.clicked.connect(self._apply_manual_time)

        for button, minutes in self.preset_buttons:
            button.clicked.connect(lambda _checked=False, m=minutes: self.load_preset(m))

    def _populate_monitors(self) -> None:
        self.combo_monitors.clear()
        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            geo = screen.geometry()
            name = screen.name() or f"Monitor {i + 1}"
            self.combo_monitors.addItem(
                f"{i + 1}. {name} ({geo.width()}×{geo.height()})", i
            )
        if len(screens) > 1:
            self.combo_monitors.setCurrentIndex(1)
        self.label_status.setText(f"{len(screens)} monitor(es) detectado(s)")

    def setup_monitors(self) -> None:
        idx = self.combo_monitors.currentData()
        screens = QApplication.screens()
        if idx is None or idx >= len(screens):
            self._populate_monitors()
            return

        screen = screens[idx]
        geometry = screen.geometry()
        self.output_window.move(geometry.left(), geometry.top())
        self.output_window.showFullScreen()
        self.label_status.setText(f"Aberto em: {self.combo_monitors.currentText()}")
        self._update_displays()

    def load_preset(self, minutes: int) -> None:
        self.stop_countdown()
        self.loaded_preset_seconds = minutes * 60
        self.remaining_seconds = self.loaded_preset_seconds
        self.spin_minutes.setValue(minutes)
        self._update_displays()

    def _apply_manual_time(self) -> None:
        self.load_preset(self.spin_minutes.value())

    def start_countdown(self) -> None:
        if self.remaining_seconds <= 0 and self.loaded_preset_seconds > 0:
            self.remaining_seconds = self.loaded_preset_seconds

        if self.remaining_seconds > 0:
            self.output_window.stop_attention_flash()
            self.countdown_timer.start()

    def stop_countdown(self) -> None:
        self.countdown_timer.stop()

    def reset_countdown(self) -> None:
        self.stop_countdown()
        self.output_window.stop_attention_flash()
        self.remaining_seconds = self.loaded_preset_seconds
        self._update_displays()

    def call_attention(self) -> None:
        self.output_window.start_attention_flash()

    def close_output_window(self) -> None:
        self.output_window.hide()
        self.label_status.setText("Output fechado.")

    def toggle_dark_mode(self) -> None:
        self.dark_mode = not self.dark_mode
        self._apply_theme()

    def _apply_theme(self) -> None:
        s = build_control_styles(self.dark_mode)

        if self.dark_mode:
            self.btn_dark_mode.setText("\u2600 Light Mode")
        else:
            self.btn_dark_mode.setText("\U0001f319 Dark Mode")

        self.centralWidget().setStyleSheet(s["background"])
        self.label_status.setStyleSheet(s["status"])
        self.time_main_label.setStyleSheet(s["timer"])
        self.presets_container.setStyleSheet(s["presets_box"])

        for btn, _ in self.preset_buttons:
            btn.setStyleSheet(s["preset_btn"])

        for btn in (self.btn_minus, self.btn_plus):
            btn.setStyleSheet(s["preset_btn"])
        self.btn_set.setStyleSheet(s["preset_btn"])
        self.spin_minutes.setStyleSheet(s["spinbox"])

        for btn in (self.btn_start, self.btn_stop, self.btn_reset):
            btn.setStyleSheet(s["control_btn"])

        for btn in (self.btn_output, self.btn_close_output, self.btn_refresh_monitors):
            btn.setStyleSheet(s["monitor_btn"])

        self.combo_monitors.setStyleSheet(s["spinbox"])

        self.btn_attention.setStyleSheet(s["attention_btn"])
        self.btn_dark_mode.setStyleSheet(s["toggle_btn"])
        self.label_clock.setStyleSheet(s["footer"])
        self.label_date.setStyleSheet(s["footer"])

    def _tick_countdown(self) -> None:
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._update_displays()

        if self.remaining_seconds <= 0:
            self.countdown_timer.stop()

    def _update_displays(self) -> None:
        minutes, seconds = divmod(max(self.remaining_seconds, 0), 60)
        self.time_main_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.output_window.update_time_display(self.remaining_seconds)

    def _update_datetime(self) -> None:
        now = QDateTime.currentDateTime()
        self.label_clock.setText(now.toString("HH:mm:ss"))
        self.label_date.setText(now.toString("dd/MM/yyyy"))

    def closeEvent(self, event) -> None:
        self.output_window.close()
        event.accept()
