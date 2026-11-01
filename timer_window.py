"""Janela de saída com o temporizador para o público."""

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QDateTime, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QHideEvent, QMouseEvent, QShowEvent

from chronometer.theme import (
    CLOCK_INTERVAL, FLASH_INTERVAL_MS, FLASH_MAX_TICKS,
    OUTPUT, TIME_DANGER_SECS, TIME_WARN_SECS,
    OUTPUT_TIMER_H_RATIO, OUTPUT_TIMER_W_RATIO,
    OUTPUT_CLOCK_RATIO, OUTPUT_CLOCK_MIN_PX,
    OUTPUT_TIMER_DEFAULT_PX, OUTPUT_CLOCK_DEFAULT_PX,
    output_bg_style, output_clock_style, output_flash_bg, output_time_style,
)
from chronometer.icon_manager import get_app_icon


class TimerWindow(QWidget):
    """Janela que aparecerá no segundo monitor (Output)"""

    visibility_changed = pyqtSignal(bool)

    def __init__(self):
        """Cria o visor, o relógio local e o efeito de atenção."""
        super().__init__()
        self.setWindowIcon(get_app_icon())
        self.setStyleSheet(output_bg_style())

        self.flash_timer = QTimer(self)
        self.flash_timer.setInterval(FLASH_INTERVAL_MS)
        self.flash_timer.timeout.connect(self._toggle_flash)
        self._flash_phase: bool | None = None
        self._flash_ticks = 0
        self._time_color = OUTPUT["time_normal"]

        self.output_clock_timer = QTimer(self)
        self.output_clock_timer.setInterval(CLOCK_INTERVAL)
        self.output_clock_timer.timeout.connect(self._update_output_clock)
        self.output_clock_timer.start()

        self._timer_size = OUTPUT_TIMER_DEFAULT_PX
        self._clock_size = OUTPUT_CLOCK_DEFAULT_PX

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
        self.retranslate_ui()

    def resizeEvent(self, event) -> None:  # pylint: disable=invalid-name
        """Reajusta os tamanhos de fonte ao redimensionar."""
        h = event.size().height()
        w = event.size().width()
        self._timer_size = min(int(h * OUTPUT_TIMER_H_RATIO), int(w * OUTPUT_TIMER_W_RATIO))
        self._clock_size = max(int(self._timer_size * OUTPUT_CLOCK_RATIO), OUTPUT_CLOCK_MIN_PX)
        self._render_output()
        self.clock_label.setStyleSheet(output_clock_style(self._clock_size))
        super().resizeEvent(event)

    def update_time_display(self, remaining_seconds: int) -> None:
        """Mostra o tempo restante e ajusta a cor."""
        if remaining_seconds < 0:
            minutes, seconds = divmod(-remaining_seconds, 60)
            self.label.setText(f"-{minutes:02d}:{seconds:02d}")
        else:
            minutes, seconds = divmod(remaining_seconds, 60)
            self.label.setText(f"{minutes:02d}:{seconds:02d}")
        self._update_time_color(remaining_seconds)

    def _update_time_color(self, remaining_seconds: int) -> None:
        """Escolhe a cor correspondente ao tempo restante."""
        if remaining_seconds < TIME_DANGER_SECS:
            color = OUTPUT["time_danger"]
        elif remaining_seconds < TIME_WARN_SECS:
            color = OUTPUT["time_warn"]
        else:
            color = OUTPUT["time_normal"]

        self._time_color = color
        self._render_output()

    def _render_output(self) -> None:
        """Combina a cor temporal com o contraste exigido pela fase atual do efeito."""
        if self._flash_phase is None:
            self.setStyleSheet(output_bg_style())
            color = self._time_color
        else:
            self.setStyleSheet(output_flash_bg(self._flash_phase))
            color = OUTPUT["flash_contrast"] if self._flash_phase else OUTPUT["flash_contrast_white"]
        self._apply_time_style(color)

    def _apply_time_style(self, color: str) -> None:
        """Aplica a cor e o tamanho atual ao texto da contagem."""
        self.label.setStyleSheet(output_time_style(color, self._timer_size))

    def start_attention_flash(self) -> None:
        """Inicia o piscar de atenção."""
        self._flash_phase = None
        self._flash_ticks = 0
        self._render_output()
        self.flash_timer.start()

    def stop_attention_flash(self) -> None:
        """Para o piscar e restaura o fundo."""
        self.flash_timer.stop()
        self._flash_phase = None
        self._render_output()

    def _toggle_flash(self) -> None:
        """Alterna o fundo até ao limite de eventos do efeito de atenção."""
        if not self.flash_timer.isActive():
            return
        self._flash_ticks += 1
        if self._flash_ticks >= FLASH_MAX_TICKS:
            self.stop_attention_flash()
            return

        self._flash_phase = True if self._flash_phase is None else not self._flash_phase
        self._render_output()

    def showEvent(self, event: QShowEvent) -> None:
        """Notifica o painel depois de a saída se tornar visível."""
        super().showEvent(event)
        self.visibility_changed.emit(self.isVisible())

    def hideEvent(self, event: QHideEvent) -> None:
        """Notifica a visibilidade após esconder ou fechar a janela."""
        super().hideEvent(event)
        self.visibility_changed.emit(self.isVisible())

    def _update_output_clock(self) -> None:
        """Apresenta a hora local no formato de 24 horas."""
        now = QDateTime.currentDateTime()
        self.clock_label.setText(now.toString("HH:mm"))

    def _on_clock_clicked(self, _event: QMouseEvent) -> None:
        """Esconde a saída sem interferir com a contagem."""
        self.hide()

    def retranslate_ui(self) -> None:
        """Atualiza os textos da UI para o idioma atual."""
        self.setWindowTitle(_("Saída do temporizador"))
