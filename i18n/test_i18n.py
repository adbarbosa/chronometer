#!/usr/bin/env python3
"""
Script de teste do sistema i18n da aplicação Chronometer.
Valida que as traduções são carregadas corretamente em diferentes idiomas.
"""

import gettext
import sys
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chronometer.i18n import setup_i18n, LOCALE_DIR


def test_language(lang: str, expected_translations: dict) -> bool:
    """
    Testa um idioma específico.
    
    Args:
        lang: Código do idioma (pt_PT, en_US)
        expected_translations: Dict com pares (original, tradução esperada)
    
    Returns:
        True se todos os testes passarem, False caso contrário
    """
    print(f"\n{'='*60}")
    print(f"Testando {lang.upper()}")
    print('='*60)
    
    # Resetar gettext
    gettext._translations = {}
    
    # Setup de i18n
    setup_i18n(lang)
    _ = gettext.gettext
    
    all_passed = True
    
    for original, expected in expected_translations.items():
        translated = _(original)
        passed = translated == expected
        all_passed = all_passed and passed
        
        status = "✓" if passed else "✗"
        print(f"{status} '{original}' → '{translated}'")
        if not passed:
            print(f"  Esperado: '{expected}'")
    
    return all_passed


def main():
    print("\n" + "="*60)
    print("TESTES DE INTERNACIONALIZAÇÃO - Chronometer 0.3.0")
    print("="*60)
    
    # Verificar se os ficheiros .mo existem
    mo_pt = LOCALE_DIR / "pt_PT" / "LC_MESSAGES" / "chronometer.mo"
    mo_en = LOCALE_DIR / "en_US" / "LC_MESSAGES" / "chronometer.mo"
    
    print(f"\nVerificando ficheiros .mo:")
    print(f"  pt_PT: {'✓' if mo_pt.exists() else '✗'} {mo_pt}")
    print(f"  en_US: {'✓' if mo_en.exists() else '✗'} {mo_en}")
    
    if not mo_pt.exists() or not mo_en.exists():
        print("\n✗ Ficheiros .mo não encontrados!")
        return False
    
    # Testes pt_PT
    pt_pt_tests = {
        "Abrir": "Abrir",
        "Fechar": "Fechar",
        "Iniciar": "Iniciar",
        "Parar": "Parar",
        "Repor": "Repor",
        "Chamar Atenção": "Chamar Atenção",
        "Modo Escuro": "Modo Escuro",
        "Modo Claro": "Modo Claro",
        "Control": "Controlo",
        "Output fechado.": "Output fechado.",
    }
    
    # Testes en_US
    en_us_tests = {
        "Abrir": "Open",
        "Fechar": "Close",
        "Iniciar": "Start",
        "Parar": "Stop",
        "Repor": "Reset",
        "Chamar Atenção": "Call Attention",
        "Modo Escuro": "Dark Mode",
        "Modo Claro": "Light Mode",
        "Control": "Control",
        "Output fechado.": "Output closed.",
    }
    
    pt_passed = test_language("pt_PT", pt_pt_tests)
    en_passed = test_language("en_US", en_us_tests)
    
    # Resumo
    print(f"\n{'='*60}")
    print("RESUMO DOS TESTES")
    print('='*60)
    print(f"pt_PT: {'✓ PASSOU' if pt_passed else '✗ FALHOU'}")
    print(f"en_US: {'✓ PASSOU' if en_passed else '✗ FALHOU'}")
    
    if pt_passed and en_passed:
        print("\n✓ TODOS OS TESTES PASSARAM!")
        return True
    else:
        print("\n✗ ALGUNS TESTES FALHARAM")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
