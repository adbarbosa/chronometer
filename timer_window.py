from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QDateTime, QTimer, Qt
from PyQt6.QtGui import QMouseEvent

from .theme import (
    CLOCK_INTERVAL, FLASH_INTERVAL_MS, FLASH_MAX_TICKS,
    OUTPUT, TIME_DANGER_SECS, TIME_WARN_SECS,
    OUTPUT_TIMER_H_RATIO, OUTPUT_TIMER_W_RATIO,
    OUTPUT_CLOCK_RATIO, OUTPUT_CLOCK_MIN_PX,
    output_bg_style, output_clock_style, output_flash_bg, output_time_style,
)


class TimerWindow(QWidget):
    """Janela que aparecerá no segundo monitor (Output)"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timer Output")
        self.setStyleSheet(output_bg_style())

        self.flash_timer = QTimer(self)
        self.flash_timer.setInterval(FLASH_INTERVAL_MS)
        self.flash_timer.timeout.connect(self._toggle_flash)
        self.flash_red = True
        self._flash_ticks = 0
        self._time_color = OUTPUT["time_normal"]

        self.output_clock_timer = QTimer(self)
        self.output_clock_timer.setInterval(CLOCK_INTERVAL)
        self.output_clock_timer.timeout.connect(self._update_output_clock)
        self.output_clock_timer.start()

        self._timer_size = 220
        self._clock_size = 52

        layout = QVBoxLayout()
        self.label = QLabel("00:00")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._apply_time_style(OUTPUT["time_normal"])

        self.clock_label = QLabel("00:00")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clock_label.mousePressEvent = self._on_clock_clicked
        self.clock_label.setStyleSheet(output_clock_style())

        layout.addWidget(self.label)
        layout.addWidget(self.clock_label)
        self.setLayout(layout)
        self._update_output_clock()

    def resizeEvent(self, event) -> None:
        h = event.size().height()
        w = event.size().width()
        self._timer_size = min(int(h * OUTPUT_TIMER_H_RATIO), int(w * OUTPUT_TIMER_W_RATIO))
        self._clock_size = max(int(self._timer_size * OUTPUT_CLOCK_RATIO), OUTPUT_CLOCK_MIN_PX)
        self._apply_time_style(self._time_color)
        self.clock_label.setStyleSheet(output_clock_style(self._clock_size))
        super().resizeEvent(event)

    def update_time_display(self, remaining_seconds: int) -> None:
        minutes, seconds = divmod(max(remaining_seconds, 0), 60)
        self.label.setText(f"{minutes:02d}:{seconds:02d}")
        self._update_time_color(remaining_seconds)

    def _update_time_color(self, remaining_seconds: int) -> None:
        if remaining_seconds < TIME_DANGER_SECS:
            color = OUTPUT["time_danger"]
        elif remaining_seconds < TIME_WARN_SECS:
            color = OUTPUT["time_warn"]
        else:
            color = OUTPUT["time_normal"]

        self._time_color = color
        self._apply_time_style(color)

    def _apply_time_style(self, color: str) -> None:
        self.label.setStyleSheet(output_time_style(color, self._timer_size))

    def start_attention_flash(self) -> None:
        self.flash_red = True
        self._flash_ticks = 0
        if not self.flash_timer.isActive():
            self.flash_timer.start()

    def stop_attention_flash(self) -> None:
        self.flash_timer.stop()
        self._restore_background()

    def _restore_background(self) -> None:
        self.setStyleSheet(output_bg_style())
        self._apply_time_style(self._time_color)

    def _toggle_flash(self) -> None:
        self._flash_ticks += 1
        if self._flash_ticks >= FLASH_MAX_TICKS:
            self.stop_attention_flash()
            return

        if self.flash_red:
            self.setStyleSheet(output_flash_bg(True))
            self._apply_time_style(OUTPUT["flash_contrast"])
        else:
            self.setStyleSheet(output_flash_bg(False))
            self._apply_time_style(OUTPUT["flash_contrast_white"])
        self.flash_red = not self.flash_red

    def _update_output_clock(self) -> None:
        now = QDateTime.currentDateTime()
        self.clock_label.setText(now.toString("HH:mm"))

    def _on_clock_clicked(self, event: QMouseEvent) -> None:
        self.hide()
