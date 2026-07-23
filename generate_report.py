"""测试报告生成器"""
import subprocess
import sys
from datetime import datetime


def generate_test_report():
    """生成完整测试报告"""
    report = []
    report.append("=" * 80)
    report.append("十二动物号码归纳器 - 完整测试报告")
    report.append("=" * 80)
    report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Python 版本: {sys.version}")
    report.append("")

    # 运行所有测试
    print("正在运行所有测试...")
    result = subprocess.run(
        [
            sys.executable, '-m', 'pytest', 'tests/', '-v',
            '--tb=short', '-p', 'no:cacheprovider'
        ],
        capture_output=True,
        text=True
    )

    report.append("=" * 80)
    report.append("测试结果详情")
    report.append("=" * 80)
    report.append(result.stdout)

    # 解析测试结果
    if 'passed' in result.stdout:
        import re
        match = re.search(r'(\d+) passed', result.stdout)
        if match:
            passed = int(match.group(1))
            report.append("")
            report.append("=" * 80)
            report.append("测试通过情况")
            report.append("=" * 80)
            report.append(f"总计: {passed} 项测试")
            report.append("")

            report.append("测试项目与结果以上方pytest实际输出为准。")

    report.append("")
    report.append("=" * 80)
    report.append("测试总结")
    report.append("=" * 80)

    if result.returncode == 0:
        report.append("[SUCCESS] 所有测试通过！")
        report.append("")
        report.append("项目已准备就绪，可以打包发布。")
    else:
        report.append("[FAIL] 部分测试失败")
        report.append("")
        report.append("请检查失败的测试并修复问题。")

    report.append("")
    report.append("=" * 80)
    report.append("下一步操作")
    report.append("=" * 80)
    report.append("1. 运行 build_windows.bat 打包 Windows 版本")
    report.append("2. 在 macOS 上运行 ./build_macos.sh 打包 macOS 版本")
    report.append("3. 手动测试打包后的应用程序")
    report.append("4. 在断网环境下测试所有功能")
    report.append("5. 生成 SHA-256 校验值")
    report.append("")

    # 保存报告
    report_text = '\n'.join(report)
    with open('TEST_REPORT.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print("\n测试报告已保存到: TEST_REPORT.txt")

    return result.returncode == 0


if __name__ == '__main__':
    success = generate_test_report()
    sys.exit(0 if success else 1)
