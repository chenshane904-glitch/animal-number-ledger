import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

# 测试输入
test_input = "马猴马狗猴50"

print(f"输入: {test_input}")
print()

instructions = parser.parse_input(test_input)

print(f"解析结果: {len(instructions)} 条指令")
print()

for i, inst in enumerate(instructions):
    print(f"指令{i+1}:")
    print(f"  类型: {inst.target_type}")
    print(f"  目标: {inst.targets}")
    print(f"  金额: {inst.amount_integer / 100}")
    print()

# 检查目标数组
if instructions:
    inst = instructions[0]
    print(f"目标数组详细: {inst.targets}")
    print(f"目标数量: {len(inst.targets)}")
    print()
    
    # 统计每个动物出现次数
    from collections import Counter
    counter = Counter(inst.targets)
    print("动物出现次数:")
    for animal, count in counter.items():
        print(f"  {animal}: {count}次")
