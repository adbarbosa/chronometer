# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/adb/Development/000_adbtech.pt/python/chronometer/i18n/locales', 'i18n/locales'), ('/home/adb/Development/000_adbtech.pt/python/chronometer/icon', 'icon'), ('/home/adb/Development/000_adbtech.pt/python/chronometer/chronometer.desktop', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Chronometer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/home/adb/Development/000_adbtech.pt/python/chronometer/icon/chronometer-stopwatch-svgrepo-com.ico'],
)
