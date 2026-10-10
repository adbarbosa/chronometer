# AGENTS.md

Instructions for AI coding agents working on Chronometer. Humans: see [README.md](README.md).

## Overview

Chronometer is a PyQt6 countdown timer for presentations: a control window plus an output window for a second monitor. The repository root **is** the Python package `chronometer`, so imports look like `from chronometer.config import ConfigManager`.

## Layout

- `app.py`, `__main__.py`: entry point (`python -m chronometer`).
- `main_window.py`, `timer_window.py`, `about_dialog.py`: UI.
- `theme.py`: all colors, sizes and stylesheets. Put visual values here.
- `config.py`: `ConfigManager`, JSON preferences in `~/.chronometer/config.json`.
- `windows_displays.py`, `icon_manager.py`: platform helpers.
- `i18n/`: gettext setup, `.pot`/`.po` sources, compiled `.mo` in `i18n/locales/`.
- `build.py`: PyInstaller build. Do not edit `Chronometer.spec`, `build/` or `dist/`.

## Commands

Run inside the repository root with the virtual environment active (`python -m venv .venv`, then `python -m pip install -r requirements-dev.txt`).

| Task | Command |
|------|---------|
| Run the app | `cd .. && python -m chronometer` |
| Tests | `cd .. && python -m pytest -q chronometer --ignore=chronometer/.venv` |
| Config tests | `python test_config.py` |
| Pylint | `python -m pylint $(git ls-files '*.py')` |
| Compile translations | `python i18n/compile.py` |
| Build executable | `python build.py` |

`python -m chronometer` must run from the folder that **contains** the repository. Without a display, set `QT_QPA_PLATFORM=offscreen`.

## Conventions

- Code, comments, docstrings and UI strings are in **Portuguese (pt-PT)**. README, AGENTS.md and commit messages are in **English**.
- Commits follow Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Use type hints like `str | None` (Python 3.10+).
- Every module and function needs a docstring (Pylint enforces it).
- Keep changes small and focused. Do not fix unrelated issues.

## Pylint is mandatory

`.pylintrc` sets `fail-under=10`. The code must score **10.00/10** before you finish. Fix the cause instead of adding disables; inline disables need a real reason (Windows-only code, `sys._MEIPASS`, imports after `sys.path.insert`).

## Translations

- Wrap every user-visible string in `_("...")`.
- When strings change, update `i18n/chronometer.pot` and each `i18n/*.po`, then run `python i18n/compile.py`.
- The `.mo` files **are versioned**. Commit them in the same commit as the `.po` changes. `pytest` fails if a `.mo` is stale.
- Languages are defined once in `ConfigManager.LANGUAGE_NAMES`.

## Versioning

The version lives in `__init__.py` (`__version__`) and is repeated in the README project tree. Change both together, and only when asked.

## Before finishing a task

1. `python -m pylint $(git ls-files '*.py')` gives 10.00/10.
2. `pytest` (command above) passes.
3. Translations compiled if any text changed.
4. README updated if behavior, commands or structure changed.

## Limitations

Development is done on Linux. Windows behavior (CMD, Git Bash, Smart App Control, `windows_displays.py`) is not verified by automated tests: say so instead of claiming it works.
