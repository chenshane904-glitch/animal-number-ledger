import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

from parser import InstructionParser
from calculator import Calculator
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)
calculator = Calculator(DEFAULT_ANIMAL_MAPPING)

# 测试用例
test_input = """蛇狗各30
14、38各20"""

print(f"输入:")
print(test_input)
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

# 计算结果
result = calculator.calculate(instructions, {})

print(f"计算结果:")
print(f"  总金额: {result.total_amount / 100}")
print(f"  涉及号码记录数: {result.non_zero_count}")
print(f"  分配记录数: {len(result.allocations)}")
print()

# 统计14号和38号的金额
num14_amount = result.number_amounts[14] / 100
num38_amount = result.number_amounts[38] / 100

print(f"号码金额:")
print(f"  14号: {num14_amount} 元")
print(f"  38号: {num38_amount} 元")
print()

# 统计14号和38号的下注次数
count_14 = sum(1 for a in result.allocations if a.number == 14)
count_38 = sum(1 for a in result.allocations if a.number == 38)

print(f"下注次数:")
print(f"  14号: {count_14} 次")
print(f"  38号: {count_38} 次")
