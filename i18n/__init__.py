"""
Internacionalização (i18n) da aplicação Chronometer.

Usa gettext para suportar múltiplos idiomas.
Idiomas suportados: pt_PT (Portugal), en_US (English)
"""

import builtins
import gettext

from PyQt6.QtCore import QLocale
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


def get_current_language() -> str:
    """Retorna o idioma atualmente ativo."""
    return _current_language or _get_system_language()


def setup_i18n(lang: str | None = None) -> str:
    """
    Configura gettext para o idioma especificado.

    Args:
        lang: Idioma no formato 'pt_PT', 'en_US', etc. Se None, detecta do sistema.

    Returns:
        O código pedido ou detetado, mesmo quando falta o catálogo e se usam os textos originais.
    """
    global _current_language  # pylint: disable=global-statement

    if lang is None:
        lang = _get_system_language()

    _current_language = lang

    try:
        translation = gettext.translation(
            "chronometer",
            localedir=str(LOCALE_DIR),
            languages=[lang],
            fallback=True
        )
        # Instalar globalmente no builtins para que _() funcione em todo o lado
        builtins.__dict__['_'] = translation.gettext
    except Exception:
        # Fallback: usar identidade (sem tradução)
        builtins.__dict__['_'] = lambda x: x

    return lang
