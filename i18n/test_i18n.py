"""Testes de carregamento, atualização e compilação das traduções."""

import builtins
from pathlib import Path
from string import Formatter
import sys

import polib
import pytest

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from chronometer import i18n  # pylint: disable=wrong-import-position
from chronometer.config import ConfigManager  # pylint: disable=wrong-import-position
from chronometer.i18n.compile import compile_catalogs  # pylint: disable=wrong-import-position
from chronometer.i18n.update import extract_messages, update_catalogs  # pylint: disable=wrong-import-position

PROJECT_DIR = Path(__file__).resolve().parent.parent
EXPECTED = {
    "pt_PT": {"Abrir": "Abrir", "Controlo": "Controlo", "Ajuda": "Ajuda", "Iniciar": "Iniciar"},
    "en_US": {"Abrir": "Open", "Controlo": "Control", "Ajuda": "Help", "Iniciar": "Start"},
}


@pytest.mark.parametrize("language", EXPECTED)
def test_language_loading(language, monkeypatch):
    """Confirma traduções carregadas em execução, restaurando o estado global no fim."""
    monkeypatch.setattr(builtins, "_", lambda text: text, raising=False)
    monkeypatch.setattr(i18n, "_current_language", None)
    assert i18n.setup_i18n(language) == language
    for source, translated in EXPECTED[language].items():
        assert builtins.__dict__["_"](source) == translated


def test_missing_catalog_uses_original_strings(monkeypatch):
    """Um idioma não registado usa português e mantém o código ativo coerente."""
    monkeypatch.setattr(builtins, "_", lambda text: text, raising=False)
    monkeypatch.setattr(i18n, "_current_language", None)
    i18n.setup_i18n("zz_ZZ")
    assert i18n.get_current_language() == "pt_PT"
    assert builtins.__dict__["_"]("Abrir") == "Abrir"


@pytest.mark.parametrize("language", [None, "", "   ", "en-US"])
def test_empty_language_and_separator_use_system_or_registered_code(language, monkeypatch):
    """Uma preferência vazia usa o sistema e um código regional normaliza o separador."""
    monkeypatch.setattr(builtins, "_", lambda text: text, raising=False)
    monkeypatch.setattr(i18n, "_current_language", None)
    monkeypatch.setattr(i18n, "_get_system_language", lambda: "en_US")
    assert i18n.setup_i18n(language) == "en_US"
    assert i18n.get_current_language() == "en_US"
    assert builtins.__dict__["_"]("Iniciar") == "Start"


def test_missing_registered_catalog_reports_portuguese(tmp_path, monkeypatch):
    """Sem ficheiros de tradução, o idioma efetivo e as mensagens são portugueses."""
    monkeypatch.setattr(builtins, "_", lambda text: text, raising=False)
    monkeypatch.setattr(i18n, "_current_language", None)
    monkeypatch.setattr(i18n, "LOCALE_DIR", tmp_path)
    assert i18n.setup_i18n("en_US") == "pt_PT"
    assert i18n.get_current_language() == "pt_PT"
    assert builtins.__dict__["_"]("Iniciar") == "Iniciar"


def test_corrupt_catalog_falls_back_without_misleading_selector(tmp_path, monkeypatch):
    """Um MO inválido não mantém o nome do idioma cuja tradução falhou."""
    catalog = tmp_path / "en_US" / "LC_MESSAGES" / "chronometer.mo"
    catalog.parent.mkdir(parents=True)
    catalog.write_bytes(b"invalid mo")
    monkeypatch.setattr(builtins, "_", lambda text: text, raising=False)
    monkeypatch.setattr(i18n, "_current_language", None)
    monkeypatch.setattr(i18n, "LOCALE_DIR", tmp_path)
    assert i18n.setup_i18n("en_US") == "pt_PT"
    assert i18n.get_current_language() == "pt_PT"


def _fields(text: str) -> set[str]:
    """Extrai os nomes dos marcadores usados por str.format."""
    return {name for _literal, name, _spec, _conversion in Formatter().parse(text) if name is not None}


def test_catalogs_cover_source_and_keep_placeholders():
    """O modelo e cada idioma contêm todas as mensagens e conservam os marcadores."""
    messages = set(extract_messages(PROJECT_DIR))
    template = polib.pofile(str(PROJECT_DIR / "i18n" / "chronometer.pot"))
    assert {entry.msgid for entry in template if not entry.obsolete} == messages
    languages = ConfigManager.LANGUAGE_NAMES
    assert {path.stem for path in (PROJECT_DIR / "i18n").glob("*.po")} == set(languages)
    for language in languages:
        catalog = polib.pofile(str(PROJECT_DIR / "i18n" / f"{language}.po"))
        assert {entry.msgid for entry in catalog if not entry.obsolete} == messages
        assert not catalog.fuzzy_entries()
        assert not catalog.untranslated_entries()
        for entry in catalog.translated_entries():
            assert _fields(entry.msgid) == _fields(entry.msgstr)


def test_add_language_preserves_existing_translation(tmp_path, monkeypatch):
    """Registar um idioma permite criar, traduzir, compilar e carregar o novo catálogo."""
    (tmp_path / "i18n").mkdir()
    (tmp_path / "i18n" / "__init__.py").write_text('', encoding="utf-8")
    (tmp_path / "sample.py").write_text('_("Abrir")\n_("Fechar")\n', encoding="utf-8")
    monkeypatch.setattr(ConfigManager, "LANGUAGE_NAMES", {"es_ES": "Español"})
    update_catalogs(tmp_path)
    path = tmp_path / "i18n" / "es_ES.po"
    catalog = polib.pofile(str(path))
    catalog.find("Abrir").msgstr = "Abrir en español"
    catalog.find("Fechar").msgstr = "Cerrar"
    catalog.save(str(path))
    update_catalogs(tmp_path)
    assert polib.pofile(str(path)).find("Fechar").msgstr == "Cerrar"
    compile_catalogs(tmp_path / "i18n")
    monkeypatch.setattr(i18n, "LOCALE_DIR", tmp_path / "i18n" / "locales")
    monkeypatch.setattr(builtins, "_", lambda text: text, raising=False)
    monkeypatch.setattr(i18n, "_current_language", None)
    i18n.setup_i18n("es_ES")
    assert builtins.__dict__["_"]("Fechar") == "Cerrar"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
