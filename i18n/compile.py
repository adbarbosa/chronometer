#!/usr/bin/env python3
"""
Compilador robusto de .po para .mo usando polib.
"""

import sys
from pathlib import Path

try:
    import polib
except ImportError:
    print("ERRO: polib não instalado. Use: pip install polib")
    sys.exit(1)


def compile_po(po_path: Path, mo_path: Path):
    """Compila um PO para MO usando polib."""
    print(f"Compilando {po_path.name}...", end=' ')
    
    # Parse PO
    po = polib.pofile(str(po_path))
    
    # Save MO
    mo_path.parent.mkdir(parents=True, exist_ok=True)
    po.save_as_mofile(str(mo_path))
    
    # Contar strings (excluindo header)
    num_entries = len([e for e in po if str(e.msgid)])
    
    mo_size = mo_path.stat().st_size
    print(f"✓ ({mo_size} bytes, {num_entries} mensagens)")


if __name__ == '__main__':
    i18n_dir = Path(__file__).parent
    
    print("Compilando traduções com polib...\n")
    
    try:
        compile_po(
            i18n_dir / 'pt_PT.po',
            i18n_dir / 'locales' / 'pt_PT' / 'LC_MESSAGES' / 'chronometer.mo'
        )
        
        compile_po(
            i18n_dir / 'en_US.po',
            i18n_dir / 'locales' / 'en_US' / 'LC_MESSAGES' / 'chronometer.mo'
        )
        
        print("\n✓ Compilação concluída com sucesso!")
    except Exception as e:
        print(f"\n✗ ERRO: {e}", file=sys.stderr)
        sys.exit(1)
