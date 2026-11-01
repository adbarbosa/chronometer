"""Extrai mensagens literais do código e atualiza os catálogos sem ferramentas externas."""

import ast
from pathlib import Path
import sys

import polib

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from chronometer import __version__  # pylint: disable=wrong-import-position
from chronometer.config import ConfigManager  # pylint: disable=wrong-import-position

PROJECT_DIR = Path(__file__).resolve().parent.parent


def extract_messages(project_dir: Path) -> dict[str, list[tuple[str, str]]]:
    """Recolhe chamadas _(texto literal) nos módulos da aplicação, excluindo testes e build."""
    sources = sorted(
        path for path in project_dir.glob("*.py")
        if not path.name.startswith("test_") and path.name not in {"conftest.py", "build.py"}
    )
    sources.append(project_dir / "i18n" / "__init__.py")
    messages: dict[str, list[tuple[str, str]]] = {}
    for path in sources:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "_":
                continue
            if len(node.args) != 1 or not isinstance(node.args[0], ast.Constant):
                raise ValueError(f"{path.name}:{node.lineno}: _() exige uma mensagem literal.")
            message = node.args[0].value
            if not isinstance(message, str) or not message:
                raise ValueError(f"{path.name}:{node.lineno}: mensagem inválida em _().")
            occurrence = (path.relative_to(project_dir).as_posix(), str(node.lineno))
            messages.setdefault(message, []).append(occurrence)
    return messages


def update_catalogs(project_dir: Path = PROJECT_DIR) -> None:
    """Recria o modelo e funde mensagens nos idiomas registados, preservando traduções."""
    i18n_dir = project_dir / "i18n"
    template = polib.POFile()
    template.metadata = {
        "Project-Id-Version": f"Chronometer {__version__}",
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
    }
    for message, occurrences in sorted(extract_messages(project_dir).items()):
        template.append(polib.POEntry(msgid=message, occurrences=sorted(occurrences)))
    template.save(str(i18n_dir / "chronometer.pot"))
    for language in ConfigManager.LANGUAGE_NAMES:
        path = i18n_dir / f"{language}.po"
        catalog = polib.pofile(str(path)) if path.exists() else polib.POFile()
        catalog.merge(template)
        catalog.metadata.update(template.metadata)
        catalog.metadata["Language"] = language
        catalog.save(str(path))
        print(f"Atualizado {path.name}: {len(catalog.translated_entries())} mensagens traduzidas.")


if __name__ == "__main__":
    update_catalogs()
