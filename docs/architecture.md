# How Chronometer works

This guide explains the application to a developer who has not used Qt or this repository before. For installation commands, start with [Contributing](../CONTRIBUTING.md). For button behavior, use the [user guide](../README.md#use-the-timer).

## The main idea

Qt runs an **event loop**: it waits for events such as a button click, a display change or a timer notification, then calls the connected Python function. A connection between an event and a function is called a **signal/slot connection**.

Chronometer has one `QApplication`, one control panel (`MainWindow`) and one output (`TimerWindow`). The control panel coordinates actions. Its `Countdown` object owns the countdown state. A `DisplayManager` reads available monitors and places the output. The output displays a reading sent by the panel; it never subtracts time independently.

```text
__main__.py -> app.main()
                 |
                 +-> configuration -> language setup -> QApplication
                                                          |
                                                       MainWindow
                                                          |
                         +--------------------------------+------------------+
                         |                                |                  |
                     Countdown                     DisplayManager       TimerWindow
                    measures time                   selects screen      renders time
```

There is no server, database or network connection involved in timing. Opening the project website delegates to the operating system's browser.

## Repository layout

The root folder is the `chronometer` Python package. It must keep that name. There is no `pyproject.toml` or editable pip installation at present.

```text
chronometer/
├── __init__.py           # Authoritative version: 0.6.0
├── __main__.py           # Direct/module entry point
├── app.py                # Language, QApplication and platform startup
├── countdown.py          # Pure countdown state and monotonic timing
├── main_window.py        # Controls, events and output coordination
├── compact_widgets.py    # Ellipsis when drawing; full text and tooltips retained
├── timer_window.py       # Audience countdown, clock and attention effect
├── about_dialog.py       # Project information, using the panel's theme
├── theme.py              # Palettes, dimensions and stylesheet builders
├── config.py             # JSON preferences and safe replacement
├── displays.py           # Monitor snapshot, identity, selection and placement
├── windows_displays.py   # Native Windows monitor interfaces
├── resources.py          # Source/frozen resource root
├── icon_manager.py       # Shared icon loading
├── build.py              # Supported PyInstaller build
├── smoke_check.py        # Isolated executable startup and bundle-content check
├── conftest.py           # Isolated Qt test fixtures
├── test_*.py             # Countdown, UI, preferences and resource tests
├── i18n/                 # Translation runtime, tools, catalogs and tests
├── icon/                 # SVG and ICO artwork
├── docs/                 # Technical guides, validation and screenshots
├── .github/workflows/    # Linux/Windows checks, builds and startup smoke checks
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

`MainWindow` keeps a reference to one `TimerWindow`. Hiding the output leaves the model and its update timer running. The output can be shown again without restarting the countdown. Closing the panel stops its timers, closes the output and ends the application session.

Application-wide monitor signals are connected to bound Qt slots on the panel, so destroying that receiver disconnects the callbacks. The panel's destruction also schedules the output for deletion. Test fixtures explicitly dispose of both windows and process deferred deletion events before restoring their temporary state; closing a window alone does not necessarily destroy its Qt object.

The smaller clock label handles mouse clicks and hides the output. The large countdown label does not have that behavior. Output show/hide events emit a visibility signal. The panel uses that signal to rebuild its status text, so clicking the clock or closing the output through the window system cannot leave an incorrect “Opened in…” message.

The pending monitor-list selection and the identity of the currently opened monitor are stored separately. Changing the selector does not claim that an already visible output has moved. Refreshing the list or changing language also rebuilds the status from the real output state.

The attention effect has its own Qt timer, with interval and event limit in `theme.py`. It alternates background/contrast colors and restores the normal background at the end. Start and Reset also stop the effect. The ordinary output background is black in both themes.

The output keeps its normal time-warning color separately from the active flash phase. One rendering method combines those states whenever time, flash or size changes. A countdown update therefore cannot replace the black text required on a white flash background with ordinary white timer text.

## Monitors and identity

`DisplayManager` in `displays.py` reads Qt's list of `QScreen` objects and a native Windows provider. Its `refresh()` method creates a snapshot of `DisplayInfo` records, each containing the Qt screen, saved identity, display name and description. These providers can be replaced in tests without calling physical display APIs.

An index is a position in the list, and can change when screens are reconnected. Chronometer therefore saves an identity where possible:

1. On Windows, match the Qt screen name to its GDI adapter name and use the native monitor interface identity.
2. Otherwise, combine available serial number, manufacturer, model and screen name.
3. If metadata is unavailable, use position and dimensions.
4. When metadata matches more than one Qt screen, append geometry to distinguish them.

At startup, selection tries the saved identity, then a valid legacy saved index, then the second available screen, then the first. With no screens, `preferred_index()` returns `-1`, leaving no selection. The index API is retained for older preference files; opening an output now saves the identity.

`open_output()` refreshes the snapshot once and resolves the selected identity. If it is gone, the method returns `None` without moving or showing the window, and the panel refreshes the selector. Otherwise it explicitly calls `setScreen()` before setting the position and requesting full-screen display. When an already full-screen output changes screens, it first hides the output and clears the old full-screen state. These operations do not change the countdown.

Explicit screen association matters on Wayland, where a compositor can ignore manual window coordinates. Coordinates remain a placement hint on systems that support them; selecting a `QScreen` does not remove the need to test the intended compositor and hardware. Screen-added and screen-removed signals refresh the list; removal of a visible output's screen triggers an attempt to reopen on an available selection.

On Windows, `EnumDisplayDevicesW` enumerates all monitor indexes under each active, non-mirroring adapter. Monitor queries pass `EDD_GET_DEVICE_INTERFACE_NAME` (`0x00000001`) to populate `DeviceID` with the registered monitor interface. The code does not use the reserved `DeviceKey` as an identity. An active adapter with no enumerated monitor receives a name-based fallback.

Several physical monitors can share one GDI output, for example in a cloned display arrangement. In that case, matching native entries are combined into an order-independent identity and description. A clone group still corresponds to one Qt screen; the app cannot select its physical members independently.

The native structures and calls remain guarded by `sys.platform == 'win32'`. Linux returns no native Windows displays unless a simulated provider is supplied by a test. Simulated selection/placement tests do not establish real Windows API or compositor behavior.

## Preference storage

`ConfigManager.CONFIG_DIR` and `CONFIG_FILE` are evaluated at import time. Normally the folder is `Path.home() / '.chronometer'`. The optional `CHRONOMETER_CONFIG_DIR` environment variable replaces that folder for isolated runs; set it before starting the process.

Reads combine a valid JSON object with defaults, preserving unknown keys. Missing files, malformed JSON and read errors use defaults. Known fields are normalized before they reach the interface:

| Field | Accepted value and fallback |
|---|---|
| `last_monitor_index` | Nonnegative integer, integral finite number or legacy decimal text. Booleans, fractions, non-finite numbers and negative values use the default index. |
| `last_monitor_id` | Non-empty trimmed string, otherwise `None`. |
| `language` | Trimmed registered code; hyphens are normalized to underscores. Blank, unsupported or wrongly typed values become `None`, meaning automatic detection. |
| `dark_mode` | A boolean, otherwise the default theme. |

All public `save*()` methods return a boolean result. A save creates the directory if needed, then obtains a `QLockFile` named `config.json.lock` in that directory. The lock covers the complete read–alter–write transaction, not just final replacement. Another process waits at most 250 milliseconds; if the lock cannot be acquired, that save returns `False` instead of blocking the presentation indefinitely.

The lock holder reads the latest preferences, updates and normalizes them, and writes a uniquely named temporary file such as `.config.json.<random>.tmp` beside the destination. It flushes Python's buffer, asks the OS to flush with `fsync`, closes the temporary file and replaces the original with `os.replace`. Each writer owns its temporary file, so two processes cannot truncate each other's in-progress JSON. A failed write or replacement leaves the previous final file in place and attempts to clean up only that writer's temporary file. The lock is released in a `finally` block.

The panel reports a failed preference save through a short nonmodal status-bar message, while leaving the countdown usable. Portuguese diagnostics also go to the terminal. The lock and unique temporary files support multiple app instances; they do not synchronize their live UI settings, and two saves of the same preference still use the last successful value. No active timer session is stored.

## Translation flow

Gettext maps each literal original message to its translated form. `ConfigManager.LANGUAGE_NAMES` supplies the language selector and maintenance tools; `SUPPORTED_LANGUAGES` is derived at import time.

Automatic detection normalizes Portuguese variants to `pt_PT` and English variants to `en_US`. Only registered codes are applied. An unknown system code uses the default Portuguese language. A blank request uses system detection; a blank or unsupported saved preference has already been normalized to that automatic choice by `ConfigManager`.

`setup_i18n()` tries the requested registered catalog. If it is missing or invalid, it tries the default Portuguese catalog, then uses original Portuguese strings if no catalog can be loaded. Its return value and `get_current_language()` are the effective registered language, so the selector stays consistent with the applied fallback. Individual missing messages within an otherwise valid catalog can still fall back to their original strings; catalog-completeness tests prevent that in maintained production catalogs.

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

The control panel has a fixed configured size of 400 × 550. The preset grid has three rows and four columns, with these minute values from left to right: `1, 2, 3, 4`; `5, 10, 15, 20`; `25, 30, 45, 60`. The compact layout uses smaller margins and button padding while retaining the main text sizes. The footer places the language selector and theme button on the left. On the right, the date sits above the clock, with both labels right-aligned. These local date/time labels are independent of countdown state.

`compact_widgets.py` provides `ElidingComboBox` and `ElidingLabel`. They shorten long monitor names and output-status text with an ellipsis only when drawing. Tooltips retain the complete text. Full monitor labels and identity data remain available to selection and placement logic, so fitting the panel must not change monitor identity or confuse the pending selection with the actual open output.

The About dialog has a configured minimum size and can accommodate more text. Output fonts scale with the output's dimensions. Native window decorations and font substitution remain platform-dependent; the operating system's borders are additional to the configured panel size.

## Resources and executable layout

`resource_path()` returns paths under the repository root when running source, or under `sys._MEIPASS` when frozen by PyInstaller. The latter is the temporary extraction root for the bundled data. Icons and translations use this common helper. Icon loading tries a valid ICO, then a valid SVG, and returns an empty icon only if neither can be read.

`build.py` adds the repository's parent as an analysis import path, bundles `icon/`, `i18n/locales/` and `chronometer.desktop`, and generates its specification under `build/`. The legacy root specification is not loaded or regenerated by this process.

`smoke_check.py` verifies the packaged icons and translation bytes, then launches the executable from a temporary working directory with isolated preferences and the `offscreen` backend. It checks startup only, not physical display placement or interactive controls. See [Distribution](distribution.md) for the actual commands and verification procedure.
