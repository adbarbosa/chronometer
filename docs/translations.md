# Maintain translations

This guide covers changing interface text and adding a language. Work from the **repository root**, with the virtual environment active and `requirements-dev.txt` installed as described in [Contributing](../CONTRIBUTING.md#prepare-your-environment).

## Understand the files

Chronometer uses **gettext**, a system that looks up an original message and returns its translation.

| File | Purpose | Edit by hand? |
|---|---|---|
| Python `_('Mensagem')` calls | Original interface messages, in Portuguese (Portugal) | Yes, when changing the interface. |
| `i18n/chronometer.pot` | Template listing messages extracted from the code | Regenerate with the update command. |
| `i18n/<language>.po` | Human-readable translations, such as `en_US.po` | Yes, edit translations and translator metadata. |
| `i18n/locales/<language>/LC_MESSAGES/chronometer.mo` | Compiled translation read by the app | Generate with the compiler. Commit this file too. |

`pt_PT` means Portuguese/Portugal; `en_US` means English/United States. `ConfigManager.LANGUAGE_NAMES` in `config.py` is the registration list. Tools process that list, and the app uses it for the language selector. A catalog file alone does not register a selectable language.

The app normalizes saved language codes before loading them. An empty, whitespace-only, unsupported or wrongly typed saved value means automatic selection. Automatic detection maps Portuguese variants to `pt_PT` and English variants to `en_US`; another unregistered system language uses Portuguese.

For a registered language, the app tries to load its compiled catalog. If the file is missing or invalid, it tries Portuguese and finally the original Portuguese messages. `setup_i18n()` and `get_current_language()` report the language actually applied, not a failed request. The selector follows that effective language. This avoids an English selection remaining visible while the fallback interface is Portuguese.

## Change an existing message

### 1. Edit the original message

Use a literal string inside `_()`:

```python
_("Abrir")
_("Aberto em: {monitor_name}").format(monitor_name=name)
```

Do not use an f-string inside `_()`: the catalog needs the stable message before values are inserted. Product names, time values and internal identifiers are not messages to translate.

### 2. Update the catalogs

From the root, in Linux, CMD or Git Bash:

```bash
python i18n/update.py
```

**Expected result:** an `Atualizado <language>.po` line for each registered language. The template contains current messages and source references; each PO gains new messages while retaining existing translations. Removed messages become obsolete entries in the PO. No MO is generated at this stage.

The extractor reads root application `.py` modules and `i18n/__init__.py`; it excludes `test_*.py`, `conftest.py` and `build.py`. It handles `_()` calls containing one non-empty literal string, including adjacent Python string literals. It rejects dynamic messages. If application modules move to another folder, extend `extract_messages()` and its coverage tests. Plural/context gettext APIs are not currently implemented by this extractor.

### 3. Translate every active message

Open each registered `.po` with Poedit, Lokalize or a text editor. Fill in `msgstr`, preserving the original `msgid`:

```po
msgid "Abrir"
msgstr "Open"
```

For Portuguese, the translation will usually match the source. Complete all registered languages before considering the change finished.

Keep placeholder names exactly the same:

```po
msgid "Aberto em: {monitor_name}"
msgstr "Opened in: {monitor_name}"
```

Also preserve meaningful spaces, such as the leading space in `" min"`. Resolve any `fuzzy` entries: that flag means a translation needs review and prevents it from being considered a finished translation.

### 4. Compile and verify

From the root:

```bash
python i18n/compile.py
python -m pytest -q . --ignore=.venv
```

**Expected result:** a `Compilado <language>.po` line for every registered language, followed by passing tests. The compiler reports errors if a registered PO is absent or cannot be read. The tests check source/template/catalog coverage, placeholder names, unfinished translations, runtime loading and MO correspondence.

Compilation alone does not translate empty entries. Gettext can fall back to original strings for individual missing translations; the tests deliberately require registered catalogs to be complete. Missing or corrupt whole catalogs also have runtime fallback tests, but a fallback is not a replacement for delivering complete compiled resources.

### 5. Check the interface and review files

Run `python __main__.py`, select each language and inspect buttons, the Help menu, output title and About dialog. Long translations must remain readable.

Review changes to the Python source, POT, affected POs and compiled MOs. The MO files are versioned on purpose and must accompany their PO changes. Re-running the updater without source/version changes should not introduce a new diff.

## Add a language

1. Choose a regional code, for example `es_ES` for Spanish/Spain. Add the code and its self-name to `ConfigManager.LANGUAGE_NAMES`:

   ```python
   LANGUAGE_NAMES = {
       "pt_PT": "Português (PT)",
       "en_US": "English (US)",
       "es_ES": "Español (España)",
   }
   ```

2. Run `python i18n/update.py`. It creates `i18n/es_ES.po` if missing, already containing all active messages and its language code.
3. Fill in every translation. Set translator/team metadata where appropriate. Do not copy an incorrect plural rule from another language; this application currently uses only singular message calls.
4. Run `python i18n/compile.py`. Confirm that `i18n/locales/es_ES/LC_MESSAGES/chronometer.mo` now exists.
5. Run the full tests and Pylint as described in Contributing.
6. Start a new app process. Select the new language in the bottom selector. Registration is read when modules are imported, so an already running process will not gain the new entry.
7. Update the README's language list and the translated About description that names supported languages. Repeat extraction, translation, compilation and tests if those source messages changed.
8. Include the registration, PO, MO, template and documentation changes together.

Adding `pt_BR` or another Portuguese/English variant makes it selectable explicitly, but automatic system normalization still chooses `pt_PT` / `en_US`. Supporting a different automatic mapping requires a separate code change and tests.

## Common problems

| Problem | Explanation and next action |
|---|---|
| `No module named polib` or `pytest` | Activate `.venv` and install `requirements-dev.txt` from the root. |
| A new message is absent from the PO | Run the updater; confirm the message is a literal `_()` call in an extracted application module. |
| A new language has no MO | Register it, run the updater, translate its PO and run the compiler. Confirm you are inspecting the right code. |
| MO mismatch test fails | Run the compiler and include the regenerated binary in the change. |
| Coverage or placeholder test fails | Update the catalogs, complete translations and preserve the source's named fields. |
| The interface remains unchanged | Restart after code/catalog maintenance, select the intended language, and check the saved language preference. Built executables contain the catalogs present at build time, so rebuild them too. |
| Portuguese appears instead of the requested language | Confirm the code is registered and its MO is present and valid. Unknown system languages use Portuguese; a registered language with a missing or corrupt catalog also falls back to Portuguese, and the selector reflects that result. Rebuild executables after repairing bundled catalogs. |
| A blank saved language behaves unexpectedly | Blank and whitespace-only values use automatic detection. Set a registered code through the selector to make an explicit choice, or use `null` to keep automatic detection. |

For runtime selection and the `language: null` preference, see [Preferences](../README.md#preferences).
