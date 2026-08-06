"""测试统一查询接口"""
from database import Database
from play_mode import PlayMode

db = Database('data.db')

# 获取当前账本
from datetime import datetime
current_date = datetime.now().strftime('%Y-%m-%d')
ledger = db.get_or_create_active_ledger(current_date)

print("="*60)
print("测试统一查询接口：get_ledger_totals_by_mode()")
print("="*60)

print(f"\n当前账本: ID={ledger.id}, 日期={ledger.ledger_date}")

# 检查数据库中的批次
cursor = db.conn.cursor()
cursor.execute("SELECT id, play_mode, raw_input FROM batches WHERE ledger_id = ?", (ledger.id,))
batches = cursor.fetchall()
print(f"\n批次数: {len(batches)}")
for b in batches:
    print(f"  批次{b[0]}: mode={b[1]}, input={b[2]}")

print("\n" + "="*60)
print("测试：号码模式查询")
print("="*60)
number_totals = db.get_ledger_totals_by_mode(ledger.id, 'number')
print(f"返回类型: {type(number_totals)}")
print(f"返回数据（前5个非零）:")
count = 0
for num, amount in number_totals.items():
    if amount > 0 and count < 5:
        print(f"  号码{num:02d}: {amount/100}")
        count += 1
if count == 0:
    print("  无数据")

print("\n" + "="*60)
print("测试：平特一肖模式查询")
print("="*60)
animal_totals = db.get_ledger_totals_by_mode(ledger.id, 'flat_zodiac')
print(f"返回类型: {type(animal_totals)}")
print(f"返回数据:")
if animal_totals:
    for animal, amount in animal_totals.items():
        if amount > 0:
            print(f"  {animal}: {amount/100}")
else:
    print("  无数据")

# 检查 instructions 表
print("\n" + "="*60)
print("检查 instructions 表")
print("="*60)
cursor.execute("""
    SELECT i.id, i.target_type, i.targets, i.amount_integer, b.play_mode
    FROM instructions i
    JOIN batches b ON i.batch_id = b.id
    WHERE b.ledger_id = ?
""", (ledger.id,))
instructions = cursor.fetchall()
print(f"指令数: {len(instructions)}")
for inst in instructions:
    print(f"  ID={inst[0]}, type={inst[1]}, targets={inst[2]}, amount={inst[3]/100}, mode={inst[4]}")

db.conn.close()

print("\n" + "="*60)
print("测试完成")
print("="*60)
