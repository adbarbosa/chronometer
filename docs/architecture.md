# How Chronometer works

This guide explains the application to a developer who has not used Qt or this repository before. For installation commands, start with [Contributing](../CONTRIBUTING.md). For button behavior, use the [user guide](../README.md#use-the-timer).

## The main idea

Qt runs an **event loop**: it waits for events such as a button click, a display change or a timer notification, then calls the connected Python function. A connection between an event and a function is called a **signal/slot connection**.

Chronometer has one `QApplication`, one control panel (`MainWindow`) and one output (`TimerWindow`). The control panel coordinates actions. Its `Countdown` object owns the countdown state. The output displays a reading sent by the panel; it never subtracts time independently.

```text
__main__.py -> app.main()
                 |
                 +-> configuration -> language setup -> QApplication
                                                          |
                                                       MainWindow
                                                       /        \
                                                  Countdown   TimerWindow
                                                       \        /
                                                     same reading
```

There is no server, database or network connection involved in timing. Opening the project website delegates to the operating system's browser.

## Repository layout

The root folder is the `chronometer` Python package. It must keep that name. There is no `pyproject.toml` or editable pip installation at present.

```text
chronometer/
├── __init__.py           # Authoritative version: 0.5.0
├── __main__.py           # Direct/module entry point
├── app.py                # Language, QApplication and platform startup
├── countdown.py          # Pure countdown state and monotonic timing
├── main_window.py        # Controls, events and output coordination
├── timer_window.py       # Audience countdown, clock and attention effect
├── about_dialog.py       # Project information, using the panel's theme
├── theme.py              # Palettes, dimensions and stylesheet builders
├── config.py             # JSON preferences and safe replacement
├── windows_displays.py   # Native Windows monitor metadata
├── resources.py          # Source/frozen resource root
├── icon_manager.py       # Shared icon loading
├── build.py              # Supported PyInstaller build
├── conftest.py           # Isolated Qt test fixtures
├── test_*.py             # Countdown, UI, preferences and resource tests
├── i18n/                 # Translation runtime, tools, catalogs and tests
├── icon/                 # SVG and ICO artwork
├── docs/                 # Technical guides, validation and screenshots
├── .github/workflows/    # Linux Pylint and pytest configuration
├── chronometer.desktop   # Linux launcher metadata
└── Chronometer.spec      # Legacy generated artifact; not a build input
```

Generated files under `build/` and `dist/` are ignored by Git. The compiled translation files under `i18n/locales/` are intentionally versioned.

## Startup order

1. `__main__.py` makes the package importable when run directly and calls `app.main()`.
2. `ConfigManager` reads the saved language, or returns its default.
3. `setup_i18n()` selects a gettext catalog and installs `_` in Python's `builtins` namespace. This makes `_('Mensagem')` available across UI modules.
4. `app.main()` applies the Windows taskbar application ID when applicable, creates `QApplication`, sets the name, version and icon, and sets the Linux desktop-file identity to `chronometer`.
5. `MainWindow` creates a stopped ten-minute `Countdown`, loads the theme, creates the output and constructs the controls.
6. It fills the monitor list, restores a selection and updates both timer labels. Only the control panel is shown initially.
7. `app.exec()` starts handling events.

Create UI objects only after translation setup and a `QApplication` exist. Importing a UI class does not by itself construct its widgets.

## Countdown state and time

`Countdown` has a loaded duration in seconds, accumulated elapsed time and, while running, the last start time. The clock is `time.monotonic`, which measures elapsed time independently of changes to the calendar clock. Tests can provide their own clock function.

The visible remaining time is the loaded duration minus the number of complete elapsed seconds. Fractions are retained internally across pauses. A delayed notification asks for a fresh reading; it does not subtract just one second and lose the missed interval.

| Operation | State change |
|---|---|
| Construction | Loads the duration and stays stopped. |
| `load(seconds)` | Replaces the duration and resets to stopped. Negative input is rejected. |
| `start()` | Starts or resumes. An expired positive loaded duration is reset first. Repeated Start while still positive keeps progress. |
| `pause()` | Accumulates elapsed time and stops measuring until the next Start. |
| `reset()` | Clears elapsed time and stops, keeping the loaded duration. |

`MainWindow.remaining_seconds` and `loaded_preset_seconds` are read-only views of that model. A Qt `QTimer` prompts the panel to repaint approximately every second. `_update_displays()` takes **one** remaining-time reading and uses it for both windows, avoiding a second-boundary mismatch.

The local clock and date use `QDateTime` separately. They do not determine countdown progress. The monotonic design avoids accumulating delayed events; it does not make Qt a real-time system or guarantee identical suspension behavior across operating systems.

## Window lifetime and attention

`MainWindow` keeps a reference to one `TimerWindow`. Hiding the output leaves the model and its update timer running. The output can be shown again without restarting the countdown. Closing the panel closes the output and the application session.

The smaller clock label handles mouse clicks and hides the output. The large countdown label does not have that behavior.

The attention effect has its own Qt timer, with interval and event limit in `theme.py`. It alternates background/contrast colors and restores the normal background at the end. Start and Reset also stop the effect. The ordinary output background is black in both themes.

## Monitors and identity

Qt supplies its list of `QScreen` objects. An index is a position in that list, and can change when screens are reconnected. Chronometer therefore saves an identity where possible:

1. On Windows, match the Qt screen name with metadata read through `EnumDisplayDevicesW`; use the native identifier.
2. Otherwise, combine available serial number, manufacturer, model and screen name.
3. If metadata is unavailable, use position and dimensions.
4. When metadata matches more than one Qt screen, append geometry to distinguish them.

At startup, selection tries the saved identity, then the legacy saved index, then the second available screen, then the first. The index API is retained for older preference files; opening an output now saves the identity.

Open moves the output to the selected screen's top-left position and requests full-screen display. Qt and the desktop compositor determine the final placement. Screen-added and screen-removed signals refresh the list; removal of a visible output's screen triggers an attempt to reopen on an available selection.

The Windows API structures and calls are guarded by `sys.platform == 'win32'`. Linux returns no native Windows displays. Simulated metadata tests cannot establish real Windows API behavior or compositor behavior.

## Preference storage

`ConfigManager.CONFIG_DIR` and `CONFIG_FILE` are evaluated at import time. Normally the folder is `Path.home() / '.chronometer'`. The optional `CHRONOMETER_CONFIG_DIR` environment variable replaces that folder for isolated runs; set it before starting the process.

Reads combine a valid JSON object with defaults, preserving unknown keys. Missing files, malformed JSON and read errors use defaults. The theme getter accepts a boolean; the language getter accepts a string or uses automatic detection. Other getters perform their own checks, such as integer conversion for the legacy index.

Writes create the folder if needed, write `config.json.tmp`, flush Python's buffer, ask the OS to flush the file with `fsync`, then replace the original with `os.replace`. A failed replacement preserves the previous final file and attempts to remove the temporary file. This protects against a partial JSON write; it is not coordination between multiple running app instances.

The GUI continues after handled file-access errors, but a save may not persist. Diagnostics are printed in Portuguese. No active timer session is stored.

## Translation flow

Gettext maps each literal original message to its translated form. `ConfigManager.LANGUAGE_NAMES` supplies the language selector and maintenance tools; `SUPPORTED_LANGUAGES` is derived at import time.

Automatic detection normalizes Portuguese variants to `pt_PT` and English variants to `en_US`. Other regional codes are attempted as reported. `setup_i18n()` returns the requested/detected code even if its catalog is missing; it does not report which catalog actually supplied a translation. Missing catalogs/messages use original strings.

Changing language reinstalls `_`, updates panel controls and menu, and updates the output title. About is modal, so the panel cannot be used to change language/theme while that dialog is open; a new dialog uses the current settings.

See [Translations](translations.md) for extraction, catalog updates, registration and compilation.

## Themes and dimensions

`theme.py` contains:

- `LIGHT` / `DARK`: panel and About palettes.
- `CONTROL` / `ABOUT`: widget dimensions, margins and spacing.
- `FONT`, `FONT_FAMILY` and output sizing constants: typography.
- `OUTPUT`: audience-display colors.
- Timing and threshold constants: display updates, attention and warning limits.
- Functions producing Qt stylesheets, which are text rules similar to CSS.

The control panel has a fixed configured size. The About dialog has a configured minimum size and can accommodate more text. Output fonts scale with the output's dimensions. Native window decorations and font substitution remain platform-dependent.

## Resources and executable layout

`resource_path()` returns paths under the repository root when running source, or under `sys._MEIPASS` when frozen by PyInstaller. The latter is the temporary extraction root for the bundled data. Icons and translations use this common helper.

`build.py` adds the repository's parent as an analysis import path, bundles `icon/`, `i18n/locales/` and `chronometer.desktop`, and generates its specification under `build/`. The legacy root specification is not loaded or regenerated by this process.

See [Distribution](distribution.md) for the actual commands and verification procedure.
