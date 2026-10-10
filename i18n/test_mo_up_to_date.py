"""Garante que os ficheiros .mo versionados correspondem aos respetivos .po."""

from pathlib import Path

import polib
import pytest

I18N_DIR = Path(__file__).resolve().parent
LANGUAGES = sorted(path.stem for path in I18N_DIR.glob("*.po"))


def _translations(catalog) -> dict:
    """Devolve {msgid: msgstr} das entradas traduzidas (exclui o cabeçalho)."""
    return {
        entry.msgid: entry.msgstr
        for entry in catalog
        if entry.msgid and entry.msgstr
    }


def test_languages_found():
    """Deve existir pelo menos um .po para verificar."""
    assert LANGUAGES


@pytest.mark.parametrize("lang", LANGUAGES)
def test_mo_matches_po(lang):
    """O .mo tem de existir e ter as mesmas traduções do .po."""
    mo_path = I18N_DIR / "locales" / lang / "LC_MESSAGES" / "chronometer.mo"
    assert mo_path.exists(), f"Falta {mo_path}; corra: python i18n/compile.py"

    po = polib.pofile(str(I18N_DIR / f"{lang}.po"))
    mo = polib.mofile(str(mo_path))
    assert _translations(mo) == _translations(po), (
        f"{lang}: .mo desatualizado; corra: python i18n/compile.py"
    )
