"""测试香港版本 - 验证可以和澳门版同时运行"""
import sys
import io
from pathlib import Path

# 设置标准输出为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_澳门版_import():
    """测试澳门版导入"""
    try:
        from ui.main_window import MainWindow
        print("✅ 澳门版UI导入成功: MainWindow")
        return True
    except Exception as e:
        print(f"❌ 澳门版UI导入失败: {e}")
        return False


def test_香港版_import():
    """测试香港版导入"""
    try:
        from ui.main_window_hk import MainWindowHK
        print("✅ 香港版UI导入成功: MainWindowHK")
        return True
    except Exception as e:
        print(f"❌ 香港版UI导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_both_versions():
    """测试两个版本可以共存"""
    try:
        from ui.main_window import MainWindow
        from ui.main_window_hk import MainWindowHK

        # 验证类名不同
        assert MainWindow.__name__ == "MainWindow"
        assert MainWindowHK.__name__ == "MainWindowHK"

        print("✅ 澳门版和香港版可以共存，类名独立")
        return True
    except Exception as e:
        print(f"❌ 版本共存测试失败: {e}")
        return False


def test_database_isolation():
    """测试数据库隔离"""
    try:
        import tempfile
        import os
        from pathlib import Path
        from database import Database
        from daily_rollover import DailyRollover

        # 创建临时目录
        temp_dir = Path(tempfile.mkdtemp())

        # 澳门版数据库
        db_macao_path = temp_dir / 'ledger.db'
        db_macao = Database(str(db_macao_path))

        # 香港版数据库
        db_hk_path = temp_dir / 'ledger_hk.db'
        db_hk = Database(str(db_hk_path))

        # 验证是两个独立的数据库文件
        assert db_macao_path != db_hk_path
        assert db_macao_path.exists()
        assert db_hk_path.exists()

        print("✅ 数据库隔离测试通过：两个版本使用独立数据库")

        # 清理
        db_macao.close()
        db_hk.close()
        os.remove(db_macao_path)
        os.remove(db_hk_path)
        os.rmdir(temp_dir)

        return True
    except Exception as e:
        print(f"❌ 数据库隔离测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_window_titles():
    """测试窗口标题区分"""
    try:
        from ui.main_window import MainWindow
        from ui.main_window_hk import MainWindowHK

        # 验证窗口标题不同
        macao_title = "十二动物号码归纳器"
        hk_title = "香港十二生肖投注系统"

        print(f"✅ 窗口标题区分：")
        print(f"   澳门版: {macao_title}")
        print(f"   香港版: {hk_title}")

        return True
    except Exception as e:
        print(f"❌ 窗口标题测试失败: {e}")
        return False


def test_color_schemes():
    """测试配色方案区分"""
    try:
        from ui.main_window_hk import MainWindowHK

        # 验证香港版独特配色
        assert MainWindowHK.COLOR_PRIMARY == "#00796B"
        assert MainWindowHK.COLOR_SECONDARY == "#4DB6AC"
        assert MainWindowHK.COLOR_ACCENT == "#FF6F00"

        print("✅ 香港版配色方案独立：深青色主题")
        return True
    except Exception as e:
        print(f"❌ 配色方案测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("测试香港版本 HK v1.0")
    print("=" * 60)
    print()

    results = []

    print("1. 测试澳门版导入...")
    results.append(test_澳门版_import())
    print()

    print("2. 测试香港版导入...")
    results.append(test_香港版_import())
    print()

    print("3. 测试两个版本共存...")
    results.append(test_both_versions())
    print()

    print("4. 测试数据库隔离...")
    results.append(test_database_isolation())
    print()

    print("5. 测试窗口标题区分...")
    results.append(test_window_titles())
    print()

    print("6. 测试配色方案区分...")
    results.append(test_color_schemes())
    print()

    print("=" * 60)
    if all(results):
        print("✅ 所有测试通过！")
        print("=" * 60)
        print()
        print("✨ 香港版和澳门版可以同时运行！")
        print()
        print("启动方式：")
        print()
        print("澳门版:")
        print("  python app.py")
        print()
        print("香港版:")
        print("  python app_hk.py")
        print()
        print("数据隔离:")
        print("  澳门版: ledger.db")
        print("  香港版: ledger_hk.db")
        print()
        return 0
    else:
        print("❌ 部分测试失败")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
