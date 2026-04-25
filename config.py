"""Gestor de configurações persistentes para Chronometer."""

import json
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """Gerencia persistência de configurações em ficheiro JSON."""

    CONFIG_DIR = Path.home() / ".chronometer"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    # Valores por defeito
    DEFAULTS = {
        "last_monitor_index": 1,  # Usar segundo monitor se disponível
        "language": None,  # None = usar idioma do sistema
        "dark_mode": False,  # Tema claro por defeito
    }
    
    # Idiomas suportados
    SUPPORTED_LANGUAGES = ["pt_PT", "en_US"]
    DEFAULT_LANGUAGE = "pt_PT"

    @classmethod
    def _ensure_config_dir(cls) -> None:
        """Cria diretório de configuração se não existir."""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _load_config(cls) -> dict:
        """Carrega configurações do ficheiro JSON."""
        cls._ensure_config_dir()

        if not cls.CONFIG_FILE.exists():
            return cls.DEFAULTS.copy()

        try:
            with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Mesclar com defaults para garantir que chaves novas existem
                defaults = cls.DEFAULTS.copy()
                defaults.update(config)
                return defaults
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Erro ao carregar configurações: {e}. Usando defaults.")
            return cls.DEFAULTS.copy()

    @classmethod
    def _save_config(cls, config: dict) -> None:
        """Guarda configurações em ficheiro JSON."""
        cls._ensure_config_dir()

        try:
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"⚠️ Erro ao guardar configurações: {e}")

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
    def get_language(cls) -> str | None:
        """Obtém o idioma configurado (None = usar idioma do sistema)."""
        return cls.get("language", None)

    @classmethod
    def save_language(cls, lang: str | None) -> None:
        """Guarda a preferência de idioma."""
        if lang is not None and lang not in cls.SUPPORTED_LANGUAGES:
            lang = cls.DEFAULT_LANGUAGE
        cls.save("language", lang)

    @classmethod
    def get_dark_mode(cls) -> bool:
        """Obtém a preferência de tema escuro."""
        return cls.get("dark_mode", False)

    @classmethod
    def save_dark_mode(cls, enabled: bool) -> None:
        """Guarda a preferência de tema escuro."""
        cls.save("dark_mode", bool(enabled))
