# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller macOS 配置文件
用于构建 AnimalNumberLedger.app
"""

import os
import sys
from pathlib import Path

# 项目信息
APP_NAME = 'AnimalNumberLedger'
APP_VERSION = '1.22'
BUNDLE_IDENTIFIER = 'com.animalnumberledger.app'

# 构建配置
block_cipher = None

# 获取项目根目录（spec 文件在 packaging/ 目录下）
spec_root = os.path.abspath(SPECPATH)
project_root = os.path.dirname(spec_root)

# 需要包含的数据文件 - 使用绝对路径
datas = []
data_files = [
    'play_modes.json',
    'constants.py',
    'format_utils.py',
    'platform_paths.py',
    'platform_fonts.py',
]

# 动态添加存在的文件
for file in data_files:
    file_path = os.path.join(project_root, file)
    if os.path.exists(file_path):
        datas.append((file_path, '.'))
        print(f"✓ Adding data file: {file}")
    else:
        print(f"✗ Skipping missing file: {file}")

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
    [os.path.join(project_root, 'app.py')],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test',
        'unittest',
        'email',
        'http',
        'urllib',
        'xml',
        'pydoc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ 归档
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# EXE 可执行文件
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

# COLLECT 收集文件
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
    icon=None,
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
        'LSMinimumSystemVersion': '10.13.0',
        'NSHumanReadableCopyright': '© 2026 AnimalNumberLedger',
    },
)
