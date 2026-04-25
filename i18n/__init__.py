"""
Internacionalização (i18n) da aplicação Chronometer.

Usa gettext para suportar múltiplos idiomas.
Idiomas suportados: pt_PT (Portugal), en_US (English)
"""

import builtins
import gettext
import locale
from pathlib import Path

# Localizar pasta de traduções
LOCALE_DIR = Path(__file__).resolve().parent / "locales"

# Idioma atualmente ativo
_current_language: str | None = None


def _get_system_language() -> str:
    """
    Retorna o idioma do sistema no formato 'pt_PT' ou 'en_US'.
    Fallback para 'pt_PT' se não conseguir determinar.
    """
    try:
        lang, _ = locale.getdefaultlocale()
        if lang:
            # Converter 'pt' para 'pt_PT', 'en' para 'en_US', etc.
            if lang.startswith('pt'):
                return 'pt_PT'
            elif lang.startswith('en'):
                return 'en_US'
            else:
                # Se outro idioma, tentar manter o formato ou fallback
                return lang.replace('-', '_') if '_' in lang or '-' in lang else 'pt_PT'
    except Exception:
        pass
    return 'pt_PT'


def get_current_language() -> str:
    """Retorna o idioma atualmente ativo."""
    global _current_language
    return _current_language or _get_system_language()


def setup_i18n(lang: str | None = None) -> str:
    """
    Configura gettext para o idioma especificado.
    
    Args:
        lang: Idioma no formato 'pt_PT', 'en_US', etc. Se None, detecta do sistema.
    
    Returns:
        O idioma efetivamente configurado.
    """
    global _current_language
    
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
    except Exception as e:
        # Fallback: usar identidade (sem tradução)
        builtins.__dict__['_'] = lambda x: x
    
    return lang
