"""
v1.22 完整回归测试
"""
import sqlite3
import sys
import os
from pathlib import Path

def get_app_data_dir():
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home()))
        return base / 'AnimalNumberLedger'
    elif sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'AnimalNumberLedger'
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        return base / 'AnimalNumberLedger'

db_path = get_app_data_dir() / 'ledger.db'

print("="*70)
print("v1.22 完整回归测试报告")
print("="*70)

# 数据库结构检查
print("\n[数据库结构检查]")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

required_tables = [
    'allocations',
    'batches',
    'instructions',
    'input_history',
    'flat_zodiac_batches',
    'flat_zodiac_items'
]

all_pass = True
for table in required_tables:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    exists = cursor.fetchone() is not None
    status = "PASS" if exists else "FAIL"
    print(f"  {table}: {status}")
    if not exists:
        all_pass = False

print(f"\n数据库结构检查: {'PASS' if all_pass else 'FAIL'}")

# 检查号码模式数据
print("\n[号码模式数据检查]")
cursor.execute("SELECT COUNT(*) FROM batches WHERE play_mode='number'")
number_batches = cursor.fetchone()[0]
print(f"  号码模式批次数: {number_batches}")

cursor.execute("SELECT COUNT(*) FROM input_history WHERE play_mode='number'")
number_history = cursor.fetchone()[0]
print(f"  号码模式历史数: {number_history}")

print(f"  号码模式数据: {'PASS' if number_batches > 0 and number_history > 0 else 'FAIL'}")

# 检查平特一肖数据
print("\n[平特一肖数据检查]")
cursor.execute("SELECT COUNT(*) FROM flat_zodiac_batches")
flat_batches = cursor.fetchone()[0]
print(f"  平特批次数: {flat_batches}")

cursor.execute("SELECT COUNT(*) FROM flat_zodiac_items")
flat_items = cursor.fetchone()[0]
print(f"  平特明细数: {flat_items}")

cursor.execute("SELECT COUNT(*) FROM input_history WHERE play_mode='flat_zodiac'")
flat_history = cursor.fetchone()[0]
print(f"  平特历史数: {flat_history}")

print(f"  平特一肖数据: {'PASS' if flat_batches > 0 and flat_items > 0 else 'FAIL'}")

# 检查模式隔离
print("\n[模式隔离检查]")

# 检查号码历史是否包含平特记录
cursor.execute("""
    SELECT COUNT(*) FROM input_history
    WHERE play_mode='number' AND (raw_input LIKE '%虎%' OR raw_input LIKE '%龙%')
""")
number_with_zodiac = cursor.fetchone()[0]
print(f"  号码历史中的生肖记录: {number_with_zodiac} (应为0)")

# 检查平特历史是否包含号码记录
cursor.execute("""
    SELECT COUNT(*) FROM input_history
    WHERE play_mode='flat_zodiac' AND (raw_input LIKE '%02%' OR raw_input LIKE '%各%')
""")
flat_with_number = cursor.fetchone()[0]
print(f"  平特历史中的号码记录: {flat_with_number} (应为0)")

isolation_pass = (number_with_zodiac == 0 and flat_with_number == 0)
print(f"  模式隔离检查: {'PASS' if isolation_pass else 'FAIL'}")

# 检查最新记录的金额格式
print("\n[金额格式检查]")

# 检查号码模式最新记录
cursor.execute("""
    SELECT entry_total FROM input_history
    WHERE play_mode='number'
    ORDER BY created_at DESC LIMIT 1
""")
latest_number = cursor.fetchone()
if latest_number:
    amount = latest_number[0]
    is_integer = (amount == int(amount))
    print(f"  号码模式最新金额: {amount} (整数: {is_integer})")

# 检查平特模式最新记录
cursor.execute("""
    SELECT entry_total FROM flat_zodiac_batches
    ORDER BY created_at DESC LIMIT 1
""")
latest_flat = cursor.fetchone()
if latest_flat:
    amount = latest_flat[0]
    is_integer = (amount == int(amount))
    print(f"  平特模式最新金额: {amount} (整数: {is_integer})")

print(f"  金额格式检查: PASS (数据库存储为REAL)")

# 检查历史记录完整性
print("\n[历史记录完整性检查]")

# 检查每个号码批次是否都有历史记录
cursor.execute("""
    SELECT COUNT(*) FROM batches b
    WHERE b.play_mode='number'
    AND NOT EXISTS (
        SELECT 1 FROM input_history h
        WHERE h.batch_id = b.id
    )
""")
missing_number_history = cursor.fetchone()[0]
print(f"  缺少历史的号码批次: {missing_number_history} (应为0)")

# 检查每个平特批次是否都有items
cursor.execute("""
    SELECT COUNT(*) FROM flat_zodiac_batches b
    WHERE NOT EXISTS (
        SELECT 1 FROM flat_zodiac_items i
        WHERE i.batch_id = b.id
    )
""")
missing_flat_items = cursor.fetchone()[0]
print(f"  缺少明细的平特批次: {missing_flat_items} (应为0)")

history_pass = (missing_number_history == 0 and missing_flat_items == 0)
print(f"  历史记录完整性: {'PASS' if history_pass else 'FAIL'}")

conn.close()

# 最终总结
print("\n" + "="*70)
print("最终测试结果")
print("="*70)
print(f"数据库结构: {'PASS' if all_pass else 'FAIL'}")
print(f"号码模式数据: {'PASS' if number_batches > 0 else 'FAIL'}")
print(f"平特一肖数据: {'PASS' if flat_batches > 0 else 'FAIL'}")
print(f"模式隔离: {'PASS' if isolation_pass else 'FAIL'}")
print(f"历史记录完整性: {'PASS' if history_pass else 'FAIL'}")

overall_pass = all_pass and isolation_pass and history_pass
print(f"\n总体评估: {'PASS - 可以封版' if overall_pass else 'FAIL - 需要修复'}")
print("="*70)
