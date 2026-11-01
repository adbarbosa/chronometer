"""Fixtures Qt que mantêm os testes independentes da configuração real."""

import builtins
import os

import pytest
from PyQt6 import sip
from PyQt6.QtCore import QCoreApplication, QEvent
from PyQt6.QtWidgets import QApplication

from chronometer import i18n
from chronometer.config import ConfigManager
from chronometer.main_window import MainWindow


@pytest.fixture(name="qt_app", scope="session")
def application():
    """Cria uma aplicação Qt sem exigir um ecrã físico."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


@pytest.fixture(name="window_factory")
def isolated_windows(qt_app, monkeypatch, tmp_path):
    """Cria um painel com preferências temporárias e restaura a tradução global."""
    monkeypatch.setattr(ConfigManager, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(builtins, "_", lambda message: message, raising=False)
    monkeypatch.setattr(i18n, "_current_language", None)
    i18n.setup_i18n("pt_PT")
    panels = []

    def create_panel():
        """Regista cada painel criado para o fechar no fim do teste."""
        panel = MainWindow()
        panels.append(panel)
        return panel

    yield create_panel
    for panel in panels:
        if sip.isdeleted(panel):
            continue
        panel.close()
        panel.output_window.deleteLater()
        panel.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    qt_app.processEvents()


@pytest.fixture(name="window")
def isolated_window(window_factory):
    """Fornece um único painel com a mesma limpeza da fábrica de janelas."""
    return window_factory()
