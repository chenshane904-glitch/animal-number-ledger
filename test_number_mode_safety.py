"""测试号码模式是否正常"""
import sys
from parser import InstructionParser
from calculator import Calculator
from constants import MIN_NUMBER, MAX_NUMBER, DEFAULT_ANIMAL_MAPPING

print("="*70)
print("号码模式功能测试")
print("="*70)

animal_mapping = DEFAULT_ANIMAL_MAPPING
parser = InstructionParser(animal_mapping)
calculator = Calculator(animal_mapping)

# 测试1: 02各20
print("\n【测试1: 02各20】")
input1 = "02各20"
instructions1 = parser.parse_input(input1)
current_totals1 = {i: 0 for i in range(MIN_NUMBER, MAX_NUMBER + 1)}
result1 = calculator.calculate(instructions1, current_totals1)

print(f"输入: {input1}")
print(f"02金额: {result1.number_amounts.get(2, 0) / 100}")
print(f"预期: 20.00")
assert result1.number_amounts.get(2, 0) == 2000, "02金额错误"

# 测试2: 红双各50
print("\n【测试2: 红双各50】")
input2 = "红双各50"
instructions2 = parser.parse_input(input2)
current_totals2 = {i: 0 for i in range(MIN_NUMBER, MAX_NUMBER + 1)}
result2 = calculator.calculate(instructions2, current_totals2)

red_double = [2, 8, 12, 18, 24, 30, 34, 40, 46]
print(f"输入: {input2}")
print(f"红双号码: {red_double}")
for num in red_double[:3]:
    print(f"  {num:02d}金额: {result2.number_amounts.get(num, 0) / 100}")
print(f"预期每个: 50.00")

for num in red_double:
    assert result2.number_amounts.get(num, 0) == 5000, f"红双{num}金额错误"

# 测试3: 虎各30
print("\n【测试3: 虎各30】")
input3 = "虎各30"
instructions3 = parser.parse_input(input3)
current_totals3 = {i: 0 for i in range(MIN_NUMBER, MAX_NUMBER + 1)}
result3 = calculator.calculate(instructions3, current_totals3)

tiger_numbers = [3, 15, 27, 39]
print(f"输入: {input3}")
print(f"虎号码: {tiger_numbers}")
for num in tiger_numbers:
    print(f"  {num:02d}金额: {result3.number_amounts.get(num, 0) / 100}")
print(f"预期每个: 30.00")

for num in tiger_numbers:
    assert result3.number_amounts.get(num, 0) == 3000, f"虎{num}金额错误"

# 综合测试
print("\n【综合测试: 02各20 + 红双各50 + 虎各30】")
input_combined = """02各20
红双各50
虎各30"""

instructions_all = parser.parse_input(input_combined)
current_totals_all = {i: 0 for i in range(MIN_NUMBER, MAX_NUMBER + 1)}
result_all = calculator.calculate(instructions_all, current_totals_all)

print(f"02金额: {result_all.number_amounts.get(2, 0) / 100} (预期70)")
print(f"03金额: {result_all.number_amounts.get(3, 0) / 100} (预期30)")
print(f"08金额: {result_all.number_amounts.get(8, 0) / 100} (预期50)")
print(f"本次总额: {result_all.total_amount / 100} (预期590)")

non_zero = sum(1 for amt in result_all.number_amounts.values() if amt > 0)
print(f"涉及号码: {non_zero} (预期14)")

assert result_all.number_amounts.get(2, 0) == 7000, "02累计错误"
assert result_all.number_amounts.get(3, 0) == 3000, "03金额错误"
assert result_all.number_amounts.get(8, 0) == 5000, "08金额错误"
assert result_all.total_amount == 59000, "总额错误"
assert non_zero == 14, "号码数量错误"

print("\n" + "="*70)
print("号码模式测试全部通过 ✓")
print("="*70)
