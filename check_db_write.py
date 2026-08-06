"""检查平特一肖数据是否正确写入真实数据库"""
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
print(f"检查真实数据库写入")
print(f"数据库: {real_db_path}")
print("="*70)

conn = sqlite3.connect(str(real_db_path))
cursor = conn.cursor()

# 检查 flat_zodiac_batches
print("\n【flat_zodiac_batches 最新记录】")
cursor.execute("""
    SELECT id, ledger_id, raw_input, entry_total, status, created_at
    FROM flat_zodiac_batches
    ORDER BY id DESC
    LIMIT 3
""")
batches = cursor.fetchall()

if batches:
    for row in batches:
        print(f"\nBatch ID: {row[0]}")
        print(f"  Ledger ID: {row[1]}")
        print(f"  Raw Input: {row[2]}")
        print(f"  Entry Total: {row[3]}")
        print(f"  Status: {row[4]}")
        print(f"  Created: {row[5]}")

        # 查询对应的 items
        cursor.execute("""
            SELECT zodiac, amount, odds, payout
            FROM flat_zodiac_items
            WHERE batch_id = ?
        """, (row[0],))
        items = cursor.fetchall()
        print(f"  Items ({len(items)}):")
        for item in items:
            print(f"    {item[0]}: amount={item[1]}, odds={item[2]}, payout={item[3]}")
else:
    print("没有记录")

# 检查 allocations 是否被污染
print("\n" + "="*70)
print("【allocations 完整性检查】")
print("="*70)
cursor.execute("SELECT COUNT(*) FROM allocations")
alloc_count = cursor.fetchone()[0]
print(f"allocations 记录数: {alloc_count}")
print(f"预期: 707")
print(f"状态: {'正常' if alloc_count == 707 else '异常 - 被污染'}")

conn.close()
