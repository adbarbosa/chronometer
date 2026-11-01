"""
Internacionalização (i18n) da aplicação Chronometer.

Usa gettext para suportar múltiplos idiomas.
Idiomas suportados: pt_PT (Portugal), en_US (English)
"""

import builtins
import gettext
import struct

from PyQt6.QtCore import QLocale
from chronometer.config import ConfigManager
from chronometer.resources import resource_path

LOCALE_DIR = resource_path("i18n", "locales")

# Idioma atualmente ativo
_current_language: str | None = None


def _get_system_language() -> str:
    """
    Normaliza as variantes de português e inglês e conserva outros códigos regionais.
    Usa 'pt_PT' quando o idioma do sistema não pode ser determinado.
    """
    try:
        lang = QLocale.system().name()
        if lang and lang != 'C':
            # Converter 'pt' para 'pt_PT', 'en' para 'en_US', etc.
            if lang.startswith('pt'):
                return 'pt_PT'
            if lang.startswith('en'):
                return 'en_US'
            # Se outro idioma, tentar manter o formato ou fallback
            return lang.replace('-', '_') if '_' in lang or '-' in lang else 'pt_PT'
    except Exception:
        pass
    return 'pt_PT'


def _registered_language(lang: str | None) -> str:
    """Normaliza um pedido e resolve códigos não registados para o idioma por defeito."""
    candidate = lang.strip().replace("-", "_") if isinstance(lang, str) else ""
    if not candidate:
        candidate = _get_system_language()
    return candidate if candidate in ConfigManager.LANGUAGE_NAMES else ConfigManager.DEFAULT_LANGUAGE


def get_current_language() -> str:
    """Devolve o idioma aplicado, sem confundir uma preferência vazia com o sistema."""
    return _current_language if _current_language is not None else _registered_language(None)


def setup_i18n(lang: str | None = None) -> str:
    """Instala a tradução disponível e devolve o código realmente apresentado na interface.

    Um pedido vazio usa a deteção do sistema. Se faltar o catálogo pedido ou este
    estiver inválido, tenta português e, em último caso, os textos originais.
    """
    global _current_language  # pylint: disable=global-statement

    requested = _registered_language(lang)
    active = ConfigManager.DEFAULT_LANGUAGE
    translation = gettext.NullTranslations()
    for candidate in dict.fromkeys((requested, ConfigManager.DEFAULT_LANGUAGE)):
        try:
            translation = gettext.translation("chronometer", localedir=str(LOCALE_DIR), languages=[candidate])
            active = candidate
            break
        except (OSError, ValueError, EOFError, struct.error, LookupError):
            # Catálogos ausentes ou danificados não devem impedir o arranque.
            continue
    _current_language = active
    builtins.__dict__["_"] = translation.gettext
    return active
