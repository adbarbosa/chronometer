"""Verifica recursos e arranque isolado; não valida interação nem monitores físicos."""

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import tempfile

from PyInstaller.archive.readers import CArchiveReader

SOURCE_ROOT = Path(__file__).resolve().parent
BUNDLED_RESOURCES = (
    "icon/chronometer-stopwatch-svgrepo-com.svg",
    "icon/chronometer-stopwatch-svgrepo-com.ico",
    "i18n/locales/pt_PT/LC_MESSAGES/chronometer.mo",
    "i18n/locales/en_US/LC_MESSAGES/chronometer.mo",
)


@dataclass(frozen=True)
class StartupResult:
    """Guarda os diagnósticos recolhidos antes de terminar o processo de verificação."""

    stdout: str
    stderr: str


def verify_bundle_resources(executable: Path, source_root: Path = SOURCE_ROOT) -> None:
    """Compara os bytes dos recursos empacotados com as fontes, incluindo caminhos Windows."""
    archive = CArchiveReader(str(executable))
    names = {name.replace("\\", "/"): name for name in archive.toc}
    for relative_path in BUNDLED_RESOURCES:
        if relative_path not in names:
            raise ValueError(f"Falta o recurso empacotado: {relative_path}")
        bundled = archive.extract(names[relative_path])
        if bundled != (source_root / relative_path).read_bytes():
            raise ValueError(f"O recurso empacotado está desatualizado: {relative_path}")


def _terminate_tree(process: subprocess.Popen, force: bool = False) -> None:
    """Termina o grupo POSIX ou a árvore Windows, incluindo o filho do executável onefile."""
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=False,
            )
        finally:
            if process.poll() is None:
                process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL if force else signal.SIGTERM)
        except ProcessLookupError:
            pass


def check_startup(command: Sequence[str], seconds: float = 5.0) -> StartupResult:
    """Exige que o processo permaneça ativo durante um intervalo limitado, fora do checkout."""
    if not command or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("Indique um comando e uma duração positiva e finita.")
    with tempfile.TemporaryDirectory(prefix="chronometer-smoke-") as directory:
        base = Path(directory)
        working_directory = base / "working"
        preferences = base / "preferences"
        extraction_directory = base / "temporary"
        working_directory.mkdir()
        preferences.mkdir()
        extraction_directory.mkdir()
        (preferences / "config.json").write_text(
            json.dumps({"language": "en_US", "dark_mode": True}), encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["CHRONOMETER_CONFIG_DIR"] = str(preferences)
        environment["QT_QPA_PLATFORM"] = "offscreen"
        environment["PYTHONUNBUFFERED"] = "1"
        # Conservar também a extração onefile dentro da pasta eliminada no fim da verificação.
        for name in ("TMPDIR", "TMP", "TEMP"):
            environment[name] = str(extraction_directory)
        options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {
            "start_new_session": True,
        }
        with subprocess.Popen(
            list(command), cwd=working_directory, env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
            **options,
        ) as process:
            early_exit = None
            try:
                stdout, stderr = process.communicate(timeout=seconds)
                early_exit = process.returncode
            except subprocess.TimeoutExpired:
                early_exit = process.poll()
            finally:
                _terminate_tree(process)
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    _terminate_tree(process, force=True)
                    stdout, stderr = process.communicate(timeout=5)
        if early_exit is not None:
            raise RuntimeError(f"O processo terminou antes do fim da verificação ({early_exit}).\n{stdout}{stderr}")
        if "Traceback (most recent call last)" in stdout + stderr:
            raise RuntimeError(f"O arranque produziu uma exceção Python.\n{stdout}{stderr}")
        return StartupResult(stdout, stderr)


def _positive_seconds(value: str) -> float:
    """Valida a duração recebida pela linha de comandos."""
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("A duração deve ser positiva e finita.")
    return seconds


def main(arguments: Sequence[str] | None = None) -> int:
    """Verifica um executável e devolve um código adequado a verificações automáticas."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path, help="Caminho do executável produzido por build.py.")
    parser.add_argument("--seconds", type=_positive_seconds, default=5.0, help="Duração do arranque, em segundos.")
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT, help="Raiz das fontes para comparar recursos.")
    options = parser.parse_args(arguments)
    try:
        executable = options.executable.resolve(strict=True)
        verify_bundle_resources(executable, options.source_root.resolve())
        result = check_startup([str(executable)], options.seconds)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Falhou a verificação: {error}")
        return 1
    print("Recursos empacotados confirmados; arranque isolado concluído sem término prematuro.")
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    print("Esta verificação não confirma interação, posicionamento ou monitores físicos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
