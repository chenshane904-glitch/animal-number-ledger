# -*- coding: utf-8 -*-
"""
跨平台路径管理模块
统一处理 Windows、macOS 和 Linux 的路径
"""
import sys
import os
from pathlib import Path


def get_user_data_dir() -> Path:
    """
    获取用户数据目录

    Windows: C:\\Users\\<用户名>\\AppData\\Roaming\\AnimalNumberLedger
    macOS: ~/Library/Application Support/AnimalNumberLedger
    Linux: ~/.local/share/AnimalNumberLedger
    """
    if sys.platform == 'win32':
        # Windows
        base = Path(os.environ.get('APPDATA', Path.home()))
        app_dir = base / 'AnimalNumberLedger'
    elif sys.platform == 'darwin':
        # macOS
        app_dir = Path.home() / 'Library' / 'Application Support' / 'AnimalNumberLedger'
    else:
        # Linux
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        app_dir = base / 'AnimalNumberLedger'

    # 确保目录存在
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_database_path() -> Path:
    """
    获取数据库文件路径

    Windows: C:\\Users\\<用户名>\\AppData\\Roaming\\AnimalNumberLedger\\ledger.db
    macOS: ~/Library/Application Support/AnimalNumberLedger/ledger.db
    Linux: ~/.local/share/AnimalNumberLedger/ledger.db
    """
    return get_user_data_dir() / 'ledger.db'


def get_log_dir() -> Path:
    """
    获取日志目录

    Windows: C:\\Users\\<用户名>\\AppData\\Roaming\\AnimalNumberLedger\\logs
    macOS: ~/Library/Logs/AnimalNumberLedger
    Linux: ~/.local/share/AnimalNumberLedger/logs
    """
    if sys.platform == 'darwin':
        # macOS 使用系统日志目录
        log_dir = Path.home() / 'Library' / 'Logs' / 'AnimalNumberLedger'
    else:
        # Windows 和 Linux 使用数据目录下的 logs
        log_dir = get_user_data_dir() / 'logs'

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_resource_path(relative_path: str) -> Path:
    """
    获取资源文件路径（支持打包后环境）

    开发环境：从项目目录读取
    PyInstaller 环境：从 _MEIPASS 读取

    Args:
        relative_path: 相对于项目根目录的路径，如 "assets/icon.png"

    Returns:
        资源文件的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后环境
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境
        base_path = Path(__file__).parent

    return base_path / relative_path


def get_config_path(config_name: str) -> Path:
    """
    获取配置文件路径

    Args:
        config_name: 配置文件名，如 "play_modes.json"

    Returns:
        配置文件的绝对路径
    """
    return get_resource_path(config_name)


# 平台信息
PLATFORM = sys.platform
IS_WINDOWS = PLATFORM == 'win32'
IS_MACOS = PLATFORM == 'darwin'
IS_LINUX = PLATFORM.startswith('linux')


if __name__ == '__main__':
    # 测试输出
    print("="*70)
    print("跨平台路径测试")
    print("="*70)
    print(f"\n当前平台: {PLATFORM}")
    print(f"  Windows: {IS_WINDOWS}")
    print(f"  macOS: {IS_MACOS}")
    print(f"  Linux: {IS_LINUX}")

    print(f"\n用户数据目录: {get_user_data_dir()}")
    print(f"数据库路径: {get_database_path()}")
    print(f"日志目录: {get_log_dir()}")

    print(f"\n资源路径示例:")
    print(f"  play_modes.json: {get_config_path('assets/play_modes.json')}")

    print("\n目录创建测试:")
    print(f"  用户数据目录存在: {get_user_data_dir().exists()}")
    print(f"  日志目录存在: {get_log_dir().exists()}")
    print("="*70)
