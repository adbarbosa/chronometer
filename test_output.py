"""Regressões do contraste, da visibilidade e dos recursos da janela de saída."""

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QSignalSpy, QTest

from chronometer import icon_manager
from chronometer.theme import FLASH_MAX_TICKS


def test_flash_keeps_contrast_during_updates_and_resize(window, qt_app):
    """Atualizar ou redimensionar durante a fase branca conserva o texto preto."""
    output = window.output_window
    output.show()
    qt_app.processEvents()
    output.update_time_display(120)
    output.start_attention_flash()
    output.flash_timer.timeout.emit()
    output.flash_timer.timeout.emit()
    assert output.styleSheet() == "background-color: white;"
    assert "color: black;" in output.label.styleSheet()
    output.update_time_display(119)
    assert "color: black;" in output.label.styleSheet()
    output.resize(output.width() + 100, output.height() + 100)
    qt_app.processEvents()
    assert output.styleSheet() == "background-color: white;"
    assert "color: black;" in output.label.styleSheet()
    output.update_time_display(-1)
    for _index in range(FLASH_MAX_TICKS - 2):
        output.flash_timer.timeout.emit()
    assert output.styleSheet() == "background-color: black;"
    assert "color: #ff3b30;" in output.label.styleSheet()


@pytest.mark.parametrize("action", ["start_countdown", "reset_countdown"])
def test_start_and_reset_cancel_attention(window, action):
    """Iniciar e Repor terminam o efeito e restauram o contraste normal."""
    output = window.output_window
    output.start_attention_flash()
    output.flash_timer.timeout.emit()
    getattr(window, action)()
    assert not output.flash_timer.isActive()
    assert output.styleSheet() == "background-color: black;"
    assert "color: white;" in output.label.styleSheet()


def test_output_reports_clock_hide_and_close(window, qt_app):
    """Mostrar, esconder pelo relógio e fechar notificam a visibilidade real."""
    output = window.output_window
    changes = QSignalSpy(output.visibility_changed)
    output.show()
    qt_app.processEvents()
    QTest.mouseClick(output.clock_label, Qt.MouseButton.LeftButton)
    qt_app.processEvents()
    output.show()
    qt_app.processEvents()
    output.close()
    qt_app.processEvents()
    assert [entry[0] for entry in changes] == [True, False, True, False]


@pytest.mark.parametrize("ico_data", [None, b"ficheiro ICO invalido"])
def test_icon_uses_svg_when_ico_is_missing_or_invalid(qt_app, monkeypatch, tmp_path, ico_data):
    """Um SVG válido é usado quando o ICO não existe ou não pode ser carregado."""
    assert qt_app is not None
    ico_path = tmp_path / "icon.ico"
    if ico_data is not None:
        ico_path.write_bytes(ico_data)
    svg_path = tmp_path / "icon.svg"
    svg_path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">'
        '<rect width="32" height="32" fill="blue"/></svg>', encoding="utf-8",
    )
    monkeypatch.setattr(icon_manager, "ICO_ICON_PATH", ico_path)
    monkeypatch.setattr(icon_manager, "SVG_ICON_PATH", svg_path)
    icon = icon_manager.get_app_icon()
    assert not icon.isNull()
    assert not icon.pixmap(32, 32).isNull()


def test_icon_is_empty_only_when_all_candidates_fail(qt_app, monkeypatch, tmp_path):
    """Todos os recursos inválidos produzem um ícone vazio sem lançar exceções."""
    assert qt_app is not None
    ico_path = tmp_path / "icon.ico"
    svg_path = tmp_path / "icon.svg"
    ico_path.write_bytes(b"invalido")
    svg_path.write_bytes(b"invalido")
    monkeypatch.setattr(icon_manager, "ICO_ICON_PATH", ico_path)
    monkeypatch.setattr(icon_manager, "SVG_ICON_PATH", svg_path)
    assert icon_manager.get_app_icon().isNull()
