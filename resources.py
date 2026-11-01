"""Localização comum dos recursos no código e no executável PyInstaller."""

from pathlib import Path
import sys


def resource_path(*parts: str) -> Path:
    """Obtém um caminho relativo à raiz dos recursos da aplicação."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # pylint: disable=protected-access
    else:
        base = Path(__file__).resolve().parent
    return base.joinpath(*parts)
