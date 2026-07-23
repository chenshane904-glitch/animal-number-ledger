"""离线测试脚本"""
import sys
import subprocess


def check_network_imports():
    """检查是否有网络相关的导入"""
    forbidden_imports = [
        'requests',
        'urllib.request',
        'urllib.error',
        'http.client',
        'socket',  # 某些socket操作
        'websocket'
    ]

    print("检查网络相关导入...")

    # 检查所有Python文件
    import os
    from pathlib import Path

    project_root = Path(__file__).parent
    python_files = list(project_root.glob('*.py')) + list(project_root.glob('ui/*.py'))

    issues = []
    for file in python_files:
        if file.name.startswith('test_'):
            continue

        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

            for forbidden in forbidden_imports:
                if f'import {forbidden}' in content or f'from {forbidden}' in content:
                    issues.append(f"{file.name}: 发现禁止的导入 {forbidden}")

    if issues:
        print("[FAIL] 发现网络相关导入：")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("[PASS] 未发现禁止的网络导入")
        return True


def test_offline_functionality():
    """测试离线功能"""
    print("\n" + "="*60)
    print("离线功能测试")
    print("="*60)

    # 1. 检查网络导入
    result1 = check_network_imports()

    # 2. 运行单元测试（使用内存数据库，完全离线）
    print("\n运行单元测试...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-v'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("[PASS] 所有单元测试通过")
        result2 = True
    else:
        print("[FAIL] 单元测试失败")
        print(result.stdout)
        print(result.stderr)
        result2 = False

    # 总结
    print("\n" + "="*60)
    print("离线测试总结")
    print("="*60)
    print(f"网络导入检查: {'[PASS] 通过' if result1 else '[FAIL] 失败'}")
    print(f"单元测试: {'[PASS] 通过' if result2 else '[FAIL] 失败'}")

    if result1 and result2:
        print("\n[SUCCESS] 所有离线测试通过！")
        print("\n建议：在完全断网环境下测试以下功能：")
        print("  1. 启动程序")
        print("  2. 添加指令")
        print("  3. 查看历史记录")
        print("  4. 导出备份")
        print("  5. 导入备份")
        print("  6. 跨日归档（修改系统时间测试）")
        return True
    else:
        print("\n[FAIL] 离线测试失败")
        return False


if __name__ == '__main__':
    success = test_offline_functionality()
    sys.exit(0 if success else 1)
