# Agent instructions

Chronometer is a Python/PyQt6 presentation timer with a control panel and a separate audience output. Read these rules before editing. For complete setup steps and explanations, use [Contributing](CONTRIBUTING.md); for user behavior, use [README](README.md).

## Start in the right place

The repository root **is** the Python package `chronometer`. Keep that folder name. Imports use `from chronometer.config import ConfigManager`; there is no editable pip installation.

Use the existing checkout unless instructed otherwise. Inspect `git status --short` before editing and preserve unrelated work. Do not reset files, make commits, push or change the app version merely because you are implementing a task.

All commands below run from the repository root and assume its virtual environment is active. On Linux, prepare it with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

If `.venv` exists, activate it instead of recreating it. Windows CMD and Git Bash activation and interpreter commands are in [Contributing](CONTRIBUTING.md#prepare-your-environment).

## Commands

| Task | Command from the root |
|---|---|
| Interactive app | `python __main__.py` |
| Full test suite | `python -m pytest -q . --ignore=.venv` |
| Pylint, including new files | `python -m pylint "*.py" "i18n/*.py"` |
| Configuration subset | `python -m pytest -q test_config.py` |
| Translation subset | `python -m pytest -q i18n` |
| Extract messages and merge catalogs | `python i18n/update.py` |
| Compile registered translations | `python i18n/compile.py` |
| Build current platform's executable | `python build.py` |
| Check bundled resources and startup | `python smoke_check.py dist/Chronometer` (Windows: `dist/Chronometer.exe`) |
| Check whitespace | `git diff --check` |

The lint patterns cover current root and `i18n` modules. Extend them and CI if adding another Python source directory. The older `git ls-files '*.py'` command omits untracked files, so it cannot by itself validate newly created modules.

`python -m chronometer` is also supported, but only from the repository's parent directory. Avoid persistent `cd ..` steps in command sequences.

Tests default to Qt's `offscreen` backend if none is set. On Linux, an explicit invocation is `QT_QPA_PLATFORM=offscreen python -m pytest -q . --ignore=.venv`. Use a real desktop for interactive checks. For cache permission errors, see [Contributing](CONTRIBUTING.md#3-establish-a-baseline).

## Where changes belong

| Area | Files |
|---|---|
| Startup | `app.py`, `__main__.py`, `__init__.py` |
| Countdown state | `countdown.py`; coordinated by `main_window.py` |
| Controls and output | `main_window.py`, `timer_window.py`, `about_dialog.py` |
| Elided monitor and status text | `compact_widgets.py` |
| Visual values and styles | `theme.py` |
| Preferences | `config.py` |
| Display identity and placement | `displays.py`, `windows_displays.py`; coordinated by `main_window.py` |
| Icons and resource roots | `icon_manager.py`, `resources.py` |
| Translations | `i18n/`, registered in `ConfigManager.LANGUAGE_NAMES` |
| Packaging | `build.py`; generated output in `build/` and `dist/` |

Read [Architecture](docs/architecture.md) before changing state, resource lookup or platform integration.

## Preserve these contracts

- Startup loads ten minutes and remains stopped. Manual field edits take effect only after Set; choosing a preset stops and loads it.
- Keep the 400 × 550 control panel and its three rows of four presets: `1, 2, 3, 4`; `5, 10, 15, 20`; `25, 30, 45, 60` minutes. Keep the footer's language/theme controls on the left and the date above the clock, both right-aligned, on the right. Preserve the main text sizes when adjusting spacing.
- Shorten long monitor/status text only when drawing it. Preserve the full text in tooltips and underlying widget data, and preserve the selected monitor's identity.
- `Countdown` owns elapsed state. Use its monotonic reading, not the number of Qt notifications. Preserve fractional pause/resume, overtime and restart of an expired positive duration.
- Read remaining time once per display update and send that same reading to both windows. The output must not run an independent countdown. Its normal warning color must not replace the current attention contrast during time updates or resizing.
- Hiding output, including clicking its smaller clock or closing through the OS, does not pause and must update the panel status. Reset stops the countdown and attention effect. Closing the panel stops its timers and closes both windows. Destroying the panel also disposes of its output; bind application-wide signals to QObject receiver slots instead of lambdas capturing widgets.
- Initialize gettext with `setup_i18n()` before constructing UI objects that use `_()`. A `QApplication` must exist before widgets are created.
- A language change refreshes controls, menu, output title and the effective selector. Blank or invalid saved codes use automatic selection; missing/corrupt catalogs fall back to Portuguese and report that effective language. About uses the current panel theme when opened. The ordinary output remains black.
- Prefer saved monitor identity to the legacy index. Preserve native Windows identity, repeated-metadata disambiguation and missing-monitor fallback. Do not replace identity with a list index.
- Guard Windows APIs by platform. Linux tests must not execute native Windows calls.
- Preserve a unique same-directory temporary file, flush/fsync and `os.replace` for preferences. Hold QLockFile across the entire read–normalize–update–write operation with bounded wait; do not bypass it when adding save methods. Public saves return a boolean, and callers must show a nonblocking failure indication. A failed save must not truncate the last valid file.
- Do not read or modify personal preferences for tests or screenshots. Fixtures must override both `CONFIG_DIR` and `CONFIG_FILE`. For standalone experiments/build checks, set `CHRONOMETER_CONFIG_DIR` to a fresh temporary folder before starting the process.
- Use `resources.resource_path()` for bundled data. Frozen data lives under the PyInstaller extraction root, not a source working directory.

## Code and documentation conventions

- Identifiers are in English, following the existing API. Comments, docstrings, UI source messages and script diagnostics use Portuguese (Portugal).
- README, AGENTS, other repository guides and commit messages are in English. Write for a newcomer: explain prerequisites, terms, starting directory, commands, expected output and recovery steps. Keep user-facing technical detail relevant to the user's task.
- Use Python 3.10-compatible annotations such as `str | None`.
- Every module, class and named function needs a meaningful docstring, including constructors/private helpers. Pylint does not enforce every private docstring: check this convention separately.
- Put explicit visual values and stylesheet construction in `theme.py`; keep countdown durations and state in application logic.
- Keep changes focused. Fix a lint cause rather than adding suppressions or lowering checks. A local suppression requires a concrete reason, such as a Windows-only API, PyInstaller's private attribute or imports after a direct-script path adjustment.
- Use Conventional Commits if a commit is requested. Do not create commits as an automatic completion step.

## Translation workflow

Follow [Translations](docs/translations.md), including its new-language procedure.

- Wrap translatable UI text in `_()` with a non-empty literal Portuguese source message. Apply `.format()` afterwards and preserve named fields in every translation.
- Product names, technical identifiers, numeric times, developer-script diagnostics and `.desktop` metadata do not use this Python message extractor.
- `ConfigManager.LANGUAGE_NAMES` is the registration source for the selector, update tool and compiler. `SUPPORTED_LANGUAGES` is derived at import time.
- When source messages change: run `python i18n/update.py`, finish every registered PO, run `python i18n/compile.py`, then tests.
- Version `.pot`, `.po` and generated `.mo` changes together. The binaries are intentional source-controlled runtime resources.
- Documentation-only prose changes do not require regenerating translations. A version update changes translation metadata, so run the updater/compiler in that case too.

## Generated files and version

Do not manually edit `Chronometer.spec`, `build/` or `dist/`. `python build.py` generates `build/Chronometer.spec`; the root tracked specification is a legacy artifact and must remain untouched by a normal build.

The authoritative app version is `__version__` in `__init__.py`. Change it only when requested. Review the README version and architecture tree and regenerate translation metadata if a version change is requested. Do not hard-code a version into test banners. The `.desktop` entry's `Version=1.0` is a format version, not the app release.

## Completion checks and reporting

1. Run Pylint on all application and test modules: it must score **10.00/10** (`fail-under=10`).
2. Run the complete pytest command above. Add meaningful regression coverage for changed logic; do not rely solely on a smoke launch.
3. Compile translations if translatable UI messages or catalog metadata changed. Confirm coverage and MO checks pass.
4. For UI changes, inspect affected windows in both languages/themes as relevant. `offscreen` is a rendering check, not real monitor validation.
5. For packaging/resource changes, build and launch outside the checkout with temporary preferences. Verify the root tracked `.spec` is unchanged.
6. Update the appropriate user/developer/architecture guide. Check local links and follow changed command sequences literally.
7. Review `git diff`, new files and `git diff --check`. State changes, evidence and material limitations in the final response.

Use the [validation record](docs/validation.md) to distinguish automated, simulated, visual and physical checks. Local verification is on Linux; CI is configured for Linux and Windows. Do not claim Windows CMD/Git Bash, Smart App Control, native Windows display APIs or physical multi-monitor placement have been verified unless they actually were. A configured GitHub Actions matrix is not evidence of a remote run.
