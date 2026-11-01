"""Identificação nativa de monitores no Windows."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import ctypes
from ctypes import wintypes
import sys

DISPLAY_ACTIVE_FLAG = 0x00000001
DISPLAY_MIRRORING_FLAG = 0x00000008
MONITOR_INTERFACE_FLAG = 0x00000001


@dataclass(frozen=True)
class NativeDisplay:
    """Informação nativa de um monitor Windows associada ao nome GDI do adaptador."""

    identifier: str
    device_name: str
    description: str


@dataclass(frozen=True)
class DisplayDeviceInfo:
    """Copia apenas os campos usados da estrutura devolvida pela API nativa."""

    device_name: str
    description: str
    state_flags: int
    identifier: str = ""


if sys.platform == "win32":
    class _DisplayDevice(ctypes.Structure):
        """Representação da estrutura DISPLAY_DEVICEW da API Windows."""

        _fields_ = [
            ("cb", wintypes.DWORD),
            ("DeviceName", wintypes.WCHAR * 32),
            ("DeviceString", wintypes.WCHAR * 128),
            ("StateFlags", wintypes.DWORD),
            ("DeviceID", wintypes.WCHAR * 128),
            ("DeviceKey", wintypes.WCHAR * 128),
        ]

    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _enum_display_devices = _user32.EnumDisplayDevicesW
    _enum_display_devices.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.POINTER(_DisplayDevice),
        wintypes.DWORD,
    ]
    _enum_display_devices.restype = wintypes.BOOL


def _read_display_device(device_name: str | None, index: int, flags: int) -> DisplayDeviceInfo | None:
    """Lê um dispositivo através da API nativa; usado apenas em Windows."""
    device = _DisplayDevice()
    device.cb = ctypes.sizeof(device)  # pylint: disable=attribute-defined-outside-init
    if not _enum_display_devices(device_name, index, ctypes.byref(device), flags):
        return None
    return DisplayDeviceInfo(device.DeviceName, device.DeviceString, device.StateFlags, device.DeviceID)


def _adapter_monitors(
    adapter: DisplayDeviceInfo,
    device_reader: Callable[[str | None, int, int], DisplayDeviceInfo | None],
) -> list[NativeDisplay]:
    """Enumera todos os monitores do adaptador pedindo a interface por monitor."""
    displays = []
    monitor_index = 0
    while True:
        monitor = device_reader(adapter.device_name, monitor_index, MONITOR_INTERFACE_FLAG)
        if monitor is None:
            break
        monitor_index += 1
        if not monitor.state_flags & DISPLAY_ACTIVE_FLAG:
            continue
        identifier = monitor.identifier or monitor.device_name or f"{adapter.device_name}:{monitor_index - 1}"
        displays.append(NativeDisplay(
            identifier=identifier,
            device_name=adapter.device_name,
            description=monitor.description or adapter.description,
        ))
    if monitor_index == 0:
        displays.append(NativeDisplay(adapter.device_name, adapter.device_name, adapter.description))
    return displays


def enumerate_native_displays(
    device_reader: Callable[[str | None, int, int], DisplayDeviceInfo | None] | None = None,
) -> list[NativeDisplay]:
    """Enumera interfaces dos monitores ativos; aceita uma API simulada nos testes."""
    if device_reader is None:
        if sys.platform != "win32":
            return []
        device_reader = _read_display_device

    displays = []
    adapter_index = 0
    while True:
        adapter = device_reader(None, adapter_index, 0)
        if adapter is None:
            break
        adapter_index += 1
        if not adapter.state_flags & DISPLAY_ACTIVE_FLAG or adapter.state_flags & DISPLAY_MIRRORING_FLAG:
            continue
        displays.extend(_adapter_monitors(adapter, device_reader))
    return displays


def find_native_display(screen_name: str | None, displays: list[NativeDisplay]) -> NativeDisplay | None:
    """Relaciona o nome Qt com o adaptador GDI e agrupa monitores que partilham essa saída."""
    if not screen_name:
        return None
    normalized_name = screen_name.casefold().removeprefix("\\\\.\\")
    matches = [display for display in displays if
               display.device_name.casefold().removeprefix("\\\\.\\") == normalized_name]
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    # Um ecrã Qt pode representar uma saída clonada; não escolher arbitrariamente o primeiro monitor físico.
    return NativeDisplay(
        identifier="|".join(sorted({display.identifier for display in matches})),
        device_name=matches[0].device_name,
        description=" / ".join(sorted({display.description for display in matches if display.description})),
    )
