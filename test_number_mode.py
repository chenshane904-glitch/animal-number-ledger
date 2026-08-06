"""测试号码模式是否受影响"""
import json
from database import Database
from parser import InstructionParser
from calculator_factory import CalculatorFactory
from play_mode import PlayMode
from models import Batch
from datetime import datetime
from constants import MIN_NUMBER, MAX_NUMBER

print("="*60)
print("测试：号码模式是否受影响")
print("="*60)

db = Database('data.db')
current_date = datetime.now().strftime('%Y-%m-%d')
ledger = db.get_or_create_active_ledger(current_date)
animal_mapping = db.get_animal_mapping()

print(f"\n当前账本: ID={ledger.id}")

# 号码模式输入
input_text = "01 02 03 100"

print(f"\n输入（号码模式）:\n{input_text}")

# 解析
parser = InstructionParser(animal_mapping)
instructions = parser.parse_input(input_text)

print(f"\n解析: {len(instructions)} 条指令")

# 计算
calculator = CalculatorFactory.get_calculator(PlayMode.NUMBER, animal_mapping)
current_totals = {i: 0 for i in range(MIN_NUMBER, MAX_NUMBER + 1)}
result = calculator.calculate(instructions, current_totals)

print(f"计算: 总金额={result.total_amount/100}, 非零号码={result.non_zero_count}")

# 保存（使用原有方法）
batch = Batch(
    raw_input=input_text,
    total_before=0,
    total_after=result.total_amount,
    mapping_snapshot=json.dumps(animal_mapping, ensure_ascii=False),
    instructions=instructions
)

batch_id = db.add_batch_with_allocations(ledger.id, batch, animal_mapping)
print(f"批次ID: {batch_id}（号码模式）")

# 使用统一查询
print("\n使用统一查询接口:")
number_totals = db.get_ledger_totals_by_mode(ledger.id, 'number')

non_zero = [(n, a) for n, a in number_totals.items() if a > 0]
print(f"  非零号码: {len(non_zero)}")
for num, amount in non_zero[:5]:
    print(f"    号码{num:02d}: {amount/100}")

total = sum(number_totals.values())
print(f"  总金额: {total/100}")

# 验证平特模式数据仍然存在
print("\n验证平特模式数据:")
animal_totals = db.get_ledger_totals_by_mode(ledger.id, 'flat_zodiac')
non_zero_animals = [(a, amt) for a, amt in animal_totals.items() if amt > 0]
print(f"  非零生肖: {len(non_zero_animals)}")
for animal, amount in non_zero_animals:
    print(f"    {animal}: {amount/100}")

db.conn.close()

print("\n" + "="*60)
print("测试完成 - 号码模式和平特模式可以共存")
print("="*60)
