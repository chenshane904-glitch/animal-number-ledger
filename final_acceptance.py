"""最终验收测试脚本"""
import subprocess
import sys
import os
from pathlib import Path


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if Path(file_path).exists():
        print(f"[PASS] {description}: {file_path}")
        return True
    else:
        print(f"[FAIL] {description}: {file_path} - 文件不存在")
        return False


def run_tests():
    """运行所有测试"""
    print("运行测试套件...")
    result = subprocess.run(
        [
            sys.executable, '-m', 'pytest', 'tests/', '-v',
            '--tb=line', '-p', 'no:cacheprovider'
        ],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        # 统计通过的测试
        import re
        match = re.search(r'(\d+) passed', result.stdout)
        if match:
            count = match.group(1)
            print(f"[PASS] 所有测试通过: {count} 项")
            return True
    else:
        print("[FAIL] 测试失败")
        print(result.stdout[-500:])  # 只显示最后500字符
        return False


def main():
    """主验收流程"""
    print_header("十二动物号码归纳器 - 最终验收测试")

    results = []

    # 1. 检查核心文件
    print_header("1. 检查核心文件")
    results.append(check_file_exists("app.py", "主程序"))
    results.append(check_file_exists("parser.py", "解析器"))
    results.append(check_file_exists("calculator.py", "计算器"))
    results.append(check_file_exists("database.py", "数据库"))
    results.append(check_file_exists("models.py", "数据模型"))
    results.append(check_file_exists("constants.py", "常量定义"))
    results.append(check_file_exists("daily_rollover.py", "每日归档"))
    results.append(check_file_exists("backup.py", "备份恢复"))

    # 2. 检查UI模块
    print_header("2. 检查UI模块")
    results.append(check_file_exists("ui/main_window.py", "主窗口"))
    results.append(check_file_exists("ui/history_window.py", "历史窗口"))
    results.append(check_file_exists("ui/mapping_window.py", "映射窗口"))
    results.append(check_file_exists("ui/delete_dialog.py", "删除对话框"))

    # 3. 检查测试文件
    print_header("3. 检查测试文件")
    results.append(check_file_exists("tests/test_parser.py", "解析器测试"))
    results.append(check_file_exists("tests/test_calculator.py", "计算器测试"))
    results.append(check_file_exists("tests/test_database.py", "数据库测试"))
    results.append(check_file_exists("tests/test_rollover.py", "归档测试"))
    results.append(check_file_exists("tests/test_deletion.py", "删除测试"))
    results.append(check_file_exists("tests/test_backup.py", "备份测试"))

    # 4. 检查文档和脚本
    print_header("4. 检查文档和脚本")
    results.append(check_file_exists("README.md", "使用说明"))
    results.append(check_file_exists("DELIVERY.md", "交付清单"))
    results.append(check_file_exists("requirements.txt", "依赖列表"))
    results.append(check_file_exists("VERSION", "版本文件"))
    results.append(check_file_exists("build_windows.bat", "Windows打包脚本"))
    results.append(check_file_exists("build_macos.sh", "macOS打包脚本"))

    # 5. 运行测试套件
    print_header("5. 运行测试套件")
    results.append(run_tests())

    # 6. 检查依赖安装
    print_header("6. 检查依赖")
    try:
        import customtkinter
        print(f"[PASS] customtkinter 已安装 (版本: {customtkinter.__version__})")
        results.append(True)
    except ImportError:
        print("[FAIL] customtkinter 未安装")
        results.append(False)

    # 7. 检查代码质量
    print_header("7. 代码统计")
    py_files = list(Path('.').rglob('*.py'))
    py_files = [f for f in py_files if '__pycache__' not in str(f) and '.pytest_cache' not in str(f)]

    total_lines = 0
    for file in py_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
        except:
            pass

    print(f"Python文件数量: {len(py_files)}")
    print(f"总代码行数: {total_lines}")
    print(f"平均每文件: {total_lines // len(py_files) if py_files else 0} 行")

    # 总结
    print_header("验收总结")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"通过项目: {passed}/{total} ({percentage:.1f}%)")

    if passed == total:
        print("\n" + "=" * 80)
        print("状态: [SUCCESS] 项目验收通过")
        print("=" * 80)
        print("\n项目已准备就绪，可以交付！")
        print("\n下一步:")
        print("  1. 运行 build_windows.bat 打包 Windows 版本")
        print("  2. 在实际环境中测试打包后的应用")
        print("  3. 生成 SHA-256 校验值")
        print("  4. 准备交付包")
        return True
    else:
        print("\n" + "=" * 80)
        print("状态: [FAIL] 项目验收未通过")
        print("=" * 80)
        print("\n请修复失败的项目后重新验收。")
        return False


if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    success = main()
    sys.exit(0 if success else 1)
