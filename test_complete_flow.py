"""完整测试：平特一肖流程"""
import json
from database import Database
from flat_zodiac_parser import FlatZodiacParser
from calculator_factory import CalculatorFactory
from play_mode import PlayMode
from play_mode_config import get_animals_list
from models import Batch
from datetime import datetime

print("="*60)
print("完整测试：平特一肖模式")
print("="*60)

# 初始化
db = Database('data.db')
current_date = datetime.now().strftime('%Y-%m-%d')
ledger = db.get_or_create_active_ledger(current_date)
animal_mapping = db.get_animal_mapping()

print(f"\n当前账本: ID={ledger.id}, 日期={ledger.ledger_date}")

# 输入
input_text = """虎100
龙200"""

print(f"\n输入:\n{input_text}")

print("\n" + "="*60)
print("第一步：解析")
print("="*60)

parser = FlatZodiacParser()
instructions = parser.parse_input(input_text)

print(f"解析结果: {len(instructions)} 条指令")
for idx, inst in enumerate(instructions, 1):
    print(f"  指令{idx}: {inst.target_type} -> {inst.targets} -> {inst.amount_integer/100}")

print("\n" + "="*60)
print("第二步：计算")
print("="*60)

calculator = CalculatorFactory.get_calculator(PlayMode.FLAT_ZODIAC, animal_mapping)
animals = get_animals_list(PlayMode.FLAT_ZODIAC)
current_totals = {animal: 0 for animal in animals}

result = calculator.calculate(instructions, current_totals)

print(f"计算结果:")
print(f"  总金额: {result.total_amount/100}")
print(f"  非零生肖: {result.non_zero_count}")
for animal, amount in result.animal_amounts.items():
    if amount > 0:
        print(f"  {animal}: {amount/100}")

print("\n" + "="*60)
print("第三步：保存到数据库（模拟 main_window 逻辑）")
print("="*60)

# 创建批次对象
batch = Batch(
    raw_input=input_text,
    total_before=0,
    total_after=result.total_amount,
    mapping_snapshot=json.dumps(animal_mapping, ensure_ascii=False),
    instructions=instructions
)

# 保存批次和指令
cursor = db.conn.cursor()

cursor.execute("""
    INSERT INTO batches
    (ledger_id, raw_input, total_before, total_after, mapping_snapshot, play_mode)
    VALUES (?, ?, ?, ?, ?, ?)
""", (
    ledger.id,
    batch.raw_input,
    batch.total_before,
    batch.total_after,
    batch.mapping_snapshot,
    'flat_zodiac'
))
batch_id = cursor.lastrowid
print(f"批次ID: {batch_id}")

# 保存指令
for inst in instructions:
    cursor.execute("""
        INSERT INTO instructions
        (batch_id, source_line, original_text, normalized_text,
         target_type, targets, amount_integer, warning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        batch_id,
        inst.source_line,
        inst.original_text,
        inst.normalized_text,
        inst.target_type,
        json.dumps(inst.targets, ensure_ascii=False),
        inst.amount_integer,
        inst.warning
    ))

db.conn.commit()
print(f"保存了 {len(instructions)} 条指令")

print("\n" + "="*60)
print("第四步：使用统一查询接口查询")
print("="*60)

animal_totals = db.get_ledger_totals_by_mode(ledger.id, 'flat_zodiac')

print(f"查询结果:")
print(f"  返回类型: {type(animal_totals)}")
print(f"  数据:")
for animal, amount in animal_totals.items():
    if amount > 0:
        print(f"    {animal}: {amount/100}")

# 计算统计
total = sum(animal_totals.values())
non_zero = sum(1 for amt in animal_totals.values() if amt > 0)

print(f"\n  今日总下注: {total/100}")
print(f"  非零生肖: {non_zero}")

print("\n" + "="*60)
print("第五步：验证号码模式不受影响")
print("="*60)

number_totals = db.get_ledger_totals_by_mode(ledger.id, 'number')
print(f"号码模式查询结果: {type(number_totals)}")
print(f"  号码总数: {len([n for n, a in number_totals.items() if a > 0])}")

db.conn.close()

print("\n" + "="*60)
print("测试完成")
print("="*60)
