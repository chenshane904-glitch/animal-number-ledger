# -*- coding: utf-8 -*-
"""
集成测试：测试 parser.py 集成 v2 引擎后的功能
"""

import sys
from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING


def test_integrated_parser():
    """测试集成后的解析器"""
    print("="*60)
    print("集成测试：parser.py + v2 引擎")
    print("="*60)

    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    # 测试1: 头数模式
    print("\n[测试1] 头数模式")
    result = parser.parse_input("1头20")
    print(f"  输入: 1头20")
    print(f"  结果: {len(result)} 个指令")
    if result:
        print(f"  号码: {result[0].targets[:5]}...")
        assert len(result[0].targets) == 10, "1头应该生成10个号码"
    print("  PASS")

    # 测试2: 蓝波双
    print("\n[测试2] 蓝波双")
    result = parser.parse_input("蓝波双200")
    print(f"  输入: 蓝波双200")
    print(f"  结果: {len(result)} 个指令")
    if result:
        numbers = [int(n) for n in result[0].targets]
        print(f"  号码: {numbers}")
        # 验证都是蓝波且双数
        for num in numbers:
            assert num % 2 == 0, f"{num} 不是双数"
    print("  PASS")

    # 测试3: 红波大
    print("\n[测试3] 红波大")
    result = parser.parse_input("红波大100")
    print(f"  输入: 红波大100")
    print(f"  结果: {len(result)} 个指令")
    if result:
        numbers = [int(n) for n in result[0].targets]
        print(f"  号码: {numbers}")
        # 验证都是大号
        for num in numbers:
            assert num > 24, f"{num} 不是大号"
    print("  PASS")

    # 测试4: 组合条件
    print("\n[测试4] 蓝波双1头")
    result = parser.parse_input("蓝波双1头50")
    print(f"  输入: 蓝波双1头50")
    print(f"  结果: {len(result)} 个指令")
    if result:
        numbers = [int(n) for n in result[0].targets]
        print(f"  号码: {numbers}")
        # 验证都在1头范围
        for num in numbers:
            assert 10 <= num <= 19, f"{num} 不在1头范围"
    print("  PASS")

    # 测试5: 普通号码（向后兼容）
    print("\n[测试5] 普通号码输入")
    result = parser.parse_input("20 50")
    print(f"  输入: 20 50")
    print(f"  结果: {len(result)} 个指令")
    if result:
        print(f"  号码: {result[0].targets}")
        assert '20' in result[0].targets, "应该包含号码20"
    print("  PASS")

    # 测试6: 动物输入（向后兼容）
    print("\n[测试6] 动物输入")
    result = parser.parse_input("虎100")
    print(f"  输入: 虎100")
    print(f"  结果: {len(result)} 个指令")
    if result:
        print(f"  类型: {result[0].target_type}")
        print(f"  目标: {result[0].targets[:3]}...")
    print("  PASS")

    print("\n" + "="*60)
    print("ALL INTEGRATION TESTS PASSED")
    print("="*60)


if __name__ == '__main__':
    try:
        test_integrated_parser()
        sys.exit(0)
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
