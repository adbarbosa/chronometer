# Build, install and check an executable

An executable lets someone run Chronometer without installing this repository's Python environment. PyInstaller bundles Python and the Python dependencies, but the result still depends on the target operating system and some system libraries.

This is a developer procedure. For ordinary source use, follow [Install and run](../README.md#install-and-run).

## Before building

1. Use the operating system and architecture you intend to support. A Linux build does not produce a Windows executable. The Python process's architecture also matters.
2. Download the source, keep the folder name `chronometer`, and prepare the virtual environment using [Contributing](../CONTRIBUTING.md#prepare-your-environment).
3. Open a terminal in the **repository root** and activate that environment.
4. Confirm that translations are complete and checks pass:

   ```bash
   python i18n/compile.py
   python -m pytest -q . --ignore=.venv
   python -m pylint "*.py" "i18n/*.py"
   ```

If source messages changed, run the update/translation procedure in [Translations](translations.md) before compiling. The compiler only transforms the PO files it is given; it does not discover new source messages.

## Generate the executable

From the repository root, with the environment active, the command is the same in Linux, CMD and Git Bash:

```bash
python build.py
```

**Expected result:** PyInstaller logs its work, the script reports success and the executable exists at:

| Build platform | Output |
|---|---|
| Linux | `dist/Chronometer` |
| Windows | `dist/Chronometer.exe` |

The supported script uses `--onefile`: resources are extracted to a temporary directory at startup. It uses `--windowed` for windowed platforms, adds the repository parent as an import-analysis path and includes `icon/`, `i18n/locales/` and `chronometer.desktop`.

New generated specifications are written to `build/Chronometer.spec`. The root `Chronometer.spec` is a legacy tracked artifact containing local paths; do not use or manually edit it. `build/` and `dist/` are generated output and must not be committed. The build does not install the app, desktop file or icons automatically.

The name does not include the version or architecture. When sharing a build, rename a copy to identify its app version, OS and architecture, and record the build's Python and dependency versions. Do not infer compatibility with another Linux distribution or older OS from a successful build on your own computer.

## Start the result

Run from the repository root after building.

**Linux:**

```bash
./dist/Chronometer
```

**Windows CMD:**

```cmd
dist\Chronometer.exe
```

**Windows Git Bash:**

```bash
./dist/Chronometer.exe
```

**Expected result:** the panel opens stopped at `10:00`. Check the language, icon and controls. Merely finding a file in `dist/` is not proof that imports and resources work at runtime.

## Verify a build outside the source folder

Test in a desktop session, using a fresh temporary preference folder so the check does not alter your usual settings. These examples assume the repository is in the `projects` folder from the README.

**Linux**, from any folder:

```bash
CHRONOMETER_CONFIG_DIR="$(mktemp -d)" ~/projects/chronometer/dist/Chronometer
```

**Windows CMD**, using an unused temporary folder name:

```cmd
set "CHRONOMETER_CONFIG_DIR=%TEMP%\chronometer-build-check-001"
cd /d "%TEMP%"
"%USERPROFILE%\projects\chronometer\dist\Chronometer.exe"
set CHRONOMETER_CONFIG_DIR=
```

**Windows Git Bash**, with the development environment active, from any folder:

```bash
CHRONOMETER_CONFIG_DIR="$(python -c 'import tempfile; print(tempfile.mkdtemp())')" ~/projects/chronometer/dist/Chronometer.exe
```

The inner Python command is only used to obtain a native Windows temporary-folder path. To check on a target machine without Python installed, create an empty folder yourself and use its absolute Windows path as the variable value instead.

These commands intentionally use absolute executable paths. Adjust them if you cloned elsewhere. `CHRONOMETER_CONFIG_DIR` is read when the process starts; the chosen folder contains `config.json` directly. Keep its path if you want to inspect the saved file and delete that temporary folder after the check when no longer needed.

Verify:

1. The panel starts without access to a source-file working directory.
2. The application and About icons load.
3. Portuguese and English work, including the Help menu and output title.
4. Start, Stop, Reset, manual duration and all twelve presets work. The 400 × 550 panel fits in both languages and themes: presets form three rows (`1, 2, 3, 4`; `5, 10, 15, 20`; `25, 30, 45, 60` minutes), and the date sits above the clock at the bottom right. Long monitor/status labels show their full text in tooltips.
5. The selected output display opens full screen and remains synchronized.
6. Attention flashes and restores the background; hiding/reopening preserves progress.
7. Theme, language and monitor identity survive a restart using the **same** temporary preference folder. For shell checks, replace the temporary-folder creation expression with the actual path from the first run rather than creating a new folder each time.
8. Closing the panel ends the process.

Repeat on a machine representative of the intended target, including its display arrangement. A short `offscreen` launch is useful for startup checks in automation, but does not validate interactive behavior or physical monitor placement. Record exactly which level was checked in [Validation](validation.md).

## Automated bundle and startup check

After building, run the checker from the repository root with the development environment active.

**Linux:**

```bash
python smoke_check.py dist/Chronometer --seconds 5
```

**Windows CMD or Git Bash:**

```text
python smoke_check.py dist/Chronometer.exe --seconds 5
```

**Expected result:** the checker confirms the bundled resources, observes that the process stays running for the requested interval, terminates it and exits with code zero. Missing/outdated resources, an early process exit or a Python traceback make the command fail.

The checker compares the SVG, ICO and both production MO files with the source copies, accepting archive path separators from either operating system. It starts the executable by absolute path from a new temporary working directory, selects `offscreen` and creates isolated preferences. It also confines onefile extraction to a temporary directory. It terminates the child process tree and removes the temporary folders afterwards.

Use `--seconds` to choose a longer observation interval and `--source-root` to point to the source tree whose resources should match. A process that remains alive is not proof that every control works: this is a startup/content check, not an interactive, physical-monitor or portability check. Continue to use the desktop checklist above.

CI is configured to run tests/lint on Linux and Windows with Python 3.10–3.12 and to build/check executables on both systems with Python 3.12. Check the remote workflow result before claiming those jobs have passed; configuring them does not execute them locally.

## Install a Linux desktop launcher

The bundled `.desktop` file is a launcher description used by desktop environments. It calls an executable named `Chronometer` from the desktop session's `PATH` and uses an icon with the matching installed name.

After building, run from the repository root:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications ~/.local/share/icons/hicolor/scalable/apps
cp dist/Chronometer ~/.local/bin/Chronometer
cp chronometer.desktop ~/.local/share/applications/
cp icon/chronometer-stopwatch-svgrepo-com.svg ~/.local/share/icons/hicolor/scalable/apps/
chmod +x ~/.local/bin/Chronometer
```

If `update-desktop-database` is available, refresh the launcher database:

```bash
update-desktop-database ~/.local/share/applications
```

**Expected result:** the application menu offers Chronometer. Search for it; some desktop environments refresh only after signing out and in.

If launching fails, try `~/.local/bin/Chronometer` from a terminal. Open `~/.local/share/applications/chronometer.desktop` in a text editor and replace `Exec=Chronometer` with the executable's actual absolute path if the desktop session cannot find it. For example:

```ini
Exec=/home/yourname/.local/bin/Chronometer
```

Replace `yourname`; do not put `$HOME` or `~` in the desktop entry expecting shell expansion. If the path contains spaces, quote the full executable path. Keep the icon name unless you also change the installed icon filename. The desktop entry's `Version=1.0` describes the entry format, not Chronometer's release version.

To remove this per-user installation, delete only the three copies you installed: `~/.local/bin/Chronometer`, `~/.local/share/applications/chronometer.desktop` and `~/.local/share/icons/hicolor/scalable/apps/chronometer-stopwatch-svgrepo-com.svg`. This leaves source code and saved preferences in place.

## Windows signing and blocks

The build script does not sign the Windows executable. A digital signature identifies its publisher; reputation systems and local security policy can still affect execution.

- **SmartScreen** uses reputation. A signed but new file can still produce an unrecognized-app warning; a valid certificate is not a universal guarantee of acceptance. See [Microsoft's developer guidance](https://learn.microsoft.com/windows/apps/package-and-deploy/smartscreen-reputation).
- **Smart App Control** is a separate Windows 11 protection feature. Its availability and re-enablement behavior depend on the system state and updates. Microsoft's current guidance describes re-enablement without a clean installation on updated systems. See the [official FAQ](https://support.microsoft.com/en-us/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions).

The project's documented source installation and Python shortcut are alternative launch methods; they are not guarantees against every organization policy. Do not disable system protection as a build-validation step. Record the exact Windows version and message when investigating a block.

These references were reviewed on 2026-11-01. Windows behavior has not been executed in this Linux validation environment.

## Troubleshoot build failures

| Symptom | Next step |
|---|---|
| `No module named PyInstaller` | Activate the development environment and install `requirements-dev.txt`. |
| Missing catalog or translation | Compile current POs before building; inspect the source app in the same language. |
| Frozen app cannot find an icon or translation | Check `resources.py` and bundled data destinations. Both must refer to the extraction root, not the source working directory. |
| Qt/shared-library warning | Read the full log and test the resulting app. Warnings such as `libtiff.so.5` can concern an optional plugin; their impact depends on the plugin and target system. Do not declare every warning harmless or install an arbitrary library solely by filename. |
| Cache directory is unwritable | Set `PYINSTALLER_CONFIG_DIR` to a writable temporary folder for that build. |
| Works only from the checkout | Repeat the outside-folder check and inspect missing imports/resources. |
| Works locally but fails on a target computer | Record OS/architecture and missing-library errors; rebuild/test for that target environment. |

For a build report, include the app version, Python version, dependency versions, OS/architecture, full build command, relevant log and the runtime checks performed. Check [third-party terms](third-party.md) when preparing a distribution.
