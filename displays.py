"""Identificação, seleção e colocação da saída nos monitores disponíveis."""

from collections.abc import Callable
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QApplication, QWidget

from chronometer.windows_displays import NativeDisplay, enumerate_native_displays, find_native_display


@dataclass(frozen=True)
class DisplayInfo:
    """Associa um ecrã Qt à identidade e à descrição usadas pelo painel."""

    screen: QScreen
    identifier: str
    name: str
    description: str


def screen_identifier(screen: QScreen) -> str:
    """Identifica um monitor pelos metadados disponíveis ou pela sua geometria."""
    metadata = (screen.serialNumber(), screen.manufacturer(), screen.model(), screen.name())
    values = [value.strip() for value in metadata if value and value.strip()]
    if values:
        return "metadata:" + "|".join(values)
    geometry = screen.geometry()
    return f"geometry:{geometry.x()}:{geometry.y()}:{geometry.width()}:{geometry.height()}"


def display_identifier(screen: QScreen, screens: list[QScreen], native_displays: list[NativeDisplay]) -> str:
    """Prefere a interface nativa e distingue metadados repetidos pela geometria."""
    native = find_native_display(screen.name(), native_displays)
    if native is not None:
        return f"windows:{native.identifier}"
    identifier = screen_identifier(screen)
    if sum(screen_identifier(candidate) == identifier for candidate in screens) <= 1:
        return identifier
    geometry = screen.geometry()
    return f"{identifier}|geometry:{geometry.x()}:{geometry.y()}:{geometry.width()}:{geometry.height()}"


class DisplayManager:
    """Mantém uma fotografia dos ecrãs sem guardar preferências nem alterar a contagem."""

    def __init__(
        self,
        screens_provider: Callable[[], list[QScreen]] | None = None,
        native_provider: Callable[[], list[NativeDisplay]] | None = None,
    ):
        """Aceita fornecedores substituíveis para verificar a seleção sem monitores físicos."""
        self._screens_provider = screens_provider
        self._native_provider = native_provider
        self.displays: list[DisplayInfo] = []

    def refresh(self) -> list[DisplayInfo]:
        """Lê os fornecedores atuais e atualiza as identidades e descrições disponíveis."""
        screens = (self._screens_provider or QApplication.screens)()
        native_displays = (self._native_provider or enumerate_native_displays)()
        self.displays = []
        for screen in screens:
            native = find_native_display(screen.name(), native_displays)
            self.displays.append(DisplayInfo(
                screen=screen,
                identifier=display_identifier(screen, screens, native_displays),
                name=native.device_name if native is not None else screen.name(),
                description=native.description if native is not None else "",
            ))
        return self.displays

    def find(self, identifier: str | None) -> DisplayInfo | None:
        """Procura uma identidade na última fotografia dos ecrãs."""
        return next((display for display in self.displays if display.identifier == identifier), None)

    def preferred_index(self, identifier: str | None, legacy_index: int = 1) -> int:
        """Prefere a identidade guardada, o índice antigo e depois o segundo ou único ecrã."""
        for index, display in enumerate(self.displays):
            if display.identifier == identifier:
                return index
        if 0 <= legacy_index < len(self.displays):
            return legacy_index
        return min(1, len(self.displays) - 1)

    def open_output(self, output: QWidget, identifier: str | None) -> DisplayInfo | None:
        """Associa explicitamente a saída ao ecrã e pede ecrã inteiro nessa associação."""
        self.refresh()
        display = self.find(identifier)
        if display is None:
            return None
        if output.isFullScreen() and output.screen() is not display.screen:
            output.hide()
            output.setWindowState(output.windowState() & ~Qt.WindowState.WindowFullScreen)
        output.setScreen(display.screen)
        geometry = display.screen.geometry()
        output.move(geometry.left(), geometry.top())
        output.showFullScreen()
        return display
