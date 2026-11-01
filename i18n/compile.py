"""Compila os catálogos dos idiomas registados usando polib."""

from collections.abc import Iterable
from pathlib import Path
import sys

import polib

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from chronometer.config import ConfigManager  # pylint: disable=wrong-import-position

I18N_DIR = Path(__file__).resolve().parent


def compile_po(po_path: Path, mo_path: Path) -> None:
    """Compila um PO para MO; o catálogo de origem tem de existir."""
    catalog = polib.pofile(str(po_path))
    mo_path.parent.mkdir(parents=True, exist_ok=True)
    catalog.save_as_mofile(str(mo_path))
    print(f"Compilado {po_path.name}: {len(catalog.translated_entries())} mensagens traduzidas.")


def compile_catalogs(i18n_dir: Path = I18N_DIR, languages: Iterable[str] | None = None) -> None:
    """Compila cada idioma registado ou a lista explícita usada por ferramentas e testes."""
    for language in ConfigManager.LANGUAGE_NAMES if languages is None else languages:
        compile_po(
            i18n_dir / f"{language}.po",
            i18n_dir / "locales" / language / "LC_MESSAGES" / "chronometer.mo",
        )


if __name__ == "__main__":
    try:
        compile_catalogs()
    except (OSError, ValueError) as error:
        print(f"Erro ao compilar traduções: {error}", file=sys.stderr)
        sys.exit(1)
