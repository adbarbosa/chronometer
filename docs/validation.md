# Validation record

This record describes checks performed during the documentation and behavior update on **2026-11-01**. It is evidence for that checkout and environment, not a guarantee about every platform or future change. Repeat the relevant checks after editing the application.

## Local environment

| Component | Version |
|---|---|
| Operating system | Linux |
| Python | 3.12.3 |
| PyQt6 | 6.11.0 |
| pytest | 9.1.1 |
| Pylint | 4.1.2 |
| polib | 1.2.0 |
| PyInstaller | 6.20.0 |

An existing virtual environment was used. A clean online installation of all dependencies was not repeated. The configured GitHub Actions matrix targets Linux with Python 3.10, 3.11 and 3.12; editing that workflow is not evidence that a remote run has completed.

## Automated checks

From the repository root, with the environment active:

```bash
python i18n/update.py
python i18n/compile.py
python -m pytest -q . --ignore=.venv
python -m pylint "*.py" "i18n/*.py"
git diff --check
```

Results: **31 tests passed**, **Pylint 10.00/10**, and no whitespace errors. Tests were also run through the older parent-directory invocation. Repeating catalog update/compilation without changes produced identical catalog bytes. Local documentation paths and internal heading links were checked.

The suite's actual scope is listed in [Contributing](../CONTRIBUTING.md#what-the-automated-tests-cover). In particular, the language checks now execute under pytest, and the additional-language test creates and compiles a temporary catalog without changing the supported production languages.

The direct entry point was also started from a fresh bash shell after environment activation, and the module entry point was started from the parent folder. Both stayed running during short `offscreen` startup checks with temporary preferences and no traceback.

## Visual checks

The control panel, output and About dialog were rendered with Qt's `offscreen` backend and temporary preferences. English/light and Portuguese/dark panel/About captures were inspected for legibility and text clipping. The README's two images show the English control panel and an output with 45 seconds remaining. Example clock/date labels were set for those images.

This confirms rendering in the local test backend. It does not establish physical-screen placement, operating-system window decorations or font availability on another machine.

## Linux executable

`python build.py` completed successfully. The generated specification was under `build/`, and the tracked root `Chronometer.spec` was unchanged.

The built executable was launched by absolute path from a temporary directory outside the checkout, with:

- `QT_QPA_PLATFORM=offscreen`;
- `CHRONOMETER_CONFIG_DIR` pointing at temporary preferences;
- an English/dark preference file.

It remained running for a five-second startup check without a Python traceback and was then terminated by the check harness. Its temporary preference file was unchanged. The archive's SVG, ICO and Portuguese/English MO bytes matched the current source resources.

This was a startup and bundle-content check. Interactive full-screen behavior and preference changes in the binary were not exercised. Follow the [distribution checklist](distribution.md#verify-a-build-outside-the-source-folder) on a desktop before distributing a release.

## Still requiring target-system validation

- Windows CMD and Git Bash command execution, executable startup and native monitor API behavior.
- SmartScreen/Smart App Control behavior on an identified Windows installation.
- Real monitor selection, disconnect/reconnect, matching displays and mixed display scaling.
- Full-screen placement on the intended X11/Wayland compositor.
- Executable portability to a second representative Linux machine.
- Interactive use of the compiled app and repeated preference-saving checks on target systems.
- macOS; it is outside the current validation scope.

For each additional check, record the date, app version/commit, OS and architecture, display/session details, exact procedure and result. Distinguish an assertion made by a simulated test from a result observed on physical equipment.
