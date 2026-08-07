# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller macOS 配置文件
用于构建 AnimalNumberLedger.app
"""

import sys
from pathlib import Path

# 项目信息
APP_NAME = 'AnimalNumberLedger'
APP_VERSION = '1.22'
BUNDLE_IDENTIFIER = 'com.animalnumberledger.app'

# 构建配置
block_cipher = None

# 需要包含的数据文件
datas = [
    ('play_modes.json', '.'),
    ('constants.py', '.'),
    ('format_utils.py', '.'),
    ('platform_paths.py', '.'),
    ('platform_fonts.py', '.'),
]

# 需要包含的隐藏导入
hiddenimports = [
    'customtkinter',
    'PIL',
    'PIL._imagingtk',
    'PIL._tkinter_finder',
    'darkdetect',
    'sqlite3',
    'database',
    'calculator_factory',
    'number_calculator',
    'animal_calculator',
    'flat_zodiac_parser',
    'flat_zodiac_service',
    'play_mode',
    'daily_rollover',
    'ui.main_window',
    'ui.history_window',
    'ui.animal_result_table',
]

# 分析阶段
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pywin32',
        'win32api',
        'win32con',
        'win32gui',
        'win32com',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ 阶段
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE 阶段（macOS 不直接使用，但 BUNDLE 需要）
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
    console=False,  # 不显示终端窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 收集阶段
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

# macOS App Bundle
app = BUNDLE(
    coll,
    name=f'{APP_NAME}.app',
    icon=None,  # 如果有图标，可以指定 'assets/icon.icns'
    bundle_identifier=BUNDLE_IDENTIFIER,
    version=APP_VERSION,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': '动物号码账本',
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleVersion': APP_VERSION,
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'CFBundleExecutable': APP_NAME,
        'CFBundleIdentifier': BUNDLE_IDENTIFIER,
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra
        'NSHumanReadableCopyright': '© 2026 AnimalNumberLedger',
    },
)
