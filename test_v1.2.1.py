# -*- coding: utf-8 -*-
"""
v1.2.1 测试脚本
测试三个修改：
1. 结果按金额排序
2. 动物名称不要求分隔符
3. 金额显示两位小数
"""

import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

print("=" * 60)
print("v1.2.1 功能测试")
print("=" * 60)
print()

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

# 测试用例
test_cases = [
    ("1.2.3各0.50", "小数点分隔号码"),
    ("123各0.50", "连续数字（应识别为123号）"),
    ("1 2 3各0.50", "空格分隔号码"),
    ("1,2,3各0.50", "逗号分隔号码"),
    ("蛇鼠猴鸡各75", "连续动物名称（无分隔符）"),
    ("蛇、鼠、猴、鸡各75", "顿号分隔动物"),
    ("蛇 鼠 猴 鸡各75", "空格分隔动物"),
    ("1-2-3各0.50", "横线分隔号码"),
    ("1/2/3各0.50", "斜杠分隔号码"),
    ("1各1.25", "单个号码带小数金额"),
]

print("测试解析功能：")
print("-" * 60)

success_count = 0
fail_count = 0

for input_text, description in test_cases:
    print(f"\n测试: {description}")
    print(f"输入: {input_text}")

    try:
        instructions = parser.parse_input(input_text)
        print("✓ 解析成功!")

        for inst in instructions:
            print(f"  目标类型: {inst.target_type}")
            print(f"  目标: {inst.targets}")
            print(f"  金额: {inst.amount_integer / 100:.2f}")
            print(f"  是否各数: {inst.is_each}")

        success_count += 1

    except Exception as e:
        print(f"✗ 解析失败: {e}")
        fail_count += 1

print()
print("=" * 60)
print(f"测试结果: 成功 {success_count}/{len(test_cases)}, 失败 {fail_count}/{len(test_cases)}")
print("=" * 60)
print()

# 模拟排序测试
print("测试排序功能：")
print("-" * 60)
print()

test_amounts = {
    3: 16800,   # 168.00
    7: 16800,   # 168.00
    14: 16800,  # 168.00
    2: 5000,    # 50.00
    12: 3000,   # 30.00
    1: 0,       # 0.00
    5: 16800,   # 168.00
    10: 5000,   # 50.00
}

# 排序：金额从大到小，金额相同按号码从小到大
sorted_list = sorted(test_amounts.items(), key=lambda x: (-x[1], x[0]))

print("排序结果（金额从大到小，相同金额按号码从小到大）：")
print()

for num, amount_int in sorted_list:
    amount = amount_int / 100
    print(f"{num:02d}  {amount:.2f}")

print()
print("=" * 60)
print("所有测试完成！")
print("=" * 60)
