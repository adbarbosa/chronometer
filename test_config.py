#!/usr/bin/env python3
"""Teste da funcionalidade ConfigManager."""

import json
import os
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from functools import wraps
from pathlib import Path
from time import monotonic, sleep

import pytest
from PyQt6.QtCore import QLockFile

# Adicionar caminho ao módulo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chronometer.config import ConfigManager, config_directory  # pylint: disable=wrong-import-position


def isolated_config_test(test_function):
    """Executa cada teste com um ficheiro de configuração temporário."""
    @wraps(test_function)
    def wrapper(*args, **kwargs):
        """Substitui os caminhos reais apenas durante a execução deste teste."""
        original_dir = ConfigManager.CONFIG_DIR
        original_file = ConfigManager.CONFIG_FILE
        with tempfile.TemporaryDirectory() as temp_dir:
            ConfigManager.CONFIG_DIR = Path(temp_dir)
            ConfigManager.CONFIG_FILE = ConfigManager.CONFIG_DIR / "config.json"
            try:
                return test_function(*args, **kwargs)
            finally:
                ConfigManager.CONFIG_DIR = original_dir
                ConfigManager.CONFIG_FILE = original_file

    return wrapper


@isolated_config_test
def test_save_and_load():
    """Teste: guardar e carregar preferência de monitor."""
    print("🧪 Teste 1: Guardar e carregar preferência de monitor")

    # Guardar índice 2
    ConfigManager.save_monitor_index(2)
    loaded = ConfigManager.get_last_monitor_index()

    assert loaded == 2, f"Esperado 2, obtido {loaded}"
    print(f"  ✅ Guardou índice 2, carregou: {loaded}")


@isolated_config_test
def test_default_value():
    """Teste: valor por defeito."""
    print("\n🧪 Teste 2: Obter valor por defeito")

    # Limpar ficheiro
    if ConfigManager.CONFIG_FILE.exists():
        ConfigManager.CONFIG_FILE.unlink()

    loaded = ConfigManager.get_last_monitor_index(default=1)
    assert loaded == 1, f"Esperado 1 (default), obtido {loaded}"
    print(f"  ✅ Valor por defeito funcionando: {loaded}")


@isolated_config_test
def test_type_conversion():
    """Teste: conversão de tipo."""
    print("\n🧪 Teste 3: Conversão de tipo (string para int)")

    # Guardar como string (simulando ficheiro corrompido)
    ConfigManager.save("last_monitor_index", "3")
    loaded = ConfigManager.get_last_monitor_index()

    assert isinstance(loaded, int), f"Esperado int, obtido {type(loaded)}"
    assert loaded == 3, f"Esperado 3, obtido {loaded}"
    print(f"  ✅ Conversão bem-sucedida: string '3' → int {loaded}")


def test_config_file_location(monkeypatch, tmp_path):
    """A configuração por defeito pertence à pasta pessoal, sem a ler ou alterar."""
    monkeypatch.delenv("CHRONOMETER_CONFIG_DIR", raising=False)
    assert config_directory() == Path.home() / ".chronometer"
    monkeypatch.setenv("CHRONOMETER_CONFIG_DIR", str(tmp_path))
    assert config_directory() == tmp_path


@isolated_config_test
def test_generic_get_save():
    """Teste: métodos genéricos get/save."""
    print("\n🧪 Teste 5: Métodos genéricos get/save")

    # Guardar uma chave customizada
    ConfigManager.save("test_key", "test_value")
    loaded = ConfigManager.get("test_key")

    assert loaded == "test_value", f"Esperado 'test_value', obtido {loaded}"
    print(f"  ✅ Guardou e carregou chave customizada: {loaded}")


def test_supported_languages_match_names():
    """Teste: lista de idiomas suportados derivada dos nomes."""
    assert ConfigManager.SUPPORTED_LANGUAGES == list(ConfigManager.LANGUAGE_NAMES)
    assert ConfigManager.DEFAULT_LANGUAGE in ConfigManager.SUPPORTED_LANGUAGES
    print("✓ Idiomas suportados consistentes")


@pytest.mark.parametrize("raw", ['{invalid', '[]', 'null'])
def test_invalid_json_uses_defaults(raw, tmp_path, monkeypatch):
    """JSON inválido ou sem objeto usa os valores por defeito sem apagar o ficheiro."""
    path = tmp_path / "config.json"
    path.write_text(raw, encoding="utf-8")
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", path)
    assert ConfigManager.get_dark_mode() is False
    assert ConfigManager.get_language() is None
    assert path.read_text(encoding="utf-8") == raw


def test_invalid_preference_types(tmp_path, monkeypatch):
    """Tipos inválidos para tema e idioma não chegam à interface."""
    path = tmp_path / "config.json"
    path.write_text('{"dark_mode": "false", "language": 12}', encoding="utf-8")
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", path)
    assert ConfigManager.get_dark_mode() is False
    assert ConfigManager.get_language() is None


