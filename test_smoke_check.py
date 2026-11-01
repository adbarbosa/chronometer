"""Verifica o diagnóstico de arranque sem compilar a aplicação durante os testes unitários."""

import json
from pathlib import Path
import sys

import pytest
from PyInstaller.archive.writers import CArchiveWriter

from chronometer.smoke_check import BUNDLED_RESOURCES, check_startup, verify_bundle_resources


@pytest.mark.parametrize("exit_code", [0, 7])
def test_early_exit_is_a_failure(exit_code):
    """Um processo que termina imediatamente não conta como um arranque funcional."""
    with pytest.raises(RuntimeError, match="terminou antes"):
        check_startup([sys.executable, "-c", f"raise SystemExit({exit_code})"], seconds=1)


def test_startup_uses_temporary_preferences_outside_checkout(tmp_path, monkeypatch):
    """O filho usa preferências e pasta de trabalho temporárias, preservando o ambiente anterior."""
    original = tmp_path / "original"
    original.mkdir()
    sentinel = original / "config.json"
    sentinel.write_text('{"sentinel": true}', encoding="utf-8")
    monkeypatch.setenv("CHRONOMETER_CONFIG_DIR", str(original))
    child = '''import json
import os
from pathlib import Path
import time
preferences = Path(os.environ["CHRONOMETER_CONFIG_DIR"])
assert preferences != Path(os.environ["EXPECTED_ORIGINAL"])
(preferences / "child.json").write_text("temporário", encoding="utf-8")
print(json.dumps({"cwd": str(Path.cwd()), "preferences": str(preferences), "backend": os.environ["QT_QPA_PLATFORM"]}), flush=True)
time.sleep(30)
'''
    monkeypatch.setenv("EXPECTED_ORIGINAL", str(original))
    result = check_startup([sys.executable, "-c", child], seconds=1)
    report = json.loads(result.stdout)
    assert report["backend"] == "offscreen"
    assert Path(report["cwd"]) != Path(__file__).resolve().parent
    assert Path(report["preferences"]) != original
    assert not Path(report["cwd"]).exists()
    assert not Path(report["preferences"]).exists()
    assert sentinel.read_text(encoding="utf-8") == '{"sentinel": true}'
    assert not (original / "child.json").exists()


def test_startup_terminates_child_process_tree():
    """Um neto que conserva os pipes abertos não fica vivo após a limpeza do processo principal."""
    child = '''import subprocess
import sys
import time
subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
print("filho criado", flush=True)
time.sleep(30)
'''
    result = check_startup([sys.executable, "-c", child], seconds=1)
    assert "filho criado" in result.stdout


@pytest.mark.parametrize("windows_names", [False, True])
def test_bundle_bytes_and_path_separators(tmp_path, windows_names):
    """A comparação lê um arquivo real e aceita os separadores usados por ambos os sistemas."""
    entries = []
    for relative_path in BUNDLED_RESOURCES:
        source = tmp_path / relative_path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(relative_path.encode("utf-8"))
        archive_name = relative_path.replace("/", "\\") if windows_names else relative_path
        entries.append((archive_name, str(source), True, "x"))
    archive = tmp_path / "sample.pkg"
    CArchiveWriter(str(archive), entries, pylib_name="python-test")
    verify_bundle_resources(archive, tmp_path)
    (tmp_path / BUNDLED_RESOURCES[0]).write_bytes(b"alterado depois do build")
    with pytest.raises(ValueError, match="desatualizado"):
        verify_bundle_resources(archive, tmp_path)
