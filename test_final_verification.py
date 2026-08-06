"""
自动化验证脚本：模拟完整的 UI 流程
不启动 GUI，直接调用后台逻辑
"""
import json
from database import Database
from flat_zodiac_parser import FlatZodiacParser
from calculator_factory import CalculatorFactory
from play_mode import PlayMode
from play_mode_config import get_animals_list
from models import Batch
from datetime import datetime
from constants import AMOUNT_MULTIPLIER

print("="*60)
print("自动化验证：平特一肖完整流程")
print("="*60)

# 初始化数据库
db = Database('data.db')
current_date = datetime.now().strftime('%Y-%m-%d')
ledger = db.get_or_create_active_ledger(current_date)
animal_mapping = db.get_animal_mapping()

print(f"\nOK 初始化完成")
print(f"  账本ID: {ledger.id}")
print(f"  日期: {ledger.ledger_date}")

# ============================================================
# 模拟用户操作：输入 虎100 龙200
# ============================================================

input_text = """虎100
龙200"""

print(f"\n{'='*60}")
print("步骤1：用户输入")
print("="*60)
print(input_text)

# ============================================================
# 解析
# ============================================================

print(f"\n{'='*60}")
print("步骤2：解析输入")
print("="*60)

parser = FlatZodiacParser()
instructions = parser.parse_input(input_text)

print(f"OK 解析成功: {len(instructions)} 条指令")
for idx, inst in enumerate(instructions, 1):
    print(f"  指令{idx}: {inst.targets[0]} → {inst.amount_integer/100}元")

# ============================================================
# 计算
# ============================================================

print(f"\n{'='*60}")
print("步骤3：计算结果")
print("="*60)

calculator = CalculatorFactory.get_calculator(PlayMode.FLAT_ZODIAC, animal_mapping)
animals = get_animals_list(PlayMode.FLAT_ZODIAC)
current_totals = {animal: 0 for animal in animals}

result = calculator.calculate(instructions, current_totals)

print(f"OK 计算成功:")
print(f"  本次总数: {result.total_amount/100}元")
print(f"  涉及生肖: {result.non_zero_count}")
for animal, amount in result.animal_amounts.items():
    if amount > 0:
        print(f"    {animal}: {amount/100}元")

# ============================================================
# 保存到数据库（模拟 _confirm_add）
# ============================================================

print(f"\n{'='*60}")
print("步骤4：保存到数据库")
print("="*60)

batch = Batch(
    raw_input=input_text,
    total_before=0,
    total_after=result.total_amount,
    mapping_snapshot=json.dumps(animal_mapping, ensure_ascii=False),
    instructions=instructions
)

cursor = db.conn.cursor()

# 保存批次
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

print(f"OK 保存成功:")
print(f"  批次ID: {batch_id}")
print(f"  指令数: {len(instructions)}")

# ============================================================
# UI 刷新（模拟 _update_animal_mode_display）
# ============================================================

print(f"\n{'='*60}")
print("步骤5：UI 刷新显示")
print("="*60)

# 使用统一查询接口
animal_amounts = db.get_ledger_totals_by_mode(ledger.id, 'flat_zodiac')

# 确保所有生肖都有初始值
for animal in animals:
    if animal not in animal_amounts:
        animal_amounts[animal] = 0

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

print(f"OK 右侧显示:")
print(f"  今日总下注: {total / AMOUNT_MULTIPLIER:.2f}")
print(f"  非零生肖: {non_zero}")
print(f"  最高下注生肖: {max_animal}")
print(f"  最高金额: {max_amount_int / AMOUNT_MULTIPLIER:.2f}")

print(f"\n  12生肖金额明细:")
for animal in animals:
    amount = animal_amounts[animal]
    if amount > 0:
        print(f"    {animal}: {amount / AMOUNT_MULTIPLIER:.2f}")
    else:
        print(f"    {animal}: --")

# ============================================================
# 历史记录（检查是否需要保存）
# ============================================================

print(f"\n{'='*60}")
print("步骤6：检查历史记录")
print("="*60)

cursor.execute("""
    SELECT COUNT(*) FROM input_history WHERE ledger_id = ?
""", (ledger.id,))
history_count = cursor.fetchone()[0]

print(f"历史记录数: {history_count}")
print("注意: input_history 由 _save_input_history() 保存")
print("      本测试脚本未调用该方法，实际 UI 会自动保存")

db.conn.close()

# ============================================================
# 最终验证
# ============================================================

print(f"\n{'='*60}")
print("验证结果")
print("="*60)

success = True
errors = []

if total != 30000:  # 300元 = 30000分
    success = False
    errors.append(f"总金额错误: 期望300.00，实际{total/100:.2f}")

if non_zero != 2:
    success = False
    errors.append(f"非零生肖数错误: 期望2，实际{non_zero}")

if animal_amounts.get('虎', 0) != 10000:  # 100元 = 10000分
    success = False
    errors.append(f"虎的金额错误: 期望100.00，实际{animal_amounts.get('虎', 0)/100:.2f}")

if animal_amounts.get('龙', 0) != 20000:  # 200元 = 20000分
    success = False
    errors.append(f"龙的金额错误: 期望200.00，实际{animal_amounts.get('龙', 0)/100:.2f}")

if success:
    print("OK 所有验证通过!")
    print("\n结论:")
    print("  1. 解析成功 OK")
    print("  2. 计算成功 OK")
    print("  3. 数据库写入成功 OK")
    print("  4. UI刷新成功 OK")
    print("  5. 数据正确显示 OK")
else:
    print("ERROR 验证失败:")
    for err in errors:
        print(f"  - {err}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
