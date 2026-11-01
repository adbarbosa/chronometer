"""Regressões da seleção de monitores sem depender de equipamento físico."""

from types import SimpleNamespace
from unittest.mock import Mock, call

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtWidgets import QWidget

from chronometer.displays import DisplayManager
from chronometer.windows_displays import (
    DisplayDeviceInfo, NativeDisplay, enumerate_native_displays, find_native_display,
)


def _screen(name: str, x: int, serial: str = ""):
    """Fornece os metadados Qt usados pela seleção e uma geometria previsível."""
    return SimpleNamespace(
        name=lambda: name, serialNumber=lambda: serial, manufacturer=lambda: "Maker",
        model=lambda: "Model", geometry=lambda: QRect(x, 0, 1920, 1080),
    )


def test_refresh_and_identity_disambiguation():
    """Metadados repetidos mantêm identidades diferentes e a identidade nativa tem prioridade."""
    first, second = _screen("same", 0), _screen("same", 1920)
    manager = DisplayManager(lambda: [first, second], lambda: [])
    displays = manager.refresh()
    assert displays[0].identifier == "metadata:Maker|Model|same|geometry:0:0:1920:1080"
    assert displays[1].identifier == "metadata:Maker|Model|same|geometry:1920:0:1920:1080"
    native = NativeDisplay("physical-id", "same", "Monitor físico")
    manager = DisplayManager(lambda: [first], lambda: [native])
    assert manager.refresh()[0].identifier == "windows:physical-id"
    assert manager.displays[0].description == "Monitor físico"


def test_saved_preference_and_empty_fallback():
    """A seleção usa identidade, índice antigo válido, segundo ecrã e ausência de ecrãs."""
    manager = DisplayManager(lambda: [_screen("first", 0), _screen("second", 1920)], lambda: [])
    manager.refresh()
    assert manager.preferred_index(manager.displays[0].identifier, 1) == 0
    assert manager.preferred_index("missing", 0) == 0
    assert manager.preferred_index("missing", 99) == 1
    manager = DisplayManager(lambda: [_screen("only", 0)], lambda: [])
    manager.refresh()
    assert manager.preferred_index("missing", 99) == 0
    manager = DisplayManager(lambda: [], lambda: [])
    manager.refresh()
    assert manager.preferred_index(None) == -1


def test_default_providers_are_resolved_on_refresh(monkeypatch):
    """As alterações dos fornecedores depois da construção são usadas na próxima leitura."""
    manager = DisplayManager()
    screen = _screen("screen", 0)
    monkeypatch.setattr("chronometer.displays.QApplication.screens", lambda: [screen])
    monkeypatch.setattr("chronometer.displays.enumerate_native_displays", lambda: [])
    assert manager.refresh()[0].screen is screen


def test_open_output_associates_screen_before_fullscreen():
    """Abrir a saída associa o QScreen antes da posição e do pedido de ecrã inteiro."""
    screen = _screen("target", 1920)
    native_provider = Mock(return_value=[])
    manager = DisplayManager(lambda: [screen], native_provider)
    output = Mock(spec=QWidget)
    output.isFullScreen.return_value = False
    display = manager.open_output(output, "metadata:Maker|Model|target")
    assert display is not None and display.screen is screen
    assert native_provider.call_count == 1
    assert output.mock_calls == [
        call.isFullScreen(), call.setScreen(screen), call.move(1920, 0), call.showFullScreen(),
    ]


def test_switch_output_clears_old_fullscreen_before_association():
    """Trocar uma saída já aberta limpa o estado antigo antes de associar o novo ecrã."""
    first, second = _screen("first", 0), _screen("second", 1920)
    manager = DisplayManager(lambda: [first, second], lambda: [])
    output = Mock(spec=QWidget)
    output.isFullScreen.return_value = True
    output.screen.return_value = first
    output.windowState.return_value = Qt.WindowState.WindowFullScreen
    manager.open_output(output, "metadata:Maker|Model|second")
    assert output.mock_calls == [
        call.isFullScreen(), call.screen(), call.hide(), call.windowState(),
        call.setWindowState(Qt.WindowState.WindowNoState), call.setScreen(second),
        call.move(1920, 0), call.showFullScreen(),
    ]


def test_missing_output_screen_does_not_touch_window():
    """Uma identidade desaparecida não move nem mostra a saída."""
    manager = DisplayManager(lambda: [], lambda: [])
    output = Mock(spec=QWidget)
    assert manager.open_output(output, "missing") is None
    assert not output.mock_calls


def test_native_enumeration_requests_every_monitor_interface():
    """A API simulada recebe a flag de interface e enumera mais do que o monitor zero."""
    calls = []
    adapter = DisplayDeviceInfo(r"\\.\DISPLAY1", "Adaptador", 1)
    devices = {
        (None, 0): adapter,
        (adapter.device_name, 0): DisplayDeviceInfo("monitor-a", "Monitor A", 1, "interface-a"),
        (adapter.device_name, 1): DisplayDeviceInfo("monitor-b", "Monitor B", 1, "interface-b"),
    }

    def read_device(name, index, flags):
        """Regista os argumentos sem executar chamadas da API Windows."""
        calls.append((name, index, flags))
        return devices.get((name, index))

    displays = enumerate_native_displays(read_device)
    assert [display.identifier for display in displays] == ["interface-a", "interface-b"]
    assert [display.device_name for display in displays] == [adapter.device_name, adapter.device_name]
    assert calls == [
        (None, 0, 0), (adapter.device_name, 0, 1), (adapter.device_name, 1, 1),
        (adapter.device_name, 2, 1), (None, 1, 0),
    ]


def test_native_enumeration_filters_inactive_and_mirroring_devices():
    """Adaptadores inativos ou de espelho e monitores inativos não entram na lista."""
    adapters = [
        DisplayDeviceInfo("inactive", "", 0), DisplayDeviceInfo("mirror", "", 9),
        DisplayDeviceInfo("active", "", 1),
    ]

    def read_device(name, index, _flags):
        """Simula adaptadores e um monitor inativo ligado ao adaptador ativo."""
        if name is None:
            return adapters[index] if index < len(adapters) else None
        if name == "active" and index == 0:
            return DisplayDeviceInfo("inactive-monitor", "", 0, "unused")
        return None

    assert not enumerate_native_displays(read_device)


def test_native_adapter_without_monitor_and_clone_identity():
    """Mantém uma alternativa para saídas virtuais e agrupa clones sem depender da ordem."""
    def read_device(name, index, _flags):
        """Simula um adaptador ativo sem dispositivos de monitor enumeráveis."""
        return DisplayDeviceInfo("virtual", "Virtual", 1) if name is None and index == 0 else None

    assert enumerate_native_displays(read_device) == [NativeDisplay("virtual", "virtual", "Virtual")]
    first = NativeDisplay("interface-b", r"\\.\DISPLAY1", "B")
    second = NativeDisplay("interface-a", r"\\.\DISPLAY1", "A")
    combined = find_native_display("display1", [first, second])
    assert combined == NativeDisplay("interface-a|interface-b", first.device_name, "A / B")
    assert find_native_display("DISPLAY1", [second, first]) == combined
    assert find_native_display(None, [first]) is None
