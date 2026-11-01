"""Gestor de configurações persistentes para Chronometer."""

import json
import os
from pathlib import Path
from typing import Any


def config_directory() -> Path:
    """Permite isolar execuções de verificação sem alterar a pasta pessoal."""
    override = os.environ.get("CHRONOMETER_CONFIG_DIR")
    return Path(override).expanduser() if override else Path.home() / ".chronometer"


class ConfigManager:
    """Gere a persistência de preferências num ficheiro JSON."""

    CONFIG_DIR = config_directory()
    CONFIG_FILE = CONFIG_DIR / "config.json"

    # Valores por defeito
    DEFAULTS = {
        "last_monitor_index": 1,  # Usar segundo monitor se disponível
        "last_monitor_id": None,
        "language": None,  # None = usar idioma do sistema
        "dark_mode": False,  # Tema claro por defeito
    }

    # Idiomas suportados
    LANGUAGE_NAMES = {
        "pt_PT": "Português (PT)",
        "en_US": "English (US)",
    }
    SUPPORTED_LANGUAGES = list(LANGUAGE_NAMES)
    DEFAULT_LANGUAGE = "pt_PT"

    @classmethod
    def _ensure_config_dir(cls) -> None:
        """Cria diretório de configuração se não existir."""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _load_config(cls) -> dict[str, Any]:
        """Carrega configurações do ficheiro JSON."""
        try:
            if not cls.CONFIG_FILE.exists():
                return cls.DEFAULTS.copy()
            with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                if not isinstance(config, dict):
                    raise ValueError("o conteúdo não é um objeto JSON")
                # Completar chaves novas sem eliminar preferências desconhecidas.
                defaults = cls.DEFAULTS.copy()
                defaults.update(config)
                return defaults
        except (json.JSONDecodeError, ValueError, IOError) as e:
            print(f"⚠️ Erro ao carregar configurações: {e}. Usando defaults.")
            return cls.DEFAULTS.copy()

    @classmethod
    def _save_config(cls, config: dict[str, Any]) -> None:
        """Guarda configurações em ficheiro JSON."""
        temporary_file = cls.CONFIG_FILE.with_suffix(".json.tmp")

        try:
            cls._ensure_config_dir()
            with open(temporary_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary_file, cls.CONFIG_FILE)
        except (IOError, OSError) as e:
            print(f"⚠️ Erro ao guardar configurações: {e}")
            try:
                temporary_file.unlink()
            except OSError:
                # A limpeza é uma tentativa: a pasta também pode estar inacessível.
                pass

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Obtém uma configuração pelo nome da chave."""
        config = cls._load_config()
        return config.get(key, default)

    @classmethod
    def save(cls, key: str, value: Any) -> None:
        """Guarda uma configuração."""
        config = cls._load_config()
        config[key] = value
        cls._save_config(config)

    @classmethod
    def get_last_monitor_index(cls, default: int = 1) -> int:
        """Obtém o índice do último monitor aberto."""
        value = cls.get("last_monitor_index", default)
        # Garantir que é inteiro
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @classmethod
    def save_monitor_index(cls, index: int) -> None:
        """Guarda o índice do monitor."""
        cls.save("last_monitor_index", int(index))

    @classmethod
    def get_last_monitor_id(cls) -> str | None:
        """Obtém o identificador persistente do último monitor usado."""
        value = cls.get("last_monitor_id", None)
        return value if isinstance(value, str) and value else None

    @classmethod
    def save_monitor_id(cls, monitor_id: str) -> None:
        """Guarda o identificador persistente do monitor."""
        cls.save("last_monitor_id", str(monitor_id))

    @classmethod
    def get_language(cls) -> str | None:
        """Obtém o idioma configurado (None = usar idioma do sistema)."""
        language = cls.get("language", None)
        return language if isinstance(language, str) else None

    @classmethod
    def save_language(cls, lang: str | None) -> None:
        """Guarda a preferência de idioma."""
        if lang is not None and lang not in cls.SUPPORTED_LANGUAGES:
            lang = cls.DEFAULT_LANGUAGE
        cls.save("language", lang)

    @classmethod
    def get_dark_mode(cls) -> bool:
        """Obtém a preferência de tema escuro."""
        dark_mode = cls.get("dark_mode", False)
        return dark_mode if isinstance(dark_mode, bool) else cls.DEFAULTS["dark_mode"]

    @classmethod
    def save_dark_mode(cls, enabled: bool) -> None:
        """Guarda a preferência de tema escuro."""
        cls.save("dark_mode", bool(enabled))
