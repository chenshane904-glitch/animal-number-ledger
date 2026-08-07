# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller macOS 配置 - 重构版
确保所有资源文件从assets目录正确打包
"""

import os
from pathlib import Path

# 项目信息
APP_NAME = 'AnimalNumberLedger'
APP_VERSION = '1.2.2'
BUNDLE_IDENTIFIER = 'com.animalnumberledger.app'

# 获取项目根目录
spec_root = os.path.abspath(SPECPATH)
project_root = os.path.dirname(spec_root)

print(f"=== PyInstaller 配置 ===")
print(f"项目根目录: {project_root}")
print(f"Spec目录: {spec_root}")

# 收集所有需要打包的数据文件
datas = []

# 1. assets目录（包含所有JSON配置文件）
assets_dir = os.path.join(project_root, 'assets')
if os.path.exists(assets_dir):
    print(f"\n✓ 找到 assets 目录: {assets_dir}")
    # 递归添加assets目录下的所有文件
    for root, dirs, files in os.walk(assets_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # 计算相对路径
            rel_path = os.path.relpath(file_path, project_root)
            # 目标路径保持相同的目录结构
            dest_dir = os.path.dirname(rel_path)
            datas.append((file_path, dest_dir))
            print(f"  + {rel_path}")
else:
    print(f"\n✗ 警告: assets 目录不存在")

# 2. 必需的Python模块文件
required_modules = [
    'constants.py',
    'format_utils.py',
    'platform_paths.py',
    'platform_fonts.py',
    'head_filter.py',
]

print(f"\n包含必需模块:")
for filename in required_modules:
    filepath = os.path.join(project_root, filename)
    if os.path.exists(filepath):
        datas.append((filepath, '.'))
        print(f"  ✓ {filename}")
    else:
        print(f"  ✗ {filename} (不存在)")

# 隐藏导入 - 确保所有运行时需要的模块都被包含
hiddenimports = [
    # UI框架
    'customtkinter',
    'PIL',
    'PIL._imagingtk',
    'PIL._tkinter_finder',

    # 数据库
    'sqlite3',

    # 项目核心模块
    'database',
    'calculator',
    'calculator_factory',
    'number_calculator',
    'animal_calculator',
    'flat_zodiac_parser',
    'flat_zodiac_service',
    'play_mode',
    'play_mode_config',
    'play_group_parser',
    'daily_rollover',
    'parser',
    'models',
    'backup',
    'settlement',
    'head_filter',

    # UI模块
    'ui',
    'ui.main_window',
    'ui.history_window',
    'ui.settlement_window',
    'ui.mapping_window',
    'ui.result_canvas_table',
    'ui.delete_dialog',
]

print(f"\n隐藏导入模块数量: {len(hiddenimports)}")

# 排除不需要的模块（减小体积）
excludes = [
    'tkinter.test',
    'unittest',
    'email',
    'http',
    'xml',
    'darkdetect',  # customtkinter会自动降级到默认模式
    'test',
    'tests',
]

# 分析阶段
print(f"\n开始分析...")
a = Analysis(
    [os.path.join(project_root, 'app.py')],  # 使用app.py作为入口
    pathex=[project_root],
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

# 打包Python字节码
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建可执行文件
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
    console=False,  # macOS GUI应用，不显示控制台
    disable_windowed_traceback=False,
    target_arch=None,  # 自动检测当前架构
    codesign_identity=None,
    entitlements_file=None,
)

# 收集所有文件
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

# 创建macOS应用包
app = BUNDLE(
    coll,
    name=f'{APP_NAME}.app',
    icon=None,  # 可以后续添加图标
    bundle_identifier=BUNDLE_IDENTIFIER,
    version=APP_VERSION,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': '十二动物号码归纳器',
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleVersion': APP_VERSION,
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': APP_NAME,
        'CFBundleIdentifier': BUNDLE_IDENTIFIER,
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # 支持暗色模式
        'LSMinimumSystemVersion': '10.13.0',  # macOS 10.13+
        'NSHumanReadableCopyright': '© 2024 AnimalNumberLedger',
    },
)

print(f"\n=== 配置完成 ===")
print(f"应用名称: {APP_NAME}")
print(f"版本: {APP_VERSION}")
print(f"Bundle ID: {BUNDLE_IDENTIFIER}")
