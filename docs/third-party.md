# Third-party components and artwork

The [MIT license](../LICENSE) covers this project's own code. It does not replace the licenses of Python, Qt, PyQt, packaging tools or artwork. Keep the relevant notices and terms when distributing their components.

## Runtime and build components

| Component | Role and authoritative licensing reference |
|---|---|
| Python | Interpreter; see the [Python license](https://docs.python.org/3/license.html). |
| PyQt6 | Python bindings for Qt. Riverbank offers GPLv3 and commercial licensing; it is not the same licensing choice as Qt itself. See [Riverbank's introduction](https://en.riverbankcomputing.com/software/pyqt) and [license FAQ](https://en.riverbankcomputing.com/commercial/license-faq). |
| Qt | Window toolkit bundled by the PyQt distribution. Its terms depend on the components and distribution; see [Qt licensing](https://www.qt.io/licensing/). |
| PyInstaller | Build tool; see its [license and distribution exception](https://pyinstaller.org/en/stable/license.html). |
| polib | Translation maintenance; see its [license](https://polib.readthedocs.io/en/latest/index.html). |
| pytest | Test runner; see its [license](https://docs.pytest.org/en/stable/license.html). |
| Pylint | Static analysis; see its [project license](https://github.com/pylint-dev/pylint/blob/main/LICENSE). |

The development requirements are not all runtime application modules. A packaged executable also contains transitive dependencies: inspect the installed distributions and bundled files when preparing notices for an actual release. This document identifies sources of terms; it does not relicense their contents or promise that the project's MIT file is sufficient for every distribution.

## Application icon

The repository contains:

- `icon/chronometer-stopwatch-svgrepo-com.svg`
- `icon/chronometer-stopwatch-svgrepo-com.ico`

The SVG's embedded comment names SVG Repo. The matching catalog listing is [Chronometer Stopwatch, SVG Repo #188660](https://www.svgrepo.com/svg/188660/chronometer-stopwatch). It lists **CC0** and uploader **SVG Repo**; it does not name an individual creator. See [SVG Repo's licensing explanation](https://www.svgrepo.com/page/licensing/#public-domain) and the [CC0 dedication](https://creativecommons.org/publicdomain/zero/1.0/).

The repository does not retain a separate conversion log or creator record for the ICO. Keep that provenance limitation visible rather than inventing an author or conversion method. When replacing artwork, record its exact source, license and any changes at the same time.

References reviewed on 2026-11-01.
