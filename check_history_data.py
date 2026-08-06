"""确认真实数据库历史数据存在情况"""
import sqlite3
import sys
import os
from pathlib import Path

def get_app_data_dir() -> Path:
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home()))
        app_dir = base / 'AnimalNumberLedger'
    elif sys.platform == 'darwin':
        app_dir = Path.home() / 'Library' / 'Application Support' / 'AnimalNumberLedger'
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        app_dir = base / 'AnimalNumberLedger'
    return app_dir

real_db_path = get_app_data_dir() / 'ledger.db'

print("="*70)
print("真实数据库历史数据检查")
print("="*70)
print(f"\n1. 数据库绝对路径：")
print(f"   {real_db_path}")
print(f"   存在: {real_db_path.exists()}")

conn = sqlite3.connect(str(real_db_path))
cursor = conn.cursor()

# 2. 全部表名
print(f"\n2. 全部表名：")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
for table in tables:
    print(f"   - {table}")

# 3-7. 各表记录数量
print(f"\n3-7. 各表记录数量：")
cursor.execute("SELECT COUNT(*) FROM batches")
batches_count = cursor.fetchone()[0]
print(f"   batches: {batches_count}")

cursor.execute("SELECT COUNT(*) FROM instructions")
instructions_count = cursor.fetchone()[0]
print(f"   instructions: {instructions_count}")

cursor.execute("SELECT COUNT(*) FROM allocations")
allocations_count = cursor.fetchone()[0]
print(f"   allocations: {allocations_count}")

cursor.execute("SELECT COUNT(*) FROM flat_zodiac_batches")
flat_batches_count = cursor.fetchone()[0]
print(f"   flat_zodiac_batches: {flat_batches_count}")

cursor.execute("SELECT COUNT(*) FROM flat_zodiac_items")
flat_items_count = cursor.fetchone()[0]
print(f"   flat_zodiac_items: {flat_items_count}")

# 8. 最近20条号码模式批次
print(f"\n8. 最近20条号码模式批次（play_mode='number' 或 NULL）：")
cursor.execute("""
    SELECT id, ledger_id, raw_input, total_after, play_mode, created_at
    FROM batches
    WHERE play_mode = 'number' OR play_mode IS NULL OR play_mode = ''
    ORDER BY id DESC
    LIMIT 20
""")
number_batches = cursor.fetchall()
print(f"   找到 {len(number_batches)} 条记录:")
for row in number_batches[:5]:  # 只显示前5条
    print(f"   ID={row[0]}, Ledger={row[1]}, Mode={row[4]}, Input={row[2][:30] if row[2] else 'NULL'}...")

# 9. 最近20条平特一肖批次
print(f"\n9. 最近20条平特一肖批次：")
cursor.execute("""
    SELECT b.id, b.ledger_id, b.raw_input, b.entry_total, b.status, b.created_at
    FROM flat_zodiac_batches b
    ORDER BY b.id DESC
    LIMIT 20
""")
flat_batches = cursor.fetchall()
print(f"   找到 {len(flat_batches)} 条记录:")
for row in flat_batches:
    print(f"\n   Batch ID: {row[0]}")
    print(f"      Ledger: {row[1]}")
    print(f"      Input: {row[2]}")
    print(f"      Total: {row[3]}")
    print(f"      Status: {row[4]}")
    print(f"      Created: {row[5]}")

    # 查询关联的生肖和金额
    cursor.execute("""
        SELECT zodiac, amount, odds, payout
        FROM flat_zodiac_items
        WHERE batch_id = ?
    """, (row[0],))
    items = cursor.fetchall()
    print(f"      生肖明细:")
    for item in items:
        print(f"         {item[0]}: amount={item[1]}, odds={item[2]}, payout={item[3]}")

conn.close()

print("\n" + "="*70)
print("结论：数据是否真实存在？")
print("="*70)
print(f"号码模式批次: {len(number_batches)} 条")
print(f"平特一肖批次: {len(flat_batches)} 条")
if len(number_batches) > 0 or len(flat_batches) > 0:
    print("数据真实存在，历史窗口显示问题在查询或渲染层")
else:
    print("警告：数据库中没有历史数据")
