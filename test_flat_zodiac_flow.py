"""测试平特一肖完整流程"""
from database import Database
from flat_zodiac_parser import FlatZodiacParser
from calculator_factory import CalculatorFactory
from play_mode import PlayMode
from play_mode_config import get_animals_list

print("="*60)
print("第一步：解析输入")
print("="*60)

input_text = """虎100
龙200"""

parser = FlatZodiacParser()
instructions = parser.parse_input(input_text)

print(f"输入文本：\n{input_text}\n")
print(f"解析结果：{len(instructions)} 条指令")
for idx, inst in enumerate(instructions, 1):
    print(f"  指令{idx}: target_type={inst.target_type}, targets={inst.targets}, amount={inst.amount_integer/100}")

print("\n" + "="*60)
print("第二步：计算结果")
print("="*60)

db = Database('data.db')
animal_mapping = db.get_animal_mapping()
calculator = CalculatorFactory.get_calculator(PlayMode.FLAT_ZODIAC, animal_mapping)

print(f"计算器类型: {type(calculator).__name__}")

# 准备当前累计（生肖维度）
animals = get_animals_list(PlayMode.FLAT_ZODIAC)
current_totals = {animal: 0 for animal in animals}

print(f"当前累计: {current_totals}")

result = calculator.calculate(instructions, current_totals)

print(f"\n计算结果:")
print(f"  total_amount: {result.total_amount/100}")
print(f"  non_zero_count: {result.non_zero_count}")
print(f"  animal_amounts:")
for animal, amount in result.animal_amounts.items():
    if amount > 0:
        print(f"    {animal}: {amount/100}")

print("\n" + "="*60)
print("第三步：保存到数据库")
print("="*60)

# 获取或创建账本
from datetime import datetime
current_date = datetime.now().strftime('%Y-%m-%d')
ledger = db.get_or_create_active_ledger(current_date)
print(f"账本ID: {ledger.id}, 日期: {ledger.ledger_date}")

# 保存批次
cursor = db.conn.cursor()
cursor.execute("""
    INSERT INTO batches
    (ledger_id, raw_input, total_before, total_after, mapping_snapshot, play_mode)
    VALUES (?, ?, ?, ?, ?, ?)
""", (
    ledger.id,
    input_text,
    0,
    result.total_amount,
    "{}",
    'flat_zodiac'
))
batch_id = cursor.lastrowid
db.conn.commit()

print(f"批次ID: {batch_id}")

# 验证保存
cursor.execute("SELECT * FROM batches WHERE id=?", (batch_id,))
batch_row = cursor.fetchone()
print(f"\n批次记录:")
print(f"  id: {batch_row['id']}")
print(f"  ledger_id: {batch_row['ledger_id']}")
print(f"  raw_input: {batch_row['raw_input']}")
print(f"  total_before: {batch_row['total_before']}")
print(f"  total_after: {batch_row['total_after']}")
print(f"  play_mode: {batch_row['play_mode'] if 'play_mode' in batch_row.keys() else 'NULL'}")

print("\n" + "="*60)
print("第四步：检查数据库")
print("="*60)

cursor.execute("SELECT COUNT(*) FROM batches")
count = cursor.fetchone()[0]
print(f"batches 表记录数: {count}")

cursor.execute("SELECT id, raw_input, play_mode FROM batches ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
if row:
    print(f"最新记录: id={row[0]}, input={row[1]}, mode={row[2] if len(row) > 2 else 'NULL'}")

db.conn.close()

print("\n" + "="*60)
print("测试完成")
print("="*60)
