import PyInstaller.__main__
import sys
import os
import platform
from pathlib import Path

def build():
    """
    Script para automatizar o processo de build do Chronometer usando PyInstaller.
    Garante que os recursos (ícones e traduções) sejam incluídos corretamente.
    """
    # Determina o diretório onde o script build.py está localizado
    script_dir = Path(__file__).resolve().parent
    
    app_name = "Chronometer"
    
    # Determina o separador de caminhos para o PyInstaller (';' no Windows, ':' no Linux)
    sep = ';' if platform.system() == 'Windows' else ':'
    
    # Define os ficheiros de dados a incluir: (origem, destino)
    # Usamos caminhos relativos ao diretório do script
    datas = [
        ("i18n/locales", "i18n/locales"),
        ("icon", "icon"),
    ]
    
    # Constrói os argumentos do PyInstaller
    # O ponto de entrada é o __main__.py que está na mesma pasta que o build.py
    args = [
        '__main__.py',
        f'--name={app_name}',
        '--onefile',
        '--windowed',
    ]
    
    # Adiciona o ícone (se existir)
    icon_path = script_dir / "icon" / "chronometer-stopwatch-svgrepo-com.ico"
    if icon_path.exists():
        args.append(f'--icon={icon_path}')
    
    # Adiciona os dados (traduções e ícones)
    for src, dest in datas:
        # Criamos o caminho absoluto para a origem
        full_src = script_dir / src
        args.append(f'--add-data={full_src}{sep}{dest}')
    
    print(f"🚀 A iniciar build para {platform.system()}...")
    print(f"📂 Diretório de trabalho: {script_dir}")
    print(f"🛠️  Argumentos: {' '.join(args)}")
    
    try:
        # Mudamos para o diretório do script para que o PyInstaller encontre os ficheiros
        os.chdir(script_dir)
        PyInstaller.__main__.run(args)
        print(f"\n✅ Build concluído com sucesso! Verifique a pasta 'dist/'.")
    except Exception as e:
        print(f"\n❌ Erro durante o build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
