# -*- coding: utf-8 -*-
"""
完整测试套件
验证所有解析场景
"""

import sys
from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING


def test_case_1():
    """案例1: 普通号码列表（不应自动展开）"""
    print("\n[案例1] 普通号码列表")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "07-19-27-06-18-30-34-46-22-40-23-35-08-40-24-12-38-44各250"
    print(f"输入: {input_text}")

    result = parser.parse_input(input_text)
    assert len(result) == 1, f"应该返回1个指令，实际: {len(result)}"

    targets = result[0].targets
    expected = ['07', '19', '27', '06', '18', '30', '34', '46', '22', '40', '23', '35', '08', '24', '12', '38', '44']

    print(f"期望: {expected}")
    print(f"实际: {targets}")

    # 检查不应该出现的号码
    forbidden = ['08', '09', '10', '11', '13', '14', '15', '16', '17']
    for num in forbidden:
        if num in targets and num not in expected:
            raise AssertionError(f"不应该出现号码 {num}")

    # 检查应该出现的号码
    for num in expected:
        assert num in targets, f"缺少号码 {num}"

    assert result[0].amount_integer == 25000, "金额错误"
    print("PASS")


def test_case_2():
    """案例2: 1头模式"""
    print("\n[案例2] 1头模式")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "1头20"
    print(f"输入: {input_text}")

    result = parser.parse_input(input_text)
    assert len(result) == 1, f"应该返回1个指令"

    targets = [int(n) for n in result[0].targets]
    expected = list(range(10, 20))

    print(f"期望: {expected}")
    print(f"实际: {targets}")

    assert targets == expected, f"1头应该是10-19"
    assert result[0].amount_integer == 2000, "金额错误"
    print("✓ PASS")


def test_case_3():
    """案例3: 2头模式"""
    print("\n[案例3] 2头模式")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "2头50"
    print(f"输入: {input_text}")

    result = parser.parse_input(input_text)
    targets = [int(n) for n in result[0].targets]
    expected = list(range(20, 30))

    print(f"期望: {expected}")
    print(f"实际: {targets}")

    assert targets == expected, f"2头应该是20-29"
    assert result[0].amount_integer == 5000, "金额错误"
    print("✓ PASS")


def test_case_4():
    """案例4: 3头模式"""
    print("\n[案例4] 3头模式")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "3头100"
    print(f"输入: {input_text}")

    result = parser.parse_input(input_text)
    targets = [int(n) for n in result[0].targets]
    expected = list(range(30, 40))

    print(f"期望: {expected}")
    print(f"实际: {targets}")

    assert targets == expected, f"3头应该是30-39"
    assert result[0].amount_integer == 10000, "金额错误"
    print("✓ PASS")


def test_case_5():
    """案例5: 4头模式"""
    print("\n[案例5] 4头模式")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "4头200"
    print(f"输入: {input_text}")

    result = parser.parse_input(input_text)
    targets = [int(n) for n in result[0].targets]
    expected = list(range(40, 50))

    print(f"期望: {expected}")
    print(f"实际: {targets}")

    assert targets == expected, f"4头应该是40-49"
    assert result[0].amount_integer == 20000, "金额错误"
    print("✓ PASS")


def test_case_6():
    """案例6: 蓝波双"""
    print("\n[案例6] 蓝波双")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "蓝波双200"
    print(f"输入: {input_text}")

    result = parser.parse_input(input_text)
    targets = [int(n) for n in result[0].targets]

    print(f"结果: {targets}")

    # 验证都是蓝波
    blue_nums = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
    for num in targets:
        assert num in blue_nums, f"{num} 不是蓝波"

    # 验证都是双数
    for num in targets:
        assert num % 2 == 0, f"{num} 不是双数"

    assert result[0].amount_integer == 20000, "金额错误"
    print("✓ PASS")


def test_case_7():
    """案例7: 红波大"""
    print("\n[案例7] 红波大")
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    input_text = "红波大100"
    print(f"输入: {input_text}")

    result = parser.parse_input(input_text)
    targets = [int(n) for n in result[0].targets]

    print(f"结果: {targets}")

    # 验证都是红波
    red_nums = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
    for num in targets:
        assert num in red_nums, f"{num} 不是红波"

    # 验证都是大号
    for num in targets:
        assert num > 24, f"{num} 不是大号"

    assert result[0].amount_integer == 10000, "金额错误"
    print("✓ PASS")


def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("完整测试套件")
    print("="*60)

    tests = [
        test_case_1,
        test_case_2,
        test_case_3,
        test_case_4,
        test_case_5,
        test_case_6,
        test_case_7,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("="*60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
