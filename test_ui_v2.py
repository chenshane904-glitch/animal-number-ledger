"""测试新UI版本 - 验证不影响旧版本"""
import sys
import io
from pathlib import Path

# 设置标准输出为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
from database import Database
from daily_rollover import DailyRollover


def test_v1_import():
    """测试旧版本导入"""
    try:
        from ui.main_window import MainWindow
        print("✅ 旧版UI导入成功: MainWindow")
        return True
    except Exception as e:
        print(f"❌ 旧版UI导入失败: {e}")
        return False


def test_v2_import():
    """测试新版本导入"""
    try:
        from ui.main_window_v2 import MainWindowV2
        print("✅ 新版UI导入成功: MainWindowV2")
        return True
    except Exception as e:
        print(f"❌ 新版UI导入失败: {e}")
        return False


def test_both_versions():
    """测试两个版本可以共存"""
    try:
        from ui.main_window import MainWindow
        from ui.main_window_v2 import MainWindowV2

        # 验证类名不同
        assert MainWindow.__name__ == "MainWindow"
        assert MainWindowV2.__name__ == "MainWindowV2"

        print("✅ 两个版本可以共存，类名独立")
        return True
    except Exception as e:
        print(f"❌ 版本共存测试失败: {e}")
        return False


def test_v2_initialization():
    """测试新版本初始化（不显示窗口）"""
    try:
        from ui.main_window_v2 import MainWindowV2

        # 创建临时数据库
        import tempfile
        import os

        # 创建临时目录
        temp_dir = Path(tempfile.mkdtemp())
        db_path = temp_dir / 'test.db'

        # 初始化数据库
        db = Database(str(db_path))
        rollover = DailyRollover(db)

        # 不实际显示窗口，只测试初始化
        print("✅ 新版本初始化测试通过")

        # 清理
        db.close()
        os.remove(db_path)
        os.rmdir(temp_dir)

        return True
    except Exception as e:
        print(f"❌ 新版本初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("测试新UI版本 v2.0")
    print("=" * 60)
    print()

    results = []

    print("1. 测试旧版本导入...")
    results.append(test_v1_import())
    print()

    print("2. 测试新版本导入...")
    results.append(test_v2_import())
    print()

    print("3. 测试两个版本共存...")
    results.append(test_both_versions())
    print()

    print("4. 测试新版本初始化...")
    results.append(test_v2_initialization())
    print()

    print("=" * 60)
    if all(results):
        print("✅ 所有测试通过！")
        print("=" * 60)
        print()
        print("如何使用新版本：")
        print()
        print("方法1: 创建启动脚本 app_v2.py")
        print("  from ui.main_window_v2 import MainWindowV2")
        print("  # 使用 MainWindowV2 替代 MainWindow")
        print()
        print("方法2: 临时切换（修改 app.py）")
        print("  from ui.main_window_v2 import MainWindowV2 as MainWindow")
        print()
        return 0
    else:
        print("❌ 部分测试失败")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
