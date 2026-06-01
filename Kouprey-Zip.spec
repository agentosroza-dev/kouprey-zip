# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

_ROOT = os.getcwd()

datas = [(os.path.join(_ROOT, 'assets'), 'assets')]
hiddenimports = ['PyQt6.QtSvg', 'patoolib', 'rarfile', 'py7zr', 'cryptography', 'dotenv']
datas += collect_data_files('PyQt6')
hiddenimports += collect_submodules('lucide')

try:
    import lucide
    _lucide_zip = os.path.join(os.path.dirname(lucide.__file__), 'lucide.zip')
    if os.path.isfile(_lucide_zip):
        datas.append((_lucide_zip, 'lucide'))
except Exception:
    pass


a = Analysis(
    [os.path.join(_ROOT, 'main.py')],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='Kouprey-Zip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[os.path.join(_ROOT, 'assets', 'app.ico')],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Kouprey-Zip',
)
