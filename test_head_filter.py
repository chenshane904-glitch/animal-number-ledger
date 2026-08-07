# -*- coding: utf-8 -*-
"""测试头数筛选功能"""

import sys
from head_filter import (
    get_head_numbers,
    format_head_numbers_for_input,
    get_all_heads,
    is_valid_head,
    HEAD_MAPPING
)


def test_head_mapping():
    """测试头数映射定义"""
    print("=" * 60)
    print("测试1: 头数映射定义")
    print("=" * 60)

    for head_name in HEAD_MAPPING:
        start, end = HEAD_MAPPING[head_name]
        count = end - start + 1
        print(f"{head_name}: {start}-{end} (共{count}个号码)")
        assert count == 10, f"{head_name} 应该有10个号码"

    print("[OK] 头数映射定义正确\n")


def test_get_head_numbers():
    """测试获取头数号码"""
    print("=" * 60)
    print("测试2: 获取头数号码")
    print("=" * 60)

    # 测试一头
    one_head = get_head_numbers("一头")
    print(f"一头: {one_head}")
    assert one_head == list(range(10, 20)), "一头应该是10-19"

    # 测试二头
    two_head = get_head_numbers("二头")
    print(f"二头: {two_head}")
    assert two_head == list(range(20, 30)), "二头应该是20-29"

    # 测试三头
    three_head = get_head_numbers("三头")
    print(f"三头: {three_head}")
    assert three_head == list(range(30, 40)), "三头应该是30-39"

    # 测试四头
    four_head = get_head_numbers("四头")
    print(f"四头: {four_head}")
    assert four_head == list(range(40, 50)), "四头应该是40-49"

    # 测试无效头数
    try:
        get_head_numbers("五头")
        assert False, "应该抛出ValueError"
    except ValueError as e:
        print(f"[OK] 无效头数正确抛出异常: {e}")

    print("[OK] 获取头数号码功能正确\n")


def test_format_head_numbers():
    """测试格式化头数号码"""
    print("=" * 60)
    print("测试3: 格式化头数号码")
    print("=" * 60)

    # 一头
    text1 = format_head_numbers_for_input("一头")
    print(f"一头: {text1}")
    assert text1 == "10-19", f"格式应该是 '10-19'，实际是 '{text1}'"

    # 二头
    text2 = format_head_numbers_for_input("二头")
    print(f"二头: {text2}")
    assert text2 == "20-29", f"格式应该是 '20-29'，实际是 '{text2}'"

    # 三头
    text3 = format_head_numbers_for_input("三头")
    print(f"三头: {text3}")
    assert text3 == "30-39", f"格式应该是 '30-39'，实际是 '{text3}'"

    # 四头
    text4 = format_head_numbers_for_input("四头")
    print(f"四头: {text4}")
    assert text4 == "40-49", f"格式应该是 '40-49'，实际是 '{text4}'"

    print("[OK] 格式化头数号码功能正确\n")


def test_get_all_heads():
    """测试获取所有头数"""
    print("=" * 60)
    print("测试4: 获取所有头数")
    print("=" * 60)

    all_heads = get_all_heads()
    print(f"所有头数: {all_heads}")
    assert all_heads == ["一头", "二头", "三头", "四头"], "应该返回4个头数"

    print("[OK] 获取所有头数功能正确\n")


def test_is_valid_head():
    """测试验证头数"""
    print("=" * 60)
    print("测试5: 验证头数")
    print("=" * 60)

    assert is_valid_head("一头") == True
    assert is_valid_head("二头") == True
    assert is_valid_head("三头") == True
    assert is_valid_head("四头") == True
    assert is_valid_head("五头") == False
    assert is_valid_head("零头") == False
    assert is_valid_head("") == False

    print("[OK] 验证头数功能正确\n")


def test_parser_integration():
    """测试与解析器集成"""
    print("=" * 60)
    print("测试6: 与解析器集成")
    print("=" * 60)

    from parser import InstructionParser
    from constants import DEFAULT_ANIMAL_MAPPING, AMOUNT_MULTIPLIER

    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    # 先测试范围展开功能
    test_text = "10-19"
    expanded = parser._expand_range(test_text)
    print(f"范围展开测试: '{test_text}' -> '{expanded}'")

    # 测试标准化
    test_input = "10-19 各10"
    normalized = parser._normalize_punctuation(test_input)
    print(f"标准化后: '{normalized}'")

    expanded_normalized = parser._expand_range(normalized)
    print(f"展开后: '{expanded_normalized}'")

    # 测试一头的输入（使用范围表示法，解析器会自动展开）
    # 格式："10-19 各10" 表示10到19每个号码各10元
    input_text = format_head_numbers_for_input("一头") + " 各10"
    print(f"输入文本: {input_text}")

    instructions = parser.parse_input(input_text)
    print(f"解析结果: {len(instructions)} 条指令")

    # 检查解析结果
    assert len(instructions) > 0, "应该至少有一条指令"

    # 第一条指令应该包含所有号码
    first_inst = instructions[0]
    print(f"  目标数量: {len(first_inst.targets)}")
    print(f"  目标: {first_inst.targets}")
    print(f"  目标类型: {first_inst.target_type}")
    print(f"  金额: {first_inst.amount_integer / AMOUNT_MULTIPLIER}")

    # 应该有10个号码
    assert len(first_inst.targets) == 10, f"应该有10个号码，实际有{len(first_inst.targets)}个"

    # 检查号码范围
    target_numbers = sorted([int(t) for t in first_inst.targets])
    expected_numbers = list(range(10, 20))
    assert target_numbers == expected_numbers, f"号码应该是10-19，实际是{target_numbers}"

    print("[OK] 与解析器集成正确\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试头数筛选功能")
    print("=" * 60 + "\n")

    try:
        test_head_mapping()
        test_get_head_numbers()
        test_format_head_numbers()
        test_get_all_heads()
        test_is_valid_head()
        test_parser_integration()

        print("=" * 60)
        print("[PASS] 所有测试通过！")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
