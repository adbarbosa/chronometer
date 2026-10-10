# Chronometer

**Version:** 0.5.0

A timer for presentations and talks, with a control panel and an output window for a second monitor. Supports multiple languages (pt-PT, en-US).

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Getting the Code](#getting-the-code)
- [Running](#running)
- [Windows shortcut](#windows-shortcut)
- [Building the Executable](#building-the-executable)
- [Configuration](#configuration)
- [Internationalization (i18n)](#internationalization-i18n)
- [Tests](#tests)
- [Installation Using the Desktop File (Linux)](#installation-using-the-desktop-file-linux)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Known Issues](#known-issues)
- [Customization](#customization)
- [License](#license)

## Features

- **Duration presets** — 1 to 5 minutes, followed by 10, 15, 20, 25, 30, 45, and 60 minutes
- **Manual duration** — editable field with +/- buttons (0 to 180 minutes, 10 by default)
- **Color-coded visual warnings** — white (normal), orange (under 1 minute left), red (overtime, below 00:00)
- **Call Attention** — red/white flashing effect on the second monitor
- **Monitor selection** — lists all connected monitors and lets you choose where to show the output
- **Dark / Light mode** — switch with one click
- **Responsive text** — the timer and clock adapt to the monitor resolution
- **Close output by clicking the time** — hides the window without closing the application
- **Internationalization** — supports Portuguese (Portugal) and English (United States)
- **Help menu** — access to project information and the project link

## Requirements

### Runtime
- Python 3.10+ (the code uses `X | None` type syntax, and CI tests 3.10, 3.11 and 3.12)
- PyQt6

### Development (translations, tests and build)
- polib (translation compilation)
- pyinstaller (executable builds)

Dependencies are listed in `requirements.txt` (runtime) and `requirements-dev.txt` (runtime plus polib, pyinstaller, pytest and pylint).

### Tools
- [Git](https://git-scm.com/) (on Windows, Git for Windows also provides **Git Bash / MINGW64**)
- Python from [python.org](https://www.python.org/downloads/) (on Windows, keep the `py` launcher enabled during installation)

### Command conventions

Every procedure in this README gives commands for three terminals:

| Terminal | Python command (before activating the venv) | Activate the venv |
|---|---|---|
| **Linux** (bash) | `python3` | `source .venv/bin/activate` |
| **Windows CMD** | `py -3` | `.venv\Scripts\activate` |
| **Windows Git Bash / MINGW64** | `py -3` | `source .venv/Scripts/activate` |

Once the virtual environment is **active** (the prompt shows `(.venv)`), use plain `python` in all three terminals (`python3` does not exist on Windows). Git Bash uses `/` in paths; CMD uses `\`.

> Commands were verified on Linux. The Windows CMD and Git Bash commands follow the same logic but were not run on Windows.

## Project Structure

The repository root is the `chronometer/` package directory:

```
chronometer/
├── __init__.py              # Package marker and __version__ (0.5.0)
├── __main__.py              # Entry point (python -m chronometer)
├── app.py                   # Creates QApplication, sets up i18n
├── main_window.py           # Control panel + Help menu
├── about_dialog.py          # About Chronometer dialog
├── timer_window.py          # Output window (second monitor)
├── config.py                # ConfigManager (JSON preferences)
├── icon_manager.py          # Application icon loading
├── windows_displays.py      # Native monitor names on Windows
├── theme.py                 # Colors, fonts, sizes, stylesheets
├── build.py                 # PyInstaller build script
├── test_config.py           # ConfigManager tests
├── .pylintrc                # Pylint configuration (fail-under=10)
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Dev dependencies (polib, pyinstaller, pytest, pylint)
├── AGENTS.md                # Instructions for AI coding agents
├── chronometer.desktop      # Linux desktop entry
├── Chronometer.spec         # Local PyInstaller output (not used by the official build)
├── i18n/                    # Internationalization
│   ├── __init__.py          # setup_i18n() - gettext configuration
│   ├── compile.py           # .po → .mo compiler (uses polib)
│   ├── chronometer.pot      # Translation template
│   ├── pt_PT.po             # Portuguese (Portugal)
│   ├── en_US.po             # English (United States)
│   ├── test_i18n.py         # i18n tests
│   ├── test_mo_up_to_date.py  # Checks each .mo matches its .po
│   └── locales/             # Compiled .mo files
│       ├── pt_PT/LC_MESSAGES/chronometer.mo
│       └── en_US/LC_MESSAGES/chronometer.mo
└── icon/
    ├── chronometer-stopwatch-svgrepo-com.svg  # Original asset
    └── chronometer-stopwatch-svgrepo-com.ico  # Icon for Windows/PyInstaller
```

## Getting the Code

The project must be cloned into a directory named `chronometer`, because it is run as the `chronometer` Python package. The examples use a `projects` folder in your home directory:

```
projects/
└── chronometer/     ← the repository (contains .venv/ after the setup below)
```

### Step 1: Clone

**Linux:**

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/adbarbosa/chronometer.git chronometer
```

**Windows CMD:**

```cmd
mkdir %USERPROFILE%\projects
cd %USERPROFILE%\projects
git clone https://github.com/adbarbosa/chronometer.git chronometer
```

**Windows Git Bash / MINGW64:**

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/adbarbosa/chronometer.git chronometer
```

In Git Bash, `~` is your user folder (for example `/c/Users/<name>`). To clone over SSH instead, use `git@github.com:adbarbosa/chronometer.git` as the URL.

Expected result: a `chronometer/` folder inside `projects/`.

### Step 2: Update later (optional)

From inside `chronometer/`, in any terminal:

```bash
git pull
```

## Running

This runs the app from source. It needs Python 3.10+ and PyQt6, and an interactive graphical session.

### Step 1: Create the virtual environment (once)

Run these **inside** the `chronometer/` directory.

**Linux:**

```bash
cd ~/projects/chronometer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**Windows CMD:**

```cmd
cd %USERPROFILE%\projects\chronometer
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

**Windows Git Bash / MINGW64:**

```bash
cd ~/projects/chronometer
py -3 -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

Expected result: the prompt starts with `(.venv)` and `python -m pip show PyQt6` lists the package. In a new terminal, run only the activation command again (from inside `chronometer/`).

### Step 2: Start the app

`python -m chronometer` must be run from the directory that **contains** `chronometer/` (here, `projects/`), not from inside it. With the virtual environment active, the same two commands work in all three terminals:

```bash
cd ..
python -m chronometer
```

Expected result: the Chronometer control window opens.

For direct execution during debugging, run this from inside the `chronometer/` directory (also the same in all three terminals):

```bash
python __main__.py
```

## Windows shortcut

To start the app without opening a terminal, create a shortcut. This avoids the unsigned `.exe` (see [Building the Executable](#building-the-executable)). It was not tested on Windows.

1. Complete [Running, Step 1](#step-1-create-the-virtual-environment-once).
2. Right-click the desktop and choose **New > Shortcut**.
3. For the location, use the `pythonw.exe` of the virtual environment (it does not open a console window), followed by the module:

   ```
   C:\Users\<name>\projects\chronometer\.venv\Scripts\pythonw.exe -m chronometer
   ```

4. Name it "Chronometer" and finish.
5. Open the shortcut's **Properties** and set **Start in** to the directory that **contains** `chronometer/` (here, `C:\Users\<name>\projects`). Without this, Python cannot find the `chronometer` package.
6. Optionally, use **Change Icon** and select `icon\chronometer-stopwatch-svgrepo-com.ico`.

## Building the Executable

To build the application correctly and ensure that all resources (icons, translations, and the desktop file) are included, use the provided `build.py` script. The official process does not use the `Chronometer.spec` file.

### Step 1: Install the build tools

Prerequisite: the virtual environment from [Running, Step 1](#step-1-create-the-virtual-environment-once), **active**, with the current directory set to `chronometer/`.

```bash
python -m pip install -r requirements-dev.txt
```

The command is the same on Linux, Windows CMD, and Git Bash.

### Step 2: Compile translations

Only required when the `.po` files have changed. From inside `chronometer/`:

```bash
python i18n/compile.py
```

Expected result: one `Compilando <lang>.po... ✓` line per language and a success message. The command is the same in all three terminals (Python accepts `/` in paths on Windows).

### Step 3: Generate the executable

From inside `chronometer/`:

```bash
python build.py
```

The command is the same in all three terminals. The script includes the `.mo` files, icons, and `chronometer.desktop` present at build time.

Expected result:

- Linux: `dist/Chronometer`
- Windows: `dist/Chronometer.exe`

`build.py` always uses this name, without version or platform. If you share builds, rename the copy yourself (for example `Chronometer-v0.5.0-windows-x64.exe`).

### Platform and architecture limitation

PyInstaller does not perform cross-compilation. The executable is generated for the operating system and architecture of the Python environment where the build is run. To provide Windows and Linux versions, run the build on each one.

### Step 4: Run the executable

**Linux:**

```bash
./dist/Chronometer
```

**Windows CMD:**

```cmd
dist\Chronometer.exe
```

**Windows Git Bash / MINGW64:**

```bash
./dist/Chronometer.exe
```

### Windows Smart App Control

The `.exe` is **not code-signed**. Windows Smart App Control (and SmartScreen) can block it with a message saying the publisher could not be verified. This is not a bug in the app: an executable without a trusted signature has no verifiable publisher.

- The reliable alternative is to run the app from source ([Running](#running)) or with a [shortcut](#windows-shortcut).
- A trusted code-signing certificate or service is required for the `.exe` to be accepted on other PCs. Self-signed certificates do not help on other computers.
- Turning Smart App Control off is not recommended; it may be impossible to turn it back on without resetting Windows.

Not tested: whether an `.exe` built locally on the same PC is blocked.

## Configuration

Preferences are stored in `config.json` inside a `.chronometer` folder in your user folder (`Path.home()`):

- Linux: `~/.chronometer/config.json`
- Windows: `C:\Users\<name>\.chronometer\config.json` (in Git Bash, `~/.chronometer/config.json`)

| Key | Values | Default |
|---|---|---|
| `last_monitor_index` | Integer monitor index | `1` |
| `last_monitor_id` | Monitor identifier or `null` | `null` |
| `language` | `pt_PT`, `en_US`, or `null` (use the system language) | `null` |
| `dark_mode` | `true` or `false` | `false` |

The monitor index is validated at startup, and a fallback is used when the saved monitor no longer exists.

Tests use a temporary directory and should not modify this file.

## Internationalization (i18n)

### How translations work

1. At startup, `app.py` reads `language` from the configuration and calls `setup_i18n()` before creating the UI.
2. If `language` is `null`, the system language is detected with Qt (`QLocale.system().name()`). `pt*` becomes `pt_PT`, `en*` becomes `en_US`, and any other language is used as is.
3. If no translation file exists for the resulting language, the original (source) strings are shown. If the system language cannot be determined at all, `pt_PT` is used.

### Supported languages

- **pt_PT** — Portuguese (Portugal) [default]
- **en_US** — English (United States)

### Add a new language

All commands run from inside the `chronometer/` directory, with the virtual environment active and `polib` installed.

1. **Create a new PO file.** Replace `xx_YY` with the language code (for example `pt_BR`, `es_ES`, `fr_FR`).

   Linux and Git Bash:

   ```bash
   cp i18n/chronometer.pot i18n/xx_YY.po
   ```

   Windows CMD:

   ```cmd
   copy i18n\chronometer.pot i18n\xx_YY.po
   ```

2. **Translate the strings** in the `.po` file with Poedit, Lokalize, or a text editor. Fill in `msgstr` for each `msgid`:

   ```po
   msgid "Open"
   msgstr "Open"
   ```

3. **Compile the translations** (same in all three terminals):

   ```bash
   python i18n/compile.py
   ```

   This generates `i18n/locales/xx_YY/LC_MESSAGES/chronometer.mo`.

4. **Test.** Set `"language": "xx_YY"` in the [configuration file](#configuration), then start the app from the directory that contains `chronometer/`:

   ```bash
   python -m chronometer
   ```

   To also make the language selectable in the app, add it to `ConfigManager.LANGUAGE_NAMES` in `config.py`. The language selector and `SUPPORTED_LANGUAGES` are both derived from it.

### Key files

Paths are relative to the `chronometer/` repository directory:

- `i18n/__init__.py` — `setup_i18n(lang)` configures gettext
- `i18n/compile.py` — compiles `.po` → `.mo` using polib
- `i18n/test_i18n.py` — checks that translations load correctly

Messages with variable values use placeholders, such as `{count}` and `{monitor_name}`. The template must be translated before applying `.format()`.

## Tests

Run these from inside the `chronometer/` directory, with the virtual environment active.

**Linux and Windows Git Bash / MINGW64:**

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

Expected result: each script prints a message saying all tests passed.

The compiled `.mo` files are checked by `i18n/test_mo_up_to_date.py`, which runs with `pytest` (below).

Alternatively, run all tests with `pytest` (included in `requirements-dev.txt`). From the directory that **contains** `chronometer/`, in any terminal:

```bash
cd ..
python -m pytest -q chronometer --ignore=chronometer/.venv
```

## Installation Using the Desktop File (Linux)

The `chronometer.desktop` file assumes that the `Chronometer` executable is available in the `PATH`. From inside `chronometer/`, after [building](#building-the-executable), for a per-user installation:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications ~/.local/share/icons/hicolor/scalable/apps
cp dist/Chronometer ~/.local/bin/Chronometer
cp chronometer.desktop ~/.local/share/applications/
cp icon/chronometer-stopwatch-svgrepo-com.svg ~/.local/share/icons/hicolor/scalable/apps/
chmod +x ~/.local/bin/Chronometer
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

If `~/.local/bin` is not in the `PATH`, change `Exec` in the desktop file to the executable's absolute path. The build does not install the desktop file or icon automatically.

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| `py` is not recognized (Windows) | The Python launcher is not installed. Reinstall Python from python.org with the `py` launcher enabled, or use `python` if it is on the `PATH`. |
| `python3: command not found` on Windows | `python3` does not exist there. Use `py -3` before activating the venv and `python` after. |
| `ModuleNotFoundError: No module named 'chronometer'` | `python -m chronometer` was run from the wrong directory. Run it from the directory that **contains** `chronometer/` (`cd ..`). |
| `No module named 'PyQt6'` or `polib` | The venv is not active, or the package was not installed in it. Activate the venv and run `python -m pip install -r requirements-dev.txt`. |
| Venv activation is blocked on Windows | In PowerShell, script execution may be disabled; use CMD or Git Bash instead, or change the execution policy for your user. Not tested here. |
| The `.exe` is blocked by Smart App Control | See [Windows Smart App Control](#windows-smart-app-control). |
| The output window does not appear on the second monitor | Check that the monitor is connected and selected in the app. A saved monitor that no longer exists falls back automatically. On Linux, multi-monitor behavior depends on Qt, the compositor, and X11/Wayland. |
| `libtiff.so.5` warning during the Linux build | It appears when that library is not installed. See [Known Issues](#known-issues). |

## Contributing

See also [AGENTS.md](AGENTS.md), which holds the same rules for AI coding agents.

1. Create and activate a virtual environment and install `requirements-dev.txt`.
2. Run the tests and Pylint before and after making changes.
3. Pylint is **mandatory**: the code must score 10.00/10 (`fail-under=10` in `.pylintrc`). CI runs Pylint and `pytest` on every push and pull request.
4. When changing translatable text, update the `.po` files, recompile with `python i18n/compile.py` and commit the `.mo` files together with the `.po` files. The `.mo` files are versioned on purpose, and `pytest` fails if a `.mo` is out of date.
5. Validate the build on the target operating system.
6. Keep changes focused and update the README when behavior changes.

### Running Pylint

Run from inside the `chronometer/` directory, with the virtual environment active.

**Linux and Windows Git Bash / MINGW64:**

```bash
python -m pylint $(git ls-files '*.py')
```

**Windows CMD** (`$(...)` does not exist there; Pylint expands the quoted patterns itself):

```cmd
python -m pylint "*.py" "i18n/*.py"
```

Expected result: `Your code has been rated at 10.00/10`. The CMD command was checked on Linux only (with the same quoting); it has not been run on Windows.

## Known Issues

- The countdown continues to show negative time after `00:00` until it is stopped manually.
- The PyInstaller build must be run on the target operating system.
- The Windows `.exe` is unsigned and may be blocked (see [Windows Smart App Control](#windows-smart-app-control)).
- On Linux, PyInstaller ignores the `.ico` parameter as the executable icon; visual integration depends on the `.desktop` file and icon installation.
- The output window requires a graphical session, and multi-monitor behavior depends on Qt, the compositor, and the X11/Wayland session.
- The `libtiff.so.5` warning may appear during the build when that library is not installed on the system.

## Customization

All colors, fonts, sizes, and timings can be adjusted in `theme.py` (in the `chronometer/` directory):

| Variable | Description |
|---|---|
| `LIGHT` / `DARK` | Theme color palettes |
| `OUTPUT` | Output window colors |
| `FONT` | Font sizes |
| `OUTPUT_TIMER_H_RATIO` | Output timer scale (% of height, default: 0.45) |
| `OUTPUT_TIMER_W_RATIO` | Output timer scale (% of width, default: 0.22) |
| `OUTPUT_CLOCK_RATIO` | Clock scale (% of timer, default: 0.60) |
| `TIME_WARN_SECS` | Orange warning threshold (default: 60 s) |
| `TIME_DANGER_SECS` | Red warning threshold (default: 0 s, i.e. overtime) |

## License

This project is licensed under the [MIT License](LICENSE).
