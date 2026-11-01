"""Regressões dos controlos e da coordenação das janelas em Qt offscreen."""

from types import SimpleNamespace

from PyQt6.QtCore import QRect
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from chronometer.about_dialog import AboutDialog
from chronometer.config import ConfigManager
from chronometer.countdown import Countdown
from chronometer.theme import DARK, LIGHT
from chronometer.windows_displays import NativeDisplay, find_native_display


def test_initial_duration_and_manual_apply(window):
    """O arranque carrega dez minutos; editar o campo só tem efeito após Definir."""
    assert window.time_main_label.text() == "10:00"
    assert not window.countdown_timer.isActive()
    assert not window.output_window.isVisible()
    window.spin_minutes.setValue(3)
    assert window.remaining_seconds == 600
    window.btn_set.click()
    assert window.remaining_seconds == 180
    window.btn_start.click()
    assert window.countdown_timer.isActive()
    window.preset_buttons[0][0].click()
    assert window.remaining_seconds == 60
    assert not window.countdown_timer.isActive()


def test_both_windows_pause_reset_and_hide(window):
    """As janelas mostram a mesma leitura; esconder a saída não para a contagem."""
    clock = [0.0]
    window.countdown = Countdown(600, clock=lambda: clock[0])
    window.start_countdown()
    clock[0] = 5.0
    window.countdown_timer.timeout.emit()
    assert window.time_main_label.text() == window.output_window.label.text() == "09:55"
    window.stop_countdown()
    clock[0] = 50.0
    assert window.remaining_seconds == 595
    window.start_countdown()
    window.output_window.show()
    window.close_output_window()
    assert window.countdown.is_running
    assert not window.output_window.isVisible()
    window.output_window.show()
    QTest.mouseClick(window.output_window.clock_label, Qt.MouseButton.LeftButton)
    assert not window.output_window.isVisible()
    assert window.countdown.is_running
    window.call_attention()
    window.reset_countdown()
    assert window.remaining_seconds == 600
    assert not window.countdown.is_running
    assert not window.output_window.flash_timer.isActive()


def test_language_and_about_theme(window):
    """A mudança de idioma inclui o menu e o diálogo usa o tema atual do painel."""
    window.combo_language.setCurrentIndex(window.combo_language.findData("en_US"))
    assert window.help_menu.title() == "Help"
    assert window.btn_start.text() == "Start"
    assert ConfigManager.get_language() == "en_US"
    window.toggle_dark_mode()
    dark_dialog = AboutDialog(window)
    assert DARK["bg"] in dark_dialog.styleSheet()
    window.toggle_dark_mode()
    light_dialog = AboutDialog(window)
    assert LIGHT["bg"] in light_dialog.styleSheet()
    dark_dialog.close()
    light_dialog.close()


def test_output_thresholds_and_flash_completion(window):
    """Os limites de cor e o fim do efeito de atenção correspondem ao guia."""
    output = window.output_window
    for seconds, color in ((60, "white"), (59, "#ff9f0a"), (0, "#ff9f0a"), (-1, "#ff3b30")):
        output.update_time_display(seconds)
        assert f"color: {color};" in output.label.styleSheet()
    output.start_attention_flash()
    for _index in range(8):
        output.flash_timer.timeout.emit()
    assert not output.flash_timer.isActive()
    assert output.styleSheet() == "background-color: black;"
    assert "#ff3b30" in output.label.styleSheet()


def _screen(x: int):
    """Simula dois monitores com metadados iguais e posições diferentes."""
    return SimpleNamespace(
        name=lambda: "screen", serialNumber=lambda: "", manufacturer=lambda: "maker",
        model=lambda: "model", geometry=lambda: QRect(x, 0, 1920, 1080),
    )


def test_monitor_identity_and_saved_fallback(window_factory, monkeypatch):
    """Desambigua a lista de monitores e recupera uma preferência desaparecida no arranque."""
    first, second = _screen(0), _screen(1920)
    monkeypatch.setattr(QApplication, "screens", lambda: [first, second])
    panel = window_factory()
    first_id = panel.combo_monitors.itemData(0)
    second_id = panel.combo_monitors.itemData(1)
    assert first_id != second_id
    ConfigManager.save_monitor_id("missing")
    ConfigManager.save_monitor_index(99)
    assert window_factory().combo_monitors.currentData() == second_id
    ConfigManager.save_monitor_id(first_id)
    assert window_factory().combo_monitors.currentData() == first_id
    native = NativeDisplay("physical-id", "screen", "Monitor de teste")
    monkeypatch.setattr("chronometer.main_window.enumerate_native_displays", lambda: [native])
    assert window_factory().combo_monitors.itemData(0) == "windows:physical-id"
    assert find_native_display(r"\\.\DISPLAY1", [NativeDisplay("id", "DISPLAY1", "")]) is not None
