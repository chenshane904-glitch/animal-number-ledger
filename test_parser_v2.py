# -*- coding: utf-8 -*-
"""
解析器 v2.0 测试
验证所有玩法组合
"""

import sys
from parser_v2 import get_parser_v2


def test_head_mode():
    """测试头数模式"""
    print("\n=== 测试1: 头数模式 ===")
    parser = get_parser_v2()

    # 测试1头
    result = parser.parse("1头20")
    assert len(result) == 1, "应该返回1个指令"
    numbers = result[0].targets
    expected = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
    assert numbers == expected, f"1头20 失败: {numbers}"
    assert result[0].amount_integer == 2000, "金额错误"
    print(f"OK 1头20 -> {len(numbers)}个号码: {', '.join(numbers[:5])}...")

    # 测试一头
    result = parser.parse("一头30")
    numbers = result[0].targets
    assert numbers == expected, f"一头30 失败"
    print(f"OK 一头30 -> {len(numbers)}个号码")

    # 测试2头
    result = parser.parse("2头50")
    numbers = result[0].targets
    expected = ['20', '21', '22', '23', '24', '25', '26', '27', '28', '29']
    assert numbers == expected, f"2头50 失败"
    print(f"OK 2头50 -> {len(numbers)}个号码: {', '.join(numbers[:5])}...")


def test_color_parity():
    """测试颜色+单双"""
    print("\n=== 测试2: 颜色+单双 ===")
    parser = get_parser_v2()

    # 蓝波双
    result = parser.parse("蓝波双200")
    numbers = [int(n) for n in result[0].targets]
    print(f"OK 蓝波双200 -> {len(numbers)}个号码: {numbers}")

    # 验证：都是蓝波
    blue_nums = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
    for num in numbers:
        assert num in blue_nums, f"{num} 不是蓝波"

    # 验证：都是双数
    for num in numbers:
        assert num % 2 == 0, f"{num} 不是双数"

    # 不应该包含奇数
    odd_nums = [3, 9, 15, 25, 31, 37, 41, 47]
    for num in odd_nums:
        assert num not in numbers, f"{num} 是奇数，不应出现"

    print(f"  验证通过：全部是蓝波且双数")


def test_color_size():
    """测试颜色+大小"""
    print("\n=== 测试3: 颜色+大小 ===")
    parser = get_parser_v2()

    # 红波大
    result = parser.parse("红波大100")
    numbers = [int(n) for n in result[0].targets]
    print(f"OK 红波大100 -> {len(numbers)}个号码: {numbers}")

    # 验证：都是红波
    red_nums = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
    for num in numbers:
        assert num in red_nums, f"{num} 不是红波"

    # 验证：都是大号（>24）
    for num in numbers:
        assert num > 24, f"{num} 不是大号"

    print(f"  验证通过：全部是红波且大号")


def test_multi_conditions():
    """测试多条件组合"""
    print("\n=== 测试4: 多条件组合 ===")
    parser = get_parser_v2()

    # 蓝波双1头
    result = parser.parse("蓝波双1头50")
    numbers = [int(n) for n in result[0].targets]
    print(f"OK 蓝波双1头50 -> {len(numbers)}个号码: {numbers}")

    # 验证：头=1
    for num in numbers:
        assert 10 <= num <= 19, f"{num} 不在1头范围"

    # 验证：蓝波
    blue_nums = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
    for num in numbers:
        assert num in blue_nums, f"{num} 不是蓝波"

    # 验证：双数
    for num in numbers:
        assert num % 2 == 0, f"{num} 不是双数"

    print(f"  验证通过：同时满足 蓝波+双+1头")


def test_tail():
    """测试尾数"""
    print("\n=== 测试5: 尾数 ===")
    parser = get_parser_v2()

    # 尾5
    result = parser.parse("尾5 50")
    numbers = [int(n) for n in result[0].targets]
    print(f"OK 尾5 50 -> {len(numbers)}个号码: {numbers}")

    # 验证：尾数都是5
    for num in numbers:
        assert num % 10 == 5, f"{num} 尾数不是5"

    print(f"  验证通过：全部尾数为5")


def test_tail_size():
    """测试尾数大小"""
    print("\n=== 测试6: 尾数大小 ===")
    parser = get_parser_v2()

    # 尾大
    result = parser.parse("尾大100")
    numbers = [int(n) for n in result[0].targets]
    print(f"OK 尾大100 -> {len(numbers)}个号码: {', '.join(str(n) for n in numbers[:10])}...")

    # 验证：尾数都>=5
    for num in numbers:
        assert num % 10 >= 5, f"{num} 尾数不是大"

    print(f"  验证通过：全部尾数大（>=5）")


def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("解析器 v2.0 测试")
    print("="*60)

    try:
        test_head_mode()
        test_color_parity()
        test_color_size()
        test_multi_conditions()
        test_tail()
        test_tail_size()

        print("\n" + "="*60)
        print("ALL TESTS PASSED")
        print("="*60)
        return True

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\nTEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
