# -*- coding: utf-8 -*-
"""
真实业务测试
模拟用户实际使用场景
"""

import sys
from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING


def format_targets(targets):
    """格式化目标列表"""
    if len(targets) <= 10:
        return str(targets)
    else:
        return f"{targets[:5]}...{targets[-5:]} (共{len(targets)}个)"


def test_business_case_1():
    """业务案例1: 1头20"""
    print("\n[业务案例1] 1头20")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "1头20"
    result = parser.parse_input(input_text)

    assert len(result) == 1, f"应该返回1个指令"
    targets = [int(n) for n in result[0].targets]

    print(f"  输入: {input_text}")
    print(f"  结果: {targets}")
    print(f"  金额: {result[0].amount_integer / 100}")

    # 验证：只有10-19
    expected = list(range(10, 20))
    assert targets == expected, f"应该只有10-19，实际: {targets}"

    # 验证：不应该有其他号码
    for num in targets:
        assert 10 <= num <= 19, f"号码{num}不在1头范围"

    print("  PASS")
    return True


def test_business_case_2():
    """业务案例2: 2头20"""
    print("\n[业务案例2] 2头20")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "2头20"
    result = parser.parse_input(input_text)

    targets = [int(n) for n in result[0].targets]
    print(f"  输入: {input_text}")
    print(f"  结果: {targets}")

    expected = list(range(20, 30))
    assert targets == expected, f"应该只有20-29"

    print("  PASS")
    return True


def test_business_case_3():
    """业务案例3: 3头20"""
    print("\n[业务案例3] 3头20")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "3头20"
    result = parser.parse_input(input_text)

    targets = [int(n) for n in result[0].targets]
    print(f"  输入: {input_text}")
    print(f"  结果: {targets}")

    expected = list(range(30, 40))
    assert targets == expected, f"应该只有30-39"

    print("  PASS")
    return True


def test_business_case_4():
    """业务案例4: 4头20"""
    print("\n[业务案例4] 4头20")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "4头20"
    result = parser.parse_input(input_text)

    targets = [int(n) for n in result[0].targets]
    print(f"  输入: {input_text}")
    print(f"  结果: {targets}")

    expected = list(range(40, 50))
    assert targets == expected, f"应该只有40-49"

    print("  PASS")
    return True


def test_business_case_5():
    """业务案例5: 真实号码列表（关键测试）"""
    print("\n[业务案例5] 真实号码列表（禁止自动展开）")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "07-19-27-06-18-30-34-46-22-40-23-35-08-40-24-12-38-44各250"
    result = parser.parse_input(input_text)

    targets = result[0].targets
    print(f"  输入: {input_text}")
    print(f"  结果: {format_targets(targets)}")

    # 应该包含的号码
    expected = ['07', '19', '27', '06', '18', '30', '34', '46', '22', '40', '23', '35', '08', '24', '12', '38', '44']

    # 禁止出现的号码（自动填充的）
    forbidden = ['09', '10', '11', '13', '14', '15', '16', '17', '20', '21', '25', '26', '28', '29', '31', '32', '33', '36', '37', '39', '41', '42', '43', '45']

    print(f"  检查禁止号码...")
    for num in forbidden:
        if num in targets:
            raise AssertionError(f"错误！出现了自动填充的号码: {num}")

    print(f"  检查必需号码...")
    for num in expected:
        if num not in targets:
            raise AssertionError(f"缺少号码: {num}")

    print("  PASS - 没有自动展开范围")
    return True


def test_business_case_6():
    """业务案例6: 蓝波双200"""
    print("\n[业务案例6] 蓝波双200")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "蓝波双200"
    result = parser.parse_input(input_text)

    targets = [int(n) for n in result[0].targets]
    amount = result[0].amount_integer / 100

    print(f"  输入: {input_text}")
    print(f"  结果: {targets}")
    print(f"  金额: {amount}")

    # 验证金额
    assert result[0].amount_integer == 20000, f"金额错误，应该是20000，实际: {result[0].amount_integer}"

    # 验证都是蓝波
    blue_nums = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
    for num in targets:
        assert num in blue_nums, f"{num} 不是蓝波"

    # 验证都是双数
    for num in targets:
        assert num % 2 == 0, f"{num} 不是双数"

    print("  PASS")
    return True


def run_business_tests():
    """运行所有业务测试"""
    print("="*60)
    print("真实业务测试")
    print("="*60)

    tests = [
        ("1头20", test_business_case_1),
        ("2头20", test_business_case_2),
        ("3头20", test_business_case_3),
        ("4头20", test_business_case_4),
        ("真实号码列表", test_business_case_5),
        ("蓝波双200", test_business_case_6),
    ]

    passed = 0
    failed = 0
    results = []

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
            results.append((name, "PASS", None))
        except AssertionError as e:
            failed += 1
            results.append((name, "FAIL", str(e)))
            print(f"  FAIL: {e}")
        except Exception as e:
            failed += 1
            results.append((name, "ERROR", str(e)))
            print(f"  ERROR: {e}")

    # 输出报告
    print("\n" + "="*60)
    print("真实业务测试报告")
    print("="*60)
    print(f"\n测试数量: {len(tests)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {passed}/{len(tests)} ({100*passed//len(tests)}%)")

    print("\n详细结果:")
    for name, status, error in results:
        if status == "PASS":
            print(f"  [{status}] {name}")
        else:
            print(f"  [{status}] {name}: {error}")

    print("\n" + "="*60)

    return failed == 0


if __name__ == '__main__':
    success = run_business_tests()
    sys.exit(0 if success else 1)