def test_failed_replace_preserves_previous_file(tmp_path, monkeypatch):
    """Uma falha na substituição mantém o ficheiro anterior e limpa o temporário."""
    path = tmp_path / "config.json"
    path.write_text('{"dark_mode": false}', encoding="utf-8")
    monkeypatch.setattr(ConfigManager, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", path)

    def deny_replace(_source, _destination):
        """Simula a recusa do sistema ao substituir o ficheiro final."""
        raise PermissionError("Substituição recusada no teste")

    monkeypatch.setattr("chronometer.config.os.replace", deny_replace)
    assert ConfigManager.save_dark_mode(True) is False
    assert json.loads(path.read_text(encoding="utf-8")) == {"dark_mode": False}
    assert not list(tmp_path.glob("*.tmp"))


def test_unwritable_directory_does_not_crash(tmp_path, monkeypatch):
    """Uma pasta que não pode ser criada não termina a aplicação."""
    path = tmp_path / "not-a-directory"
    path.write_text("ocupado", encoding="utf-8")
    monkeypatch.setattr(ConfigManager, "CONFIG_DIR", path)
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", path / "config.json")
    assert ConfigManager.save_dark_mode(True) is False
    assert path.read_text(encoding="utf-8") == "ocupado"


@pytest.mark.parametrize("value", [float("inf"), float("nan"), -1, True, False, 2.5, [], "-2"])
def test_invalid_monitor_indices_use_default(value, tmp_path, monkeypatch):
    """Índices inválidos não causam exceções nem escolhem um monitor por coerção."""
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"last_monitor_index": value}), encoding="utf-8")
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", path)
    assert ConfigManager.get_last_monitor_index() == 1


@pytest.mark.parametrize("value", ["", "  ", "unknown", "fr_FR", 12])
def test_invalid_saved_language_uses_automatic(value, tmp_path, monkeypatch):
    """Um código vazio ou não registado passa a deteção automática de idioma."""
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"language": value}), encoding="utf-8")
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", path)
    assert ConfigManager.get_language() is None


def test_save_normalizes_known_fields_and_preserves_unknown(tmp_path, monkeypatch):
    """Guardar normaliza preferências conhecidas sem perder chaves de outras versões."""
    path = tmp_path / "config.json"
    path.write_text(
        '{"dark_mode": "false", "language": " en_US ", "last_monitor_index": "3", "future": 42}',
        encoding="utf-8",
    )
    monkeypatch.setattr(ConfigManager, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", path)
    assert ConfigManager.save("another", 7) is True
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["dark_mode"] is False
    assert stored["language"] == "en_US"
    assert stored["last_monitor_index"] == 3
    assert stored["future"] == 42
    assert stored["another"] == 7


def test_save_returns_false_when_lock_is_held(tmp_path, monkeypatch):
    """A espera pelo bloqueio é limitada e não substitui o ficheiro se estiver ocupado."""
    path = tmp_path / "config.json"
    path.write_text('{"dark_mode": false}', encoding="utf-8")
    monkeypatch.setattr(ConfigManager, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", path)
    monkeypatch.setattr(ConfigManager, "LOCK_TIMEOUT_MS", 20)
    held = QLockFile(str(path.with_suffix(".json.lock")))
    assert held.tryLock(0)
    try:
        assert ConfigManager.save_dark_mode(True) is False
        assert json.loads(path.read_text(encoding="utf-8")) == {"dark_mode": False}
    finally:
        held.unlock()


def test_concurrent_processes_preserve_all_updates(tmp_path):
    """Processos sobrepostos conservam alterações independentes e um JSON final completo."""
    worker = '''from pathlib import Path
import sys
from time import sleep
sys.path.insert(0, sys.argv[1])
from chronometer.config import ConfigManager
ConfigManager.LOCK_TIMEOUT_MS = 3000
original = ConfigManager._load_config.__func__
def slow_load(cls):
    """Alarga a janela de concorrência dentro da transação protegida."""
    data = original(cls)
    sleep(0.15)
    return data
ConfigManager._load_config = classmethod(slow_load)
Path(sys.argv[3]).write_text("pronto", encoding="utf-8")
while not Path(sys.argv[4]).exists():
    sleep(0.01)
sys.exit(0 if ConfigManager.save(sys.argv[2], True) else 1)
'''
    environment = os.environ.copy()
    environment["CHRONOMETER_CONFIG_DIR"] = str(tmp_path)
    start = tmp_path / "start"
    ready = [tmp_path / f"ready-{index}" for index in range(3)]
    with ExitStack() as stack:
        processes = [
            stack.enter_context(subprocess.Popen(
                [sys.executable, "-c", worker, str(Path(__file__).resolve().parent.parent),
                 f"key-{index}", str(ready[index]), str(start)],
                env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            ))
            for index in range(3)
        ]
        try:
            deadline = monotonic() + 10
            while not all(path.exists() for path in ready):
                assert monotonic() < deadline, "Os processos de teste não ficaram prontos."
                sleep(0.01)
            start.write_text("iniciar", encoding="utf-8")
            for process in processes:
                output, errors = process.communicate(timeout=10)
                assert process.returncode == 0, (output, errors)
            stored = json.loads((tmp_path / "config.json").read_text(encoding="utf-8"))
            assert all(stored[f"key-{index}"] is True for index in range(3))
            assert not list(tmp_path.glob("*.tmp"))
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=5)


def test_invalid_index_respects_explicit_fallback(tmp_path, monkeypatch):
    """A normalização não elimina a alternativa específica pedida pelo chamador."""
    path = tmp_path / "config.json"
    path.write_text('{"last_monitor_index": null}', encoding="utf-8")
    monkeypatch.setattr(ConfigManager, "CONFIG_FILE", path)
    assert ConfigManager.get_last_monitor_index(default=0) == 0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
