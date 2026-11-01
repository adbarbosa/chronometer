"""Gestor de configurações persistentes para Chronometer."""

import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any

from PyQt6.QtCore import QLockFile


def config_directory() -> Path:
    """Permite isolar execuções de verificação sem alterar a pasta pessoal."""
    override = os.environ.get("CHRONOMETER_CONFIG_DIR")
    return Path(override).expanduser() if override else Path.home() / ".chronometer"


class ConfigManager:
    """Gere preferências normalizadas e serializa as gravações entre processos."""

    CONFIG_DIR = config_directory()
    CONFIG_FILE = CONFIG_DIR / "config.json"
    LOCK_TIMEOUT_MS = 250

    DEFAULTS = {
        "last_monitor_index": 1,
        "last_monitor_id": None,
        "language": None,
        "dark_mode": False,
    }
    LANGUAGE_NAMES = {
        "pt_PT": "Português (PT)",
        "en_US": "English (US)",
    }
    SUPPORTED_LANGUAGES = list(LANGUAGE_NAMES)
    DEFAULT_LANGUAGE = "pt_PT"

    @staticmethod
    def _monitor_index(value: Any, default: int = 1) -> int:
        """Aceita índices inteiros não negativos e texto decimal de versões anteriores."""
        try:
            if isinstance(value, bool):
                return default
            if isinstance(value, str):
                value = value.strip()
                if not value.removeprefix("+").isdecimal():
                    return default
            elif isinstance(value, float):
                if not math.isfinite(value) or not value.is_integer():
                    return default
            elif not isinstance(value, int):
                return default
            index = int(value)
            return index if index >= 0 else default
        except (ValueError, OverflowError):
            return default

    @classmethod
    def _normalize_config(cls, config: dict[str, Any], monitor_index_default: int = 1) -> dict[str, Any]:
        """Valida campos conhecidos sem eliminar chaves de versões futuras."""
        result = cls.DEFAULTS | config
        result["last_monitor_index"] = cls._monitor_index(result["last_monitor_index"], monitor_index_default)
        monitor_id = result["last_monitor_id"]
        result["last_monitor_id"] = monitor_id.strip() or None if isinstance(monitor_id, str) else None
        language = result["language"]
        language = language.strip().replace("-", "_") if isinstance(language, str) else None
        result["language"] = language if language in cls.LANGUAGE_NAMES else None
        if not isinstance(result["dark_mode"], bool):
            result["dark_mode"] = cls.DEFAULTS["dark_mode"]
        return result

    @classmethod
    def _load_config(cls, monitor_index_default: int = 1) -> dict[str, Any]:
        """Carrega e normaliza JSON; ficheiros ausentes ou inválidos usam os valores por defeito."""
        try:
            if not cls.CONFIG_FILE.exists():
                return cls.DEFAULTS.copy()
            with cls.CONFIG_FILE.open("r", encoding="utf-8") as stream:
                config = json.load(stream)
            if not isinstance(config, dict):
                raise ValueError("o conteúdo não é um objeto JSON")
            return cls._normalize_config(config, monitor_index_default)
        except (ValueError, OSError) as error:
            print(f"⚠️ Erro ao carregar configurações: {error}. A usar os valores por defeito.")
            return cls.DEFAULTS.copy()

    @classmethod
    def _save_config(cls, config: dict[str, Any]) -> bool:
        """Escreve um temporário exclusivo e substitui o ficheiro apenas após concluir a escrita."""
        temporary_file: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=cls.CONFIG_FILE.parent,
                prefix=f".{cls.CONFIG_FILE.name}.", suffix=".tmp", delete=False,
            ) as stream:
                temporary_file = Path(stream.name)
                json.dump(config, stream, indent=2, ensure_ascii=False, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_file, cls.CONFIG_FILE)
            return True
        except (OSError, TypeError, ValueError) as error:
            print(f"⚠️ Erro ao guardar configurações: {error}")
            return False
        finally:
            if temporary_file is not None:
                try:
                    temporary_file.unlink(missing_ok=True)
                except OSError:
                    # Uma pasta inacessível também pode impedir a limpeza do temporário.
                    pass

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Obtém uma preferência normalizada ou o valor indicado para uma chave ausente."""
        return cls._load_config().get(key, default)

    @classmethod
    def save(cls, key: str, value: Any) -> bool:
        """Protege a transação ler–alterar–guardar e informa se a atualização foi persistida."""
        try:
            cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            print(f"⚠️ Erro ao criar a pasta de configurações: {error}")
            return False
        lock = QLockFile(str(cls.CONFIG_FILE.with_suffix(".json.lock").resolve()))
        # Um escritor ativo não deve perder o bloqueio por uma demora no sistema de ficheiros.
        lock.setStaleLockTime(0)
        if not lock.tryLock(cls.LOCK_TIMEOUT_MS):
            print("⚠️ Não foi possível obter o bloqueio para guardar as configurações.")
            return False
        try:
            config = cls._load_config()
            config[key] = value
            return cls._save_config(cls._normalize_config(config))
        finally:
            lock.unlock()

    @classmethod
    def get_last_monitor_index(cls, default: int = 1) -> int:
        """Obtém o índice legado, usando uma alternativa para entradas inválidas."""
        return cls._load_config(monitor_index_default=default)["last_monitor_index"]

    @classmethod
    def save_monitor_index(cls, index: int) -> bool:
        """Guarda o índice legado do monitor e indica se a escrita terminou."""
        return cls.save("last_monitor_index", index)

    @classmethod
    def get_last_monitor_id(cls) -> str | None:
        """Obtém a identidade normalizada do último monitor aberto."""
        return cls.get("last_monitor_id")

    @classmethod
    def save_monitor_id(cls, monitor_id: str) -> bool:
        """Guarda a identidade do monitor e indica se a escrita terminou."""
        return cls.save("last_monitor_id", monitor_id)

    @classmethod
    def get_language(cls) -> str | None:
        """Obtém um idioma registado ou None para deteção automática."""
        return cls.get("language")

    @classmethod
    def save_language(cls, lang: str | None) -> bool:
        """Guarda um idioma normalizado ou a escolha automática e informa o resultado."""
        return cls.save("language", lang)

    @classmethod
    def get_dark_mode(cls) -> bool:
        """Obtém uma preferência de tema estritamente booleana."""
        return cls.get("dark_mode", cls.DEFAULTS["dark_mode"])

    @classmethod
    def save_dark_mode(cls, enabled: bool) -> bool:
        """Guarda a escolha do tema e informa se a escrita terminou."""
        return cls.save("dark_mode", enabled)
