"""测试运行器（用于自检按钮）"""
import unittest
import io
import sys
import tempfile
import os


def run_safe_tests() -> str:
    """
    运行安全的内置测试（不修改正式数据库）

    Returns:
        测试结果字符串
    """
    # 导入测试模块
    from tests import test_parser, test_calculator, test_database, test_rollover, test_deletion, test_backup

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试
    suite.addTests(loader.loadTestsFromModule(test_parser))
    suite.addTests(loader.loadTestsFromModule(test_calculator))
    suite.addTests(loader.loadTestsFromModule(test_database))
    suite.addTests(loader.loadTestsFromModule(test_rollover))
    suite.addTests(loader.loadTestsFromModule(test_deletion))
    suite.addTests(loader.loadTestsFromModule(test_backup))

    # 运行测试
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)

    # 格式化结果
    output = stream.getvalue()

    summary = f"\n{'='*60}\n"
    summary += f"测试总数: {result.testsRun}\n"
    summary += f"成功: {result.testsRun - len(result.failures) - len(result.errors)}\n"
    summary += f"失败: {len(result.failures)}\n"
    summary += f"错误: {len(result.errors)}\n"

    if result.wasSuccessful():
        summary += "\n✅ 所有测试通过！\n"
    else:
        summary += "\n❌ 存在失败的测试\n"

    return output + summary


def run_all_tests():
    """运行所有测试（命令行）"""
    from tests import test_parser, test_calculator, test_database, test_rollover, test_deletion, test_backup

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(test_parser))
    suite.addTests(loader.loadTestsFromModule(test_calculator))
    suite.addTests(loader.loadTestsFromModule(test_database))
    suite.addTests(loader.loadTestsFromModule(test_rollover))
    suite.addTests(loader.loadTestsFromModule(test_deletion))
    suite.addTests(loader.loadTestsFromModule(test_backup))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
