# Chronometer

**Version:** 0.5.0

A timer for presentations and talks, with a control panel and an output window for a second monitor. Supports multiple languages (pt-PT, en-US).

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Running](#running)
- [Building the Executable](#building-the-executable)
- [Internationalization (i18n)](#internationalization-i18n)
- [Customization](#customization)
- [License](#license)

## Features

- **Duration presets** — 1 to 5 minutes, followed by 10, 15, 20, 25, 30, 45, and 60 minutes
- **Manual duration** — editable field with +/- buttons (1 to 180 minutes)
- **Color-coded visual warnings** — white (normal), orange (< 1 min), red (< 0 min)
- **Call Attention** — red/white flashing effect on the second monitor
- **Monitor selection** — lists all connected monitors and lets you choose where to show the output
- **Dark / Light mode** — switch with one click
- **Responsive text** — the timer and clock adapt to the monitor resolution
- **Close output by clicking the time** — hides the window without closing the application
- **Internationalization** — supports Portuguese (Portugal) and English (United States)
- **Help menu** — access to project information and the GitHub link

## Requirements

### Runtime
- Python 3.10+
- PyQt6

### Development (Translations and Build)
- polib (translation compilation)
- pytest (test execution)
- pyinstaller or nuitka (executable builds)

### Installation
```bash
# Runtime only
python3 -m pip install PyQt6

# Full development setup (including translations and builds)
python3 -m pip install PyQt6 polib pyinstaller pytest
```

On Windows, you can use `py -3 -m pip` instead of `python3 -m pip`.

## Project Structure

```
chronometer/
├── __init__.py              # Package marker (v0.4.2)
├── __main__.py              # Entry point (python -m chronometer)
├── app.py                   # Creates QApplication, sets up i18n
├── main_window.py           # Control panel + Help menu
├── about_dialog.py          # About Chronometer dialog (v0.4.2)
├── timer_window.py          # Output window (second monitor)
├── theme.py                 # Colors, fonts, sizes, stylesheets
├── i18n/                    # Internationalization
│   ├── __init__.py          # setup_i18n() - gettext configuration
│   ├── compile.py           # .po → .mo compiler (uses polib)
│   ├── chronometer.pot      # Translation template
│   ├── pt_PT.po             # Portuguese (Portugal)
│   ├── en_US.po             # English (United States)
│   ├── test_i18n.py         # i18n tests
│   └── locales/             # Compiled (generated)
│       ├── pt_PT/LC_MESSAGES/chronometer.mo
│       └── en_US/LC_MESSAGES/chronometer.mo
├── icon/
│   ├── chronometer-stopwatch-svgrepo-com.svg  # Original asset
│   └── chronometer-stopwatch-svgrepo-com.ico  # Icon for Windows/PyInstaller
└── ...
```

## Running

The following instructions assume that the code was obtained in a directory containing the `chronometer/` directory.
Python 3.10 or later and PyQt6 are required.

### Linux

```bash
cd /path/to/directory-containing-chronometer
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install PyQt6
python3 -m chronometer
```

### Windows

```cmd
cd C:\path\to\directory-containing-chronometer
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install PyQt6
py -3 -m chronometer
```

> **Note:** `python3 -m chronometer` or `py -3 -m chronometer` must be run from the directory that **contains** the `chronometer/` directory, not from inside it.

For direct execution during debugging, you can also run the following from inside the `chronometer/` directory:

```bash
python3 __main__.py
```

## Building the Executable

To build the application correctly and ensure that all resources (icons, translations, and the desktop file) are included, use the provided `build.py` script.
The official process does not use the `Chronometer.spec` file.

### Step 1: Set up the environment

**Important:** All commands must be run **inside** the `chronometer/` directory.

```bash
# Linux
cd /path/to/directory-containing-chronometer/chronometer
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install PyQt6 polib pyinstaller

# Windows (CMD)
cd C:\path\to\directory-containing-chronometer\chronometer
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install PyQt6 polib pyinstaller
```

### Windows (Git Bash / MINGW64)

In Git Bash, use `/` in paths and `source` to activate the virtual environment:

```bash
cd /path/to/directory-containing-chronometer/chronometer
py -3 -m venv .venv
source .venv/Scripts/activate
py -3 -m pip install PyQt6 polib pyinstaller
```

### Step 2: Compile translations

This step is only required when the `.po` files have changed. It must be run from inside the `chronometer/` directory:

```bash
python3 i18n/compile.py
```

On Windows:

```cmd
py -3 i18n\compile.py
```

### Step 3: Generate the executable

From inside the `chronometer/` directory, run:

```bash
python3 build.py
```

On Windows:

```cmd
py -3 build.py
```

The executable will be created in the `dist/` directory:

- Linux: `dist/Chronometer`
- Windows: `dist/Chronometer.exe`

The script automatically includes the `.mo` files, icons, and `chronometer.desktop` file present at build time.

### Platform and architecture limitation

PyInstaller does not perform cross-compilation. The executable is generated for the operating system and architecture of the Python environment where the build is run. For example, a build made on Windows generates a Windows executable and a build made on Linux generates a Linux executable; to provide both versions, the build must be run on each target operating system and architecture.

### Run the executable

On Linux:

```bash
./dist/Chronometer
```

On Windows:

```cmd
dist\Chronometer.exe
```

The build must be run on the target operating system. The `Chronometer.spec` file contains locally generated configuration and is not used by the official process.

## Configuration

Preferences are stored in `~/.chronometer/config.json`:

| Key | Values | Default |
|---|---|---|
| `last_monitor_index` | Integer monitor index | `1` |
| `language` | `pt_PT`, `en_US`, or `null` | `null` |
| `dark_mode` | `true` or `false` | `false` |

The monitor index is validated at startup, and a fallback is used when the saved monitor no longer exists.

Tests use a temporary directory and should not modify this file.

## Internationalization (i18n)

How Translations Work

- **Automatic detection:** The application detects the system language via `locale.getdefaultlocale()`
- **Fallback:** If the language is not supported, it falls back to pt_PT
- **Initialization:** In `app.py`, `setup_i18n()` is called before creating the UI

### Supported Languages

- **pt_PT** — Portuguese (Portugal) [default]
- **en_US** — English (United States)

### Add a New Language

1. **Create a new PO file:**
   ```bash
   cp chronometer/i18n/chronometer.pot chronometer/i18n/xx_YY.po
   ```
   Replace `xx_YY` with the language code (e.g. `pt_BR`, `es_ES`, `fr_FR`)

2. **Translate strings in the `.po` file:**
   - Open it with Poedit, Lokalize, or a text editor
   - Fill in `msgstr` with the translation for each `msgid`
   - Example:
     ```po
     msgid "Open"
     msgstr "Open"
     ```

3. **Compile translations:**
   ```bash
   cd chronometer
   python3 i18n/compile.py
   ```
   This generates `.mo` files in `i18n/locales/{xx_YY}/LC_MESSAGES/chronometer.mo`

4. **Test:**
      ```bash
   LANG=xx_YY.UTF-8 python3 -m chronometer
   ```

### Key Files

- `chronometer/i18n/__init__.py` — `setup_i18n(lang)` configures gettext
- `chronometer/i18n/compile.py` — Compiles `.po` → `.mo` using polib
- `chronometer/i18n/test_i18n.py` — Tests whether translations load correctly

Messages with variable values use placeholders, such as `{count}` and `{monitor_name}`. The template must be translated before applying `.format()`.

## Tests

From the project root:

```bash
python test_config.py
PYTHONPATH=.. python i18n/test_i18n.py
```

When `pytest` is installed, tests can be discovered from the parent package root:

```bash
PYTHONPATH=.. pytest -q
```

## Installation Using the Desktop File (Linux)

The `chronometer.desktop` file assumes that the `Chronometer` executable is available in the `PATH`.

For a per-user installation:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications ~/.local/share/icons/hicolor/scalable/apps
cp dist/Chronometer ~/.local/bin/Chronometer
cp chronometer.desktop ~/.local/share/applications/
cp icon/chronometer-stopwatch-svgrepo-com.svg ~/.local/share/icons/hicolor/scalable/apps/
chmod +x ~/.local/bin/Chronometer
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

If `~/.local/bin` is not in the `PATH`, change `Exec` in the desktop file to the executable's absolute path.

The desktop file and icon are not installed automatically by the build.

## Contributing

1. Create and activate a virtual environment.
2. Install the runtime and development dependencies.
3. Run the tests before and after making changes.
4. When changing translatable text, update the `.po` files and recompile the `.mo` files.
5. Validate the build on the target operating system.
6. Keep changes focused and update the README when behavior changes.

## Known Issues

- The countdown continues to show negative time after `00:00` until it is stopped manually.
- The PyInstaller build must be run on the target operating system.
- On Linux, PyInstaller ignores the `.ico` parameter as the executable icon; visual integration depends on the `.desktop` file and icon installation.
- The output window requires a graphical session, and multi-monitor behavior depends on Qt, the compositor, and the X11/Wayland session.
- The `libtiff.so.5` warning may appear during the build when that library is not installed on the system.

## Customization

All colors, fonts, sizes, and timings can be adjusted in `chronometer/theme.py`:

| Variable | Description |
|---|---|
| `LIGHT` / `DARK` | Theme color palettes |
| `OUTPUT` | Output window colors |
| `FONT` | Font sizes |
| `OUTPUT_TIMER_H_RATIO` | Output timer scale (% of height) |
| `OUTPUT_TIMER_W_RATIO` | Output timer scale (% of width) |
| `OUTPUT_CLOCK_RATIO` | Clock scale (% of timer) |
| `TIME_WARN_SECS` | Orange warning threshold (default: 300s) |
| `TIME_DANGER_SECS` | Red warning threshold (default: 120s) |

## License

This project is free to use.
