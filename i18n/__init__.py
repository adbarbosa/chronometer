"""
Internacionalização (i18n) da aplicação Chronometer.

Usa gettext para suportar múltiplos idiomas.
Idiomas suportados: pt_PT (Portugal), en_US (English)
"""

import builtins
import gettext
import sys
from pathlib import Path

from PyQt6.QtCore import QLocale

# Localizar pasta de traduções
if getattr(sys, 'frozen', False):
    # Se estiver a correr como um executável compilado (PyInstaller)
    # O PyInstaller extrai os ficheiros para uma pasta temporária definida em sys._MEIPASS
    BASE_DIR = Path(sys._MEIPASS)  # pylint: disable=protected-access
else:
    # Se estiver a correr como script Python normal
    # O __file__ está em chronometer/i18n/__init__.py, por isso o parent.parent é a raiz
    BASE_DIR = Path(__file__).resolve().parent.parent

LOCALE_DIR = BASE_DIR / "i18n" / "locales"

# Idioma atualmente ativo
_current_language: str | None = None


def _get_system_language() -> str:
    """
    Retorna o idioma do sistema no formato 'pt_PT' ou 'en_US'.
    Fallback para 'pt_PT' se não conseguir determinar.
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
        O idioma efetivamente configurado.
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
