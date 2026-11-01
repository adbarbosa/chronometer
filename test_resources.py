"""Testes dos recursos em execução normal e na raiz extraída pelo PyInstaller."""

from pathlib import Path
import sys

from chronometer.resources import resource_path


def test_source_resources_exist(monkeypatch, tmp_path):
    """O ícone e os catálogos são encontrados a partir de qualquer diretório de trabalho."""
    monkeypatch.chdir(tmp_path)
    assert resource_path("icon", "chronometer-stopwatch-svgrepo-com.svg").is_file()
    assert resource_path("i18n", "locales", "en_US", "LC_MESSAGES", "chronometer.mo").is_file()


def test_frozen_resource_root(monkeypatch, tmp_path):
    """O executável procura os recursos na raiz de extração, sem repetir o nome do pacote."""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert resource_path("icon", "example.svg") == Path(tmp_path) / "icon" / "example.svg"
