"""Identificação nativa de monitores no Windows."""

from __future__ import annotations

from dataclasses import dataclass
import ctypes
import sys
from ctypes import wintypes


@dataclass(frozen=True)
class NativeDisplay:
    """Informação nativa de um monitor Windows."""

    identifier: str
    device_name: str
    description: str


if sys.platform == "win32":
    class _DisplayDevice(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("DeviceName", wintypes.WCHAR * 32),
            ("DeviceString", wintypes.WCHAR * 128),
            ("StateFlags", wintypes.DWORD),
            ("DeviceID", wintypes.WCHAR * 128),
            ("DeviceKey", wintypes.WCHAR * 128),
        ]

    _DISPLAY_DEVICE_ACTIVE = 0x00000001
    _DISPLAY_DEVICE_MIRRORING_DRIVER = 0x00000008
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _enum_display_devices = _user32.EnumDisplayDevicesW
    _enum_display_devices.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.POINTER(_DisplayDevice),
        wintypes.DWORD,
    ]
    _enum_display_devices.restype = wintypes.BOOL


def _read_display_device(device_name: str | None, index: int) -> _DisplayDevice | None:
    device = _DisplayDevice()
    device.cb = ctypes.sizeof(device)
    if not _enum_display_devices(device_name, index, ctypes.byref(device), 0):
        return None
    return device


def enumerate_native_displays() -> list[NativeDisplay]:
    """Enumera monitores físicos ativos no Windows."""
    if sys.platform != "win32":
        return []

    displays = []
    adapter_index = 0
    while True:
        adapter = _read_display_device(None, adapter_index)
        if adapter is None:
            break
        adapter_index += 1

        if not adapter.StateFlags & _DISPLAY_DEVICE_ACTIVE:
            continue
        if adapter.StateFlags & _DISPLAY_DEVICE_MIRRORING_DRIVER:
            continue

        monitor = _read_display_device(adapter.DeviceName, 0)
        if monitor is not None:
            identifier = monitor.DeviceID or monitor.DeviceKey
            description = monitor.DeviceString or adapter.DeviceString
        else:
            identifier = adapter.DeviceID or adapter.DeviceKey
            description = adapter.DeviceString

        identifier = identifier or adapter.DeviceName
        displays.append(
            NativeDisplay(
                identifier=identifier,
                device_name=adapter.DeviceName,
                description=description,
            )
        )

    return displays


def find_native_display(
    screen_name: str | None, displays: list[NativeDisplay]
) -> NativeDisplay | None:
    """Relaciona o nome de um QScreen com o nome nativo DISPLAYx."""
    if not screen_name:
        return None

    normalized_name = screen_name.casefold().removeprefix("\\\\.\\")
    for display in displays:
        normalized_device_name = display.device_name.casefold().removeprefix("\\\\.\\")
        if normalized_name == normalized_device_name:
            return display
    return None
