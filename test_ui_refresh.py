"""测试 UI 刷新逻辑"""
from database import Database
from play_mode import PlayMode
from play_mode_config import get_animals_list
from calculator_factory import CalculatorFactory
from constants import AMOUNT_MULTIPLIER

print("="*60)
print("测试 UI 刷新逻辑")
print("="*60)

db = Database('data.db')

# 获取当前账本
from datetime import datetime
current_date = datetime.now().strftime('%Y-%m-%d')
current_ledger = db.get_or_create_active_ledger(current_date)

print(f"\n当前账本: ID={current_ledger.id}, 日期={current_ledger.ledger_date}")

print("\n" + "="*60)
print("模拟 _update_animal_mode_display()")
print("="*60)

# 获取当前累计（号码维度）
current_totals = db.get_ledger_totals(current_ledger.id)
print(f"\n从数据库获取的号码累计（前10个）:")
for num in range(1, 11):
    amount = current_totals.get(num, 0)
    if amount > 0:
        print(f"  号码{num:02d}: {amount/100}")

# 获取动物映射和计算器
animal_mapping = db.get_animal_mapping()
calculator = CalculatorFactory.get_calculator(PlayMode.NUMBER, animal_mapping)

# 转换为生肖维度
animals = get_animals_list(PlayMode.FLAT_ZODIAC)
animal_amounts = {animal: 0 for animal in animals}

print(f"\n生肖列表: {animals}")

# 从号码累计转换为生肖累计
print(f"\n转换号码->生肖:")
for num, amount_int in current_totals.items():
    animal = calculator.number_to_animal.get(str(num).zfill(2))
    if animal and animal in animal_amounts:
        animal_amounts[animal] += amount_int
        if amount_int > 0:
            print(f"  号码{num:02d} -> {animal}: {amount_int/100}")

# 计算统计
total = sum(animal_amounts.values())
non_zero = sum(1 for amt in animal_amounts.values() if amt > 0)

# 找出最大金额的生肖
max_animal = "--"
max_amount_int = 0
for animal, amount_int in animal_amounts.items():
    if amount_int > max_amount_int:
        max_amount_int = amount_int
        max_animal = animal

print(f"\n统计结果:")
print(f"  今日总下注: {total / AMOUNT_MULTIPLIER:.2f}")
print(f"  非零生肖: {non_zero}")
print(f"  最高下注生肖: {max_animal}")
print(f"  最高金额: {max_amount_int / AMOUNT_MULTIPLIER:.2f}")

print(f"\n生肖金额明细:")
for animal in animals:
    amount = animal_amounts[animal]
    if amount > 0:
        print(f"  {animal}: {amount / AMOUNT_MULTIPLIER:.2f}")

print("\n" + "="*60)
print("检查历史记录")
print("="*60)

cursor = db.conn.cursor()
cursor.execute("""
    SELECT id, raw_input, entry_total, play_mode
    FROM input_history
    WHERE ledger_id = ?
    ORDER BY id DESC
    LIMIT 5
""", (current_ledger.id,))

rows = cursor.fetchall()
print(f"\n历史记录数: {len(rows)}")
for row in rows:
    print(f"  ID={row[0]}, input={row[1]}, total={row[2]/100}, mode={row[3]}")

db.conn.close()

print("\n" + "="*60)
print("测试完成")
print("="*60)
