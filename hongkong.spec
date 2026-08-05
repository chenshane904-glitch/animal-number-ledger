# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_hk.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui', 'ui'),
        ('tests', 'tests'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='香港',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='香港',
)

app = BUNDLE(
    coll,
    name='香港.app',
    icon=None,
    bundle_identifier='com.animalledger.hongkong',
    info_plist={
        'CFBundleName': '香港',
        'CFBundleDisplayName': '香港',
        'CFBundleGetInfoString': '香港',
        'CFBundleIdentifier': 'com.animalledger.hongkong',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': 'True',
    },
)
