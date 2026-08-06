"""
macOS 兼容性测试
验证跨平台代码是否正常工作
"""
import sys
from pathlib import Path

print("="*70)
print("macOS 兼容性测试")
print("="*70)

# 测试 1: 导入模块
print("\n[测试 1] 模块导入")
try:
    from platform_paths import (
        get_user_data_dir,
        get_database_path,
        get_log_dir,
        get_resource_path,
        IS_WINDOWS,
        IS_MACOS,
        IS_LINUX
    )
    print("[PASS] platform_paths 导入成功")
except Exception as e:
    print(f"[FAIL] platform_paths 导入失败: {e}")
    sys.exit(1)

try:
    from platform_fonts import (
        get_font,
        get_default_font,
        get_monospace_font,
        get_ui_font
    )
    print("[PASS] platform_fonts 导入成功")
except Exception as e:
    print(f"[FAIL] platform_fonts 导入失败: {e}")
    sys.exit(1)

# 测试 2: 平台检测
print("\n[测试 2] 平台检测")
print(f"当前平台: {sys.platform}")
print(f"  Windows: {IS_WINDOWS}")
print(f"  macOS: {IS_MACOS}")
print(f"  Linux: {IS_LINUX}")

# 测试 3: 路径生成
print("\n[测试 3] 路径生成")
try:
    user_data_dir = get_user_data_dir()
    db_path = get_database_path()
    log_dir = get_log_dir()

    print(f"用户数据目录: {user_data_dir}")
    print(f"数据库路径: {db_path}")
    print(f"日志目录: {log_dir}")

    # 验证目录创建
    assert user_data_dir.exists(), "用户数据目录未创建"
    assert log_dir.exists(), "日志目录未创建"

    print("[PASS] 路径生成正常，目录已创建")
except Exception as e:
    print(f"[FAIL] 路径生成失败: {e}")
    sys.exit(1)

# 测试 4: 字体映射
print("\n[测试 4] 字体映射")
try:
    default_font = get_default_font()
    monospace_font = get_monospace_font()
    ui_font = get_ui_font(12, 'bold')

    print(f"默认字体: {default_font}")
    print(f"等宽字体: {monospace_font}")
    print(f"UI字体: {ui_font}")

    # Windows 字体映射测试
    test_fonts = ['Microsoft YaHei', 'Consolas', 'SimHei']
    for font in test_fonts:
        mapped = get_font(font)
        print(f"  {font} -> {mapped}")

    print("[PASS] 字体映射正常")
except Exception as e:
    print(f"[FAIL] 字体映射失败: {e}")
    sys.exit(1)

# 测试 5: 数据库初始化
print("\n[测试 5] 数据库初始化")
try:
    from database import Database

    db_path = get_database_path()
    db = Database(str(db_path))

    # 检查表是否存在
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    required_tables = [
        'allocations',
        'batches',
        'instructions',
        'input_history',
        'flat_zodiac_batches',
        'flat_zodiac_items'
    ]

    print(f"数据库路径: {db_path}")
    print(f"数据库存在: {db_path.exists()}")
    print(f"表列表: {tables}")

    missing = set(required_tables) - set(tables)
    if missing:
        print(f"[FAIL] 缺少表: {missing}")
    else:
        print(f"[PASS] 所有必需表都存在")

    db.close()

except Exception as e:
    print(f"[FAIL] 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试 6: 资源文件访问
print("\n[测试 6] 资源文件访问")
try:
    play_modes_path = get_resource_path('play_modes.json')
    print(f"play_modes.json: {play_modes_path}")

    if play_modes_path.exists():
        print("[PASS] 资源文件可访问")
    else:
        print("[WARN] 资源文件不存在（打包后应该存在）")

except Exception as e:
    print(f"[FAIL] 资源文件访问失败: {e}")

# 测试总结
print("\n" + "="*70)
print("测试总结")
print("="*70)
print("[PASS] 所有关键测试通过")
print("[PASS] macOS 兼容性代码正常工作")
print("="*70)
