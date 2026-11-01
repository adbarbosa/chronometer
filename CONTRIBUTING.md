# Contributing to Chronometer

This guide is for someone changing the source code or documentation. To use the app without changing it, follow [Install and run](README.md#install-and-run).

## What the tools do

| Tool | Why the project uses it |
|---|---|
| Python | Runs the application and development scripts. |
| PyQt6 / Qt | Creates desktop windows and controls and delivers user/system events. |
| pytest | Runs automated checks and reports failed expectations. |
| Pylint | Finds code-quality problems; this project requires a score of 10.00/10. |
| polib | Reads and writes gettext translation catalogs. |
| PyInstaller | Packages Python, modules and resources into an executable. |
| GitHub Actions | Runs the configured checks after a push or pull request; this is called continuous integration, or CI. |

A passing automated check only establishes the behavior exercised by that check. It does not replace testing a projector, a Windows machine or a built executable.

## Prepare your environment

### 1. Get the repository

Follow [Download the code](README.md#2-download-the-code). Keep the folder name `chronometer`. The root contains `main_window.py`; the root itself is the Python package, rather than a folder containing a second `chronometer/` directory.

### 2. Create or activate the virtual environment

Run the appropriate block **from the repository root**. If `.venv` already exists, omit the creation command and activate it.

**Linux — bash:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

**Windows — CMD:**

```cmd
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
```

**Windows — Git Bash:**

```bash
py -3 -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
```

The development requirements include the runtime requirements. You do not need a separate runtime installation after this step. The requirements files pin the direct packages to validated versions, so updating an existing environment with the same command selects those versions too. Pip still resolves their indirect dependencies, and the packages available for different operating systems or Python versions may differ.

Change a version pin deliberately, then run the full configured matrix and executable checks before treating the new set as validated. When reporting a failure, include `python --version` and `python -m pip show PyQt6 pytest pylint polib pyinstaller`.

### 3. Establish a baseline

With the environment active, run these from the repository root in Linux, CMD or Git Bash:

```bash
python -m pytest -q . --ignore=.venv
python -m pylint "*.py" "i18n/*.py"
```

**Expected result:** pytest reports passing tests, and Pylint reports `10.00/10` with exit code zero. The quoted patterns are expanded by Pylint, including new Python files that Git does not yet track. The current patterns cover root modules and `i18n/`; extend them if you introduce another source directory.

The Qt test fixture chooses `offscreen` by default if `QT_QPA_PLATFORM` is unset. This backend draws without a physical screen. To select it explicitly:

**Linux / Git Bash:**

```bash
QT_QPA_PLATFORM=offscreen python -m pytest -q . --ignore=.venv
```

**Windows CMD:**

```cmd
set QT_QPA_PLATFORM=offscreen
python -m pytest -q . --ignore=.venv
set QT_QPA_PLATFORM=
```

Use a fresh terminal for normal interactive use after setting testing-only environment variables. On Linux/Git Bash, the one-command prefix affects that command only.

If pytest or Pylint cannot write their cache in a restricted environment, use `python -m pytest -q . --ignore=.venv -p no:cacheprovider` and direct Pylint's `PYLINTHOME` environment variable to a writable temporary folder. Cache access errors are separate from failed application assertions.

## Understand the code before changing it

Read [Architecture](docs/architecture.md). It explains state ownership, the monotonic countdown, preferences, monitor selection, translation startup and resource paths.

Use these entry points:

| Change | Start here |
|---|---|
| Countdown behavior | `countdown.py`, then its use in `main_window.py` |
| Control layout or actions | `main_window.py` |
| Shortened monitor/status display and full-text tooltips | `compact_widgets.py` |
| Audience output or attention flash | `timer_window.py` |
| Colors, dimensions or styles | `theme.py` |
| Preferences or file errors | `config.py` |
| Monitor selection or identity | `displays.py`, then `windows_displays.py` for the native Windows reader |
| Text or a new language | [Translation guide](docs/translations.md) |
| Executable or resource lookup | [Distribution guide](docs/distribution.md), `build.py`, `resources.py`, `smoke_check.py` |

## Make a focused change

1. Inspect `git status --short` and the relevant code. Preserve existing work.
2. Write down the expected result of the change. For a bug, keep a small reproduction example.
3. Add a regression test when logic changes. Prefer observable behavior and controllable clocks over waiting for real seconds.
4. Change only the related code and documentation.
5. Run the relevant checks, then the complete required checks before delivery.
6. Review `git diff` and `git diff --check`. Inspect new files too; ordinary `git diff` does not display their content before they are added to Git.

Do not manually edit `Chronometer.spec`, `build/` or `dist/`. The root `.spec` is a legacy generated file. The supported build script writes new specifications to `build/`; see the build guide.

### Coding and writing conventions

- Python identifiers are in English, matching the existing API.
- Comments, docstrings, user-facing source messages and diagnostic output are in Portuguese (Portugal).
- Repository documentation and commit messages are in English. Explain unfamiliar terms and give complete procedures.
- Use Python 3.10-compatible syntax, such as `str | None`.
- Give every module, class and named function a useful docstring, including private helpers and constructors. Pylint ignores some private names, so its score alone does not enforce this rule.
- Put visual values and stylesheet construction in `theme.py`. Durations and countdown state belong to the application logic.
- Wrap translatable UI messages in `_()`, using a literal source string. Keep product names, technical identifiers and numeric time formatting out of translation catalogs. Developer-script diagnostics and `.desktop` metadata do not use this Python translation mechanism.
- Use placeholders: `_('Aberto em: {monitor_name}').format(monitor_name=name)`. Do not translate an already formatted string or put an f-string inside `_()`.
- Fix the cause of Pylint findings. Do not weaken checks to obtain a score. Any local suppression needs a concrete explanation, such as a Windows-only API or PyInstaller's private runtime attribute.
- Keep the application version unchanged unless a version update was requested. `__init__.py` is authoritative. When updating it, review the README version and tree, regenerate translation metadata and review versioned examples. Test output must not hard-code an old version.
- Use Conventional Commits when committing: for example, `fix: preserve countdown progress after delayed events` or `docs: explain monitor selection`. Creating a change does not itself require making a commit or pushing it.

## What the automated tests cover

| Area | What is checked |
|---|---|
| Countdown | Late updates, fractional pause/resume, restart after expiry, reset, loading and zero duration. |
| Qt controls | Ten minutes loaded at startup, explicit manual application, presets, synchronized labels, pause/reset, output visibility/status, and preference-save failure feedback. |
| Attention and lifetime | Countdown updates and resizing during a flash, interruption/completion, and destruction of both windows without callbacks to deleted widgets. |
| Language and theme | Runtime loading, blank/unsupported language normalization, missing/corrupt catalog fallback, selector coherence, Help-menu refresh and the About dialog's selected theme. |
| Catalog maintenance | Source-message coverage, preserved placeholders, registered-language consistency, an additional temporary language and `.po`/`.mo` correspondence. |
| Preferences | Persistence, defaults, legacy decimal indexes, non-finite/fractional/invalid values, simultaneous subprocess updates, lock timeout, failed replacement and an unusable configuration directory. |
| Monitor logic | Simulated repeated metadata, native interface enumeration/flags, clone grouping, missing saved identity/index, startup selection and explicit screen/placement call order. |
| Resources | Source files, the simulated PyInstaller extraction root and valid-icon fallback when the preferred ICO is damaged or missing. |

The tests do **not** operate physical displays or call Windows display APIs on Linux. An `offscreen` output window is not evidence that positioning works on Wayland, X11 or Windows. A simulated extraction path is not a substitute for launching the built executable.

Preferences are isolated in temporary folders, including subprocess checks. `conftest.py` restores global gettext state, disposes of both the panel and output, and processes deferred deletion events. Follow that pattern for new GUI tests. A hidden or closed widget may still exist; do not leave an output window or application-wide callback behind after a test. Never let a test change your real `~/.chronometer/config.json`.

Preference writers use a `QLockFile` to coordinate separate processes, with a 250-millisecond acquisition limit. Add concurrency tests around the whole read–alter–write operation, not only `os.replace`. Use explicit subprocess/event coordination rather than hoping two arbitrary sleeps overlap. Every writer must have its own temporary file, and timeout/failure checks must confirm that the previous final JSON remains valid.

You can also run `python test_config.py` or `python i18n/test_i18n.py` for those subsets; the full pytest command remains the completion check.

The workflow is configured to run Pylint and pytest on Linux and Windows with Python 3.10, 3.11 and 3.12. Its Python 3.12 jobs also build the executable and run the packaged startup check described below. This is the configured coverage, not evidence that a new workflow run has passed. Consult the actual GitHub Actions run before reporting remote results. Neither a Windows VM nor an `offscreen` launch verifies a physical projector or multi-monitor placement.

## Check packaged startup automatically

After building with `python build.py`, keep the virtual environment active and run the appropriate command from the repository root:

**Linux:**

```bash
python smoke_check.py dist/Chronometer
```

**Windows CMD or Git Bash:**

```text
python smoke_check.py dist/Chronometer.exe
```

The helper compares the bundled SVG, ICO and Portuguese/English MO files with the source resources, then starts the executable from a fresh temporary working directory. It sets `CHRONOMETER_CONFIG_DIR` to temporary preferences and selects the `offscreen` backend, so it neither changes personal preferences nor requires a desktop display.

**Expected result:** the executable stays running for the default five-second startup interval without a Python traceback, the helper stops it, and the helper exits successfully. An early process exit, mismatched resource or traceback is a failed check. Use `--seconds 10` to request a longer interval or `python smoke_check.py --help` to see all options. The `--source-root` option changes the checkout whose resource bytes are used for comparison; normally its default is correct.

This checks packaged startup and content, not buttons, preference saving or actual display placement. Continue with the manual procedure below and the [distribution checklist](docs/distribution.md#verify-a-build-outside-the-source-folder) when validating a release.


## Run a manual smoke check

A **smoke check** is a short run through essential behavior after a change. Use an interactive desktop for this procedure.

To keep experiments separate from your real preferences, set `CHRONOMETER_CONFIG_DIR` to a new empty absolute folder before starting the process. For example:

**Linux / Git Bash**, from the repository root with the environment active:

```bash
CHRONOMETER_CONFIG_DIR="$(python -c 'import tempfile; print(tempfile.mkdtemp())')" python __main__.py
```

The inner Python command creates a temporary folder and prints its native path. Using Python here also avoids passing a Unix-style `/tmp` path directly to Windows Python in Git Bash.

**Windows CMD**, using an unused folder name:

```cmd
set "CHRONOMETER_CONFIG_DIR=%TEMP%\chronometer-check-001"
python __main__.py
set CHRONOMETER_CONFIG_DIR=
```

The app reads this variable at startup. The override contains `config.json` directly, without an extra `.chronometer` subfolder. Delete the temporary folder afterwards if no longer needed. Do not select your real preference directory for an isolated check.

Check that:

1. The panel starts stopped at `10:00`.
2. Editing manual minutes changes the loaded time only after Set.
3. Start, Stop and Reset work, and both windows agree.
4. Orange includes zero; negative time is red.
5. Hiding the output through Close, its smaller clock or the window system leaves the timer running and changes the panel status to closed; Open restores the output.
6. Attention keeps the time readable while the countdown updates or the output is resized, then restores the normal background and current warning color. Start and Reset interrupt the effect safely.
7. Changing language updates the Help menu and keeps the selector consistent with the displayed language; About follows the selected theme.
8. The panel still names the actual open monitor after a list refresh or language change. A pending selection alone does not move the output.
9. Closing the panel closes the output. Preference-save failures produce a short status-bar notice without stopping the presentation.

For control-panel layout changes, repeat the check in Portuguese and English with both light and dark themes. The panel should remain 400 × 550, excluding window borders, with no clipped or overlapping controls. Check the preset rows in order: `1, 2, 3, 4`; `5, 10, 15, 20`; `25, 30, 45, 60` minutes. Click each preset and confirm that it stops and loads the displayed duration. The language selector and theme button belong on the left of the footer; the date belongs above the clock on the right, with both right-aligned. Keep the main text sizes when adjusting margins or button padding.

Use a long monitor name and a long open-output status to check that the panel stays narrow. A shortened label should end with an ellipsis, while its tooltip shows the complete text. Refresh the list and change language to confirm that shortening text does not change the pending selection or the actual open monitor. Record whether these checks used a desktop or Qt's `offscreen` backend; a rendered image does not verify physical monitor placement.

To check the preference-save failure notice, create another fresh test folder and put an empty directory named `config.json` inside it. Set `CHRONOMETER_CONFIG_DIR` to that test folder before launching, then change the theme. A directory cannot be replaced by the preference file, so the save should fail: the status-bar notice should fit, and the timer should still work. Close the app and remove the test folder afterwards.

For monitor changes, add real connect/disconnect, duplicate-monitor and display-scaling checks on each target platform. Switch between monitors with the output already full screen as well as when first opening it. Test on the intended Wayland/X11 compositor or Windows display setup: `setScreen()` explicitly chooses the target, while coordinate placement alone may be ignored. Cloned physical monitors sharing one Qt screen cannot be selected independently. Record the OS, desktop session and display arrangement.

## Finish and report the result

Always run pytest and Pylint. If translatable UI messages changed, run the translation update and compiler and include `.pot`, `.po` and `.mo` changes. If packaging changed, build and launch the executable on the target system.

For documentation changes, follow the instructions literally in a fresh terminal, check local links and make sure expected results match the current code. Screenshots in `docs/images/` should show the current UI; capture them using temporary preferences. Explain any simulated display or example time in the caption.

State what changed, what was tested and what remains unverified. Consult [the validation record](docs/validation.md) for the current evidence; do not turn a configured CI matrix into a claim that every platform has been tested.
