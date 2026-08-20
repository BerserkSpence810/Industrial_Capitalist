# -*- mode: python ; coding: utf-8 -*-

import os


# machines_sheet.png is an optional fallback spritesheet: main.py only loads it
# if it exists on disk. Listing a missing path in datas aborts the build, so
# filter the optional single-file entries down to the ones actually present.
_datas = [('SFX', 'SFX'), ('assets', 'assets'), ('data', 'data'),
          ('machines_sheet.png', '.'), ('materials_32.png', '.')]
_datas = [(src, dst) for src, dst in _datas if os.path.exists(src)]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=_datas,
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
    name='IndustrialCapitalist',
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
)
app = BUNDLE(
    exe,
    name='IndustrialCapitalist.app',
    icon=None,
    bundle_identifier=None,
)
