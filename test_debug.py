# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

# 测试1: 号码用小数点分隔
print("=== 测试1: 1.2.3各0.50 ===")
try:
    instructions = parser.parse_input("1.2.3各0.50")
    print("解析成功!")
    for inst in instructions:
        print(f"  目标类型: {inst.target_type}")
        print(f"  目标: {inst.targets}")
        print(f"  金额: {inst.amount}")
except Exception as e:
    print(f"解析失败: {e}")

print()

# 测试2: 动物名称
print("=== 测试2: 蛇鼠猴鸡各75 ===")
try:
    instructions = parser.parse_input("蛇鼠猴鸡各75")
    print("解析成功!")
    for inst in instructions:
        print(f"  目标类型: {inst.target_type}")
        print(f"  目标: {inst.targets}")
        print(f"  金额: {inst.amount}")
except Exception as e:
    print(f"解析失败: {e}")
