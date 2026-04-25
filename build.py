import PyInstaller.__main__
import sys
import os
import platform

def build():
    """
    Script para automatizar o processo de build do Chronometer usando PyInstaller.
    Garante que os recursos (ícones e traduções) sejam incluídos corretamente.
    """
    app_name = "Chronometer"
    
    # Determina o separador de caminhos para o PyInstaller (';' no Windows, ':' no Linux)
    sep = ';' if platform.system() == 'Windows' else ':'
    
    # Define os ficheiros de dados a incluir: (origem;destino)
    # Nota: O destino deve ser relativo à raiz do pacote ou ao local onde o script é executado
    # Para que o i18n/__init__.py encontre os ficheiros, o destino deve manter a estrutura
    datas = [
        (f"chronometer/i18n/locales{sep}i18n/locales"),
        (f"icon{sep}icon"),
    ]
    
    # Constrói os argumentos do PyInstaller
    # Usamos chronometer/__main__.py como ponto de entrada
    args = [
        'chronometer/__main__.py',
        f'--name={app_name}',
        '--onefile',
        '--windowed',
    ]
    
    # Adiciona o ícone (se existir)
    icon_path = "icon/chronometer-stopwatch-svgrepo-com.ico"
    if os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')
    
    # Adiciona os dados (traduções e ícones)
    for src, dest in datas:
        args.append(f'--add-data={src}')
    
    print(f"🚀 A iniciar build para {platform.system()}...")
    print(f"🛠️ Argumentos: {' '.join(args)}")
    
    try:
        PyInstaller.__main__.run(args)
        print(f"\n✅ Build concluído com sucesso! Verifique a pasta 'dist/'.")
    except Exception as e:
        print(f"\n❌ Erro durante o build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
