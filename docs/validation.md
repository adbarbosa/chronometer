# Validation record

This record describes checks performed for the **0.6.0 compact-layout update and refresh-icon contrast fix on 2026-11-01**, following the earlier robustness work. It is evidence for that checkout and environment, not a guarantee about every platform or future change. Repeat the relevant checks after editing the application.

## Local environment

| Component | Version |
|---|---|
| Operating system | Linux |
| Python | 3.12.3 |
| PyQt6 | 6.11.0 |
| Qt runtime / PyQt6 SIP | 6.11.0 / 13.11.1 |
| pytest | 9.1.1 |
| Pylint | 4.1.2 |
| polib | 1.2.0 |
| PyInstaller | 6.20.0 |

An existing virtual environment was used. A clean online installation of all dependencies was not repeated. The listed runtime/development versions are now pinned in the requirements files. The configured GitHub Actions matrix targets Linux and Windows with Python 3.10, 3.11 and 3.12, plus packaged build/startup jobs on both systems with Python 3.12. Editing that workflow is not evidence that a remote run has completed.

## Automated checks

From the repository root, with the environment active:

```bash
python i18n/update.py
python i18n/compile.py
python -m pytest -q . --ignore=.venv
python -m pylint "*.py" "i18n/*.py"
git diff --check
```

Results: **84 tests passed**, **Pylint 10.00/10**, and no whitespace errors. Compact-text tests observe the text actually sent to Qt's painter: long labels and monitor selections are shortened visually, while their full text, tooltips and monitor identities remain intact. A refresh-icon regression supplies a white desktop icon and checks actual icon pixels through light → dark → light, at 1× and 2× pixel density. Repeating catalog update/compilation without changes produced identical catalog bytes. Local documentation paths and internal heading links were checked. Changed Python modules also passed a Python 3.10 syntax check and a check for module, class and named-function docstrings.

The suite's actual scope is listed in [Contributing](../CONTRIBUTING.md#what-the-automated-tests-cover). Regressions now include concurrent writers, bounded lock failure, invalid/non-finite preferences, effective-language fallback, contrast while flashing and resizing, output visibility/status, explicit screen association, QObject destruction, invalid-icon fallback and startup-check process cleanup. The additional-language test creates and compiles a temporary catalog without changing the supported production languages.

In a separate UI check, all twelve preset buttons were clicked in Portuguese and English with both themes. Each stopped the countdown and loaded its displayed duration. The main-window title and About dialog both reported version 0.6.0.

## Visual checks

The control panel and About dialog were rendered with Qt's `offscreen` backend and temporary preferences. The panel was checked in all four Portuguese/English and light/dark combinations at Qt scale factors 1, 1.25, 1.5 and 2. Four additional cases used Qt's Windows widget style on Linux; this is a style simulation, not a Windows operating-system test. Captures of all four language/theme combinations and examples at 125% and 200% were inspected for clipping and overlap.

The panel remained **400 × 550 logical pixels** in all 20 cases, with a 400 × 506 central area. The central layout's minimum size was 371 × 502 in Portuguese and 364 × 502 in English. The twelve presets occupied three rows of four, with buttons at least 34 pixels high. The date appeared above the clock on the right, with their right edges aligned. No visible control extended beyond the central area.

A simulated long monitor name and open-output status were shortened to fit, while the full text, tooltip and selected monitor identity stayed intact. The nonmodal save-failure notice fitted in the status bar and the countdown kept running. These rendering checks used a simulated failed-save result; an isolated configuration check also confirmed that a directory at the preference-file path makes a real save fail without replacing that directory.

The README's control image was regenerated at 400 × 550 using the English/light interface. Its existing output image shows 45 seconds remaining; the audience output layout was unchanged. Example clock/date labels were set for these documentation images.

The refresh-icon defect was reproduced with the locally installed Breeze Dark icon theme: its near-white system icon was barely visible on the light panel. After the fix, Portuguese and English captures showed a dark glyph on the light panel and a light glyph on the dark panel, while that desktop icon theme remained selected. Requested icon pixmaps at scale factors 1, 1.25, 1.5, 2, 3 and 4 retained the expected physical size and pixel-density metadata. The README image includes the corrected glyph.

This confirms rendering in the local test backend. It does not establish physical-screen placement, operating-system window decorations or font availability on another machine.

## Linux executable

`python build.py` completed successfully. The generated specification was under `build/`, and the tracked root `Chronometer.spec` was unchanged.

The built executable was launched by absolute path from a temporary directory outside the checkout, with:

- `QT_QPA_PLATFORM=offscreen`;
- `CHRONOMETER_CONFIG_DIR` pointing at temporary preferences;
- an English/dark preference file.

The documented command `python smoke_check.py dist/Chronometer --seconds 5` completed successfully. The process remained running for five seconds without a Python traceback and was then terminated by the checker. Its working, preference and extraction directories were temporary and removed afterwards. The archive's SVG, ICO and Portuguese/English MO bytes matched the current source resources.

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
