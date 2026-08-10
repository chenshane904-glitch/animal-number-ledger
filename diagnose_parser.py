# -*- coding: utf-8 -*-
"""
解析引擎诊断工具
检查当前解析流程
"""

import sys
from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING


def diagnose_parser():
    """诊断解析器"""
    print("="*60)
    print("解析引擎诊断")
    print("="*60)

    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    # 检查 v2 引擎是否可用
    print(f"\nv2 引擎可用: {parser.parser_v2 is not None}")

    # 测试用例1: 普通号码列表
    print("\n[测试1] 普通号码列表")
    test_input = "07-19-27-06-18各250"
    print(f"输入: {test_input}")

    try:
        result = parser.parse_input(test_input)
        print(f"结果: {len(result)} 个指令")
        for inst in result:
            print(f"  目标: {inst.targets}")
            print(f"  金额: {inst.amount_integer}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试用例2: 1头模式
    print("\n[测试2] 1头模式")
    test_input = "1头20"
    print(f"输入: {test_input}")

    try:
        result = parser.parse_input(test_input)
        print(f"结果: {len(result)} 个指令")
        if result:
            print(f"  目标: {result[0].targets[:5]}...")
            print(f"  金额: {result[0].amount_integer}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试用例3: 蓝波双
    print("\n[测试3] 蓝波双")
    test_input = "蓝波双200"
    print(f"输入: {test_input}")

    try:
        result = parser.parse_input(test_input)
        print(f"结果: {len(result)} 个指令")
        if result:
            print(f"  目标: {result[0].targets}")
            print(f"  金额: {result[0].amount_integer}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == '__main__':
    diagnose_parser()
