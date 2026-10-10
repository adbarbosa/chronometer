# Chronometer

**Version:** 0.5.0

A timer for presentations and talks, with a control panel and an output window for a second monitor. Supports multiple languages (pt-PT, en-US).

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Getting the Code](#getting-the-code)
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

### Tools
- [Git](https://git-scm.com/) (on Windows, Git for Windows also provides **Git Bash / MINGW64**)
- Python from [python.org](https://www.python.org/downloads/) (on Windows, enable the `py` launcher during installation)

Installation of the Python packages is described step by step in [Running](#running) and [Building the Executable](#building-the-executable).

### Command conventions

Every command in this README is given for three terminals:

| Terminal | Python command (before activating the venv) | Activate the venv |
|---|---|---|
| **Linux** (bash) | `python3` | `source .venv/bin/activate` |
| **Windows CMD** | `py -3` | `.venv\Scripts\activate` |
| **Windows Git Bash / MINGW64** | `py -3` | `source .venv/Scripts/activate` |

Once the virtual environment is **active**, use plain `python` in all three terminals (`python3` does not exist on Windows). Git Bash uses `/` in paths; CMD uses `\`.

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

## Getting the Code

The project must be cloned into a directory named `chronometer`, because it is run as the `chronometer` Python package. The examples below use a `projects` folder in your home directory; the layout will be:

```
projects/
└── chronometer/     ← the repository (contains .venv/ after the setup below)
```

**Linux and Windows Git Bash:**

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://gitlab.com/adbtech-pt/python/chronometer.git chronometer
```

**Windows CMD:**

```cmd
mkdir %USERPROFILE%\projects
cd %USERPROFILE%\projects
git clone https://gitlab.com/adbtech-pt/python/chronometer.git chronometer
```

To clone over SSH instead, use `git@gitlab.com:adbtech-pt/python/chronometer.git` as the URL.

In Git Bash, `~` is your user folder (for example `/c/Users/<name>`).

To update later, from inside the `chronometer/` directory:

```bash
git pull
```

## Running

This runs the app from source, which needs Python 3.10 or later and PyQt6. First get the code (see [Getting the Code](#getting-the-code)).

### Step 1: Create the virtual environment (once)

Run this **inside** the `chronometer/` directory.

**Linux:**

```bash
cd ~/projects/chronometer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyQt6
```

**Windows CMD:**

```cmd
cd %USERPROFILE%\projects\chronometer
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install PyQt6
```

**Windows Git Bash / MINGW64:**

```bash
cd ~/projects/chronometer
py -3 -m venv .venv
source .venv/Scripts/activate
python -m pip install PyQt6
```

The prompt shows `(.venv)` while the environment is active. In a new terminal, run only the activation command again (from inside `chronometer/`).

### Step 2: Start the app

The app is a Python package, so `python -m chronometer` must be run from the directory that **contains** `chronometer/` (`projects/`), not from inside it. With the virtual environment active, in all three terminals:

```bash
cd ..
python -m chronometer
```

(In CMD, `cd ..` works the same way.)

For direct execution during debugging, from inside the `chronometer/` directory:

```bash
python __main__.py
```

## Building the Executable

To build the application correctly and ensure that all resources (icons, translations, and the desktop file) are included, use the provided `build.py` script.
The official process does not use the `Chronometer.spec` file.

### Step 1: Install the build tools

**Important:** All commands in this section must be run **inside** the `chronometer/` directory, with the virtual environment active.

If you have not created the virtual environment yet, follow [Running, Step 1](#step-1-create-the-virtual-environment-once) first (the `python -m pip install` line there is also needed). Then, with the environment active, install the build tools:

```bash
python -m pip install polib pyinstaller
```

This command is the same on Linux, Windows CMD, and Git Bash.

### Step 2: Compile translations

This step is only required when the `.po` files have changed:

```bash
python i18n/compile.py
```

This works unchanged on Linux, Windows CMD, and Git Bash (Python accepts `/` in paths on Windows).

### Step 3: Generate the executable

```bash
python build.py
```

This works unchanged on Linux, Windows CMD, and Git Bash.

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

On Windows (Git Bash):

```bash
./dist/Chronometer.exe
```

> **Note:** Windows Smart App Control may block the unsigned `.exe` (it cannot verify the publisher). If that happens, run the app from source as described in [Running](#running).

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

1. **Create a new PO file** (from inside the `chronometer/` directory):

   Linux / Git Bash:
   ```bash
   cp i18n/chronometer.pot i18n/xx_YY.po
   ```
   Windows CMD:
   ```cmd
   copy i18n\chronometer.pot i18n\xx_YY.po
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

3. **Compile translations** (virtual environment active, `polib` installed, inside `chronometer/`):
   ```bash
   python i18n/compile.py
   ```
   This generates `.mo` files in `i18n/locales/{xx_YY}/LC_MESSAGES/chronometer.mo`

4. **Test:** set `"language": "xx_YY"` in the [configuration file](#configuration), then start the app (from the directory that contains `chronometer/`):
   ```bash
   python -m chronometer
   ```
   On Linux you can also try `LANG=xx_YY.UTF-8 python -m chronometer`; this does not work on Windows, where the configuration file must be used.

### Key Files

- `chronometer/i18n/__init__.py` — `setup_i18n(lang)` configures gettext
- `chronometer/i18n/compile.py` — Compiles `.po` → `.mo` using polib
- `chronometer/i18n/test_i18n.py` — Tests whether translations load correctly

Messages with variable values use placeholders, such as `{count}` and `{monitor_name}`. The template must be translated before applying `.format()`.

## Tests

Run these from inside the `chronometer/` directory, with the virtual environment active.

**Linux and Git Bash:**

```bash
python test_config.py
PYTHONPATH=.. python i18n/test_i18n.py
```

**Windows CMD:**

```cmd
python test_config.py
set PYTHONPATH=..
python i18n/test_i18n.py
```

The two scripts above are the supported way to run the tests. Running `pytest` over the whole project currently reports an error for `i18n/test_i18n.py::test_language`, because that helper function takes a parameter that `pytest` treats as a fixture.

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
