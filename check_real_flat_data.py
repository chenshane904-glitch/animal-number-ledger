"""检查真实数据库中的平特一肖相关数据"""
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
print(f"真实数据库: {real_db_path}")
print("="*70)

conn = sqlite3.connect(str(real_db_path))
cursor = conn.cursor()

# 检查 batches 表中是否有 play_mode='flat_zodiac' 的记录
print("\n【batches 表中的 flat_zodiac 记录】")
cursor.execute("""
    SELECT id, ledger_id, raw_input, play_mode, created_at
    FROM batches
    WHERE play_mode = 'flat_zodiac'
    ORDER BY created_at DESC
    LIMIT 20
""")
flat_batches = cursor.fetchall()

if flat_batches:
    print(f"找到 {len(flat_batches)} 条 flat_zodiac 记录:")
    for row in flat_batches:
        print(f"  Batch ID={row[0]}, Ledger={row[1]}, Mode={row[3]}")
        print(f"    Input: {row[2][:50]}...")
        print(f"    Created: {row[4]}")
else:
    print("没有任何 flat_zodiac 记录")

# 检查 instructions 表中关联的记录
if flat_batches:
    print("\n【instructions 表中关联的记录】")
    for batch in flat_batches[:3]:  # 只看前3条
        batch_id = batch[0]
        cursor.execute("""
            SELECT id, target_type, targets, amount_integer
            FROM instructions
            WHERE batch_id = ?
        """, (batch_id,))
        instructions = cursor.fetchall()
        print(f"\nBatch {batch_id} 的 instructions ({len(instructions)} 条):")
        for inst in instructions:
            print(f"  ID={inst[0]}, Type={inst[1]}, Targets={inst[2]}, Amount={inst[3]}")

# 检查是否有虎、龙的记录
print("\n【搜索虎、龙相关记录】")
cursor.execute("""
    SELECT b.id, b.ledger_id, b.raw_input, b.play_mode, i.targets, i.amount_integer
    FROM batches b
    JOIN instructions i ON b.id = i.batch_id
    WHERE (i.targets LIKE '%虎%' OR i.targets LIKE '%龙%')
    ORDER BY b.created_at DESC
    LIMIT 10
""")
tiger_dragon = cursor.fetchall()

if tiger_dragon:
    print(f"找到 {len(tiger_dragon)} 条包含虎/龙的记录:")
    for row in tiger_dragon:
        print(f"  Batch={row[0]}, Ledger={row[1]}, Mode={row[3]}")
        print(f"    Input: {row[2][:30]}...")
        print(f"    Targets: {row[4]}, Amount: {row[5]}")
else:
    print("没有找到虎/龙相关记录")

# 检查 allocations 表是否受影响
print("\n【allocations 表记录数】")
cursor.execute("SELECT COUNT(*) FROM allocations")
alloc_count = cursor.fetchone()[0]
print(f"allocations 总记录数: {alloc_count}")

if alloc_count > 0:
    cursor.execute("""
        SELECT a.id, a.number, a.animal, a.amount_integer, i.batch_id
        FROM allocations a
        JOIN instructions i ON a.instruction_id = i.id
        JOIN batches b ON i.batch_id = b.id
        WHERE b.play_mode = 'flat_zodiac'
        LIMIT 10
    """)
    flat_allocs = cursor.fetchall()
    if flat_allocs:
        print(f"\n警告：发现 {len(flat_allocs)} 条 flat_zodiac 的 allocations:")
        for row in flat_allocs:
            print(f"  ID={row[0]}, Number={row[1]}, Animal={row[2]}, Amount={row[3]}, Batch={row[4]}")
    else:
        print("没有 flat_zodiac 相关的 allocations（正确）")

conn.close()
