# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller macOS 配置 - Clean Build
"""

import os
import sys
from pathlib import Path

# ============================================
# 项目配置
# ============================================
APP_NAME = 'AnimalNumberLedger'
APP_VERSION = '1.2.2'
BUNDLE_ID = 'com.animalnumberledger.app'
APP_DISPLAY_NAME = '十二动物号码归纳器'

# ============================================
# 路径配置（使用绝对路径）
# ============================================
# spec文件在 packaging/ 目录下
SPEC_DIR = os.path.abspath(SPECPATH)
PROJECT_ROOT = os.path.dirname(SPEC_DIR)

print("="*60)
print("PyInstaller 配置信息")
print("="*60)
print(f"项目根目录: {PROJECT_ROOT}")
print(f"Spec目录: {SPEC_DIR}")
print(f"Python版本: {sys.version}")
print(f"平台: {sys.platform}")
print("="*60)

# ============================================
# 数据文件收集
# ============================================
datas = []

# 1. assets 目录（包含所有JSON配置）
assets_path = os.path.join(PROJECT_ROOT, 'assets')
if os.path.exists(assets_path):
    print(f"\n收集 assets 目录...")
    for root, dirs, files in os.walk(assets_path):
        for file in files:
            src = os.path.join(root, file)
            # 保持相对路径结构
            rel_dir = os.path.relpath(root, PROJECT_ROOT)
            datas.append((src, rel_dir))
            print(f"  + {os.path.relpath(src, PROJECT_ROOT)}")
else:
    print(f"\n警告: assets 目录不存在: {assets_path}")

# 2. 必需的Python模块文件（作为数据文件包含，确保运行时可访问）
essential_files = [
    'constants.py',
    'format_utils.py',
    'platform_paths.py',
    'platform_fonts.py',
    'head_filter.py',
]

print(f"\n收集必需模块...")
for filename in essential_files:
    filepath = os.path.join(PROJECT_ROOT, filename)
    if os.path.exists(filepath):
        datas.append((filepath, '.'))
        print(f"  + {filename}")

print(f"\n数据文件总数: {len(datas)}")

# ============================================
# 隐藏导入（确保所有运行时模块被打包）
# ============================================
hiddenimports = [
    # GUI框架
    'customtkinter',
    'tkinter',
    'tkinter.ttk',
    'PIL',
    'PIL._imagingtk',
    'PIL._tkinter_finder',

    # 数据库
    'sqlite3',

    # 核心业务模块
    'database',
    'models',
    'constants',
    'format_utils',
    'platform_paths',
    'platform_fonts',

    # 计算器
    'calculator',
    'calculator_factory',
    'number_calculator',
    'animal_calculator',

    # 解析器
    'parser',
    'play_group_parser',
    'play_mode',
    'play_mode_config',
    'flat_zodiac_parser',
    'flat_zodiac_service',

    # 业务逻辑
    'daily_rollover',
    'settlement',
    'backup',
    'head_filter',

    # UI模块
    'ui',
    'ui.main_window',
    'ui.history_window',
    'ui.settlement_window',
    'ui.mapping_window',
    'ui.result_canvas_table',
    'ui.result_table',
    'ui.animal_result_table',
    'ui.delete_dialog',
]

print(f"\n隐藏导入模块数: {len(hiddenimports)}")

# ============================================
# 排除模块（减小包体积）
# ============================================
excludes = [
    'test',
    'tests',
    'pytest',
    'unittest',
    'email',
    'http',
    'xml',
    'pydoc',
    'doctest',
    'argparse',
    'difflib',
    'inspect',
    'darkdetect',  # 避免兼容性问题
]

# ============================================
# Analysis 阶段
# ============================================
print(f"\n开始分析...")
a = Analysis(
    [os.path.join(PROJECT_ROOT, 'app.py')],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ============================================
# PYZ 阶段
# ============================================
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ============================================
# EXE 阶段
# ============================================
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
    console=False,  # GUI应用，不显示控制台
    disable_windowed_traceback=False,
    target_arch=None,  # 自动检测架构
    codesign_identity=None,
    entitlements_file=None,
)

# ============================================
# COLLECT 阶段
# ============================================
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

# ============================================
# BUNDLE 阶段 - 创建 macOS .app
# ============================================
app = BUNDLE(
    coll,
    name=f'{APP_NAME}.app',
    icon=None,
    bundle_identifier=BUNDLE_ID,
    version=APP_VERSION,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_DISPLAY_NAME,
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleVersion': APP_VERSION,
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': APP_NAME,
        'CFBundleIdentifier': BUNDLE_ID,
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.13.0',
        'NSHumanReadableCopyright': f'© 2024 {APP_NAME}',
    },
)

print("="*60)
print("配置完成")
print("="*60)
