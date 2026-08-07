# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller macOS 最小化配置
只打包核心 Python 代码，资源动态检测
"""

import os
from pathlib import Path

# 项目信息
APP_NAME = 'AnimalNumberLedger'
APP_VERSION = '1.22'
BUNDLE_IDENTIFIER = 'com.animalnumberledger.app'

# 获取项目根目录
spec_root = os.path.abspath(SPECPATH)
project_root = os.path.dirname(spec_root)

# 动态检测资源文件
datas = []
optional_files = [
    'play_modes.json',
    'constants.py',
    'format_utils.py',
    'platform_paths.py',
    'platform_fonts.py',
]

for filename in optional_files:
    filepath = os.path.join(project_root, filename)
    if os.path.exists(filepath):
        datas.append((filepath, '.'))
        print(f"✓ Including: {filename}")
    else:
        print(f"⊘ Skipping: {filename} (not found)")

# 隐藏导入
hiddenimports = [
    'customtkinter',
    'PIL',
    'PIL._imagingtk',
    'PIL._tkinter_finder',
    'darkdetect',
    'sqlite3',
]

# 分析
a = Analysis(
    [os.path.join(project_root, 'app.py')],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'unittest', 'email', 'http', 'xml'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
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
    name=APP_NAME,
)

app = BUNDLE(
    coll,
    name=f'{APP_NAME}.app',
    icon=None,
    bundle_identifier=BUNDLE_IDENTIFIER,
    version=APP_VERSION,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': '动物号码账本',
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleVersion': APP_VERSION,
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': APP_NAME,
        'CFBundleIdentifier': BUNDLE_IDENTIFIER,
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
