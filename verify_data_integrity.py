"""验证号码模式数据完整性"""
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
print(f"验证号码模式数据完整性")
print("="*70)

conn = sqlite3.connect(str(real_db_path))
cursor = conn.cursor()

# 检查 allocations 记录数
cursor.execute("SELECT COUNT(*) FROM allocations")
alloc_count = cursor.fetchone()[0]
print(f"\nallocations 记录数: {alloc_count}")
print(f"预期: 707")
print(f"状态: {'✓ 正常' if alloc_count == 707 else '✗ 异常'}")

# 检查 flat_zodiac 表记录数
cursor.execute("SELECT COUNT(*) FROM flat_zodiac_batches")
flat_batch_count = cursor.fetchone()[0]
print(f"\nflat_zodiac_batches 记录数: {flat_batch_count}")

cursor.execute("SELECT COUNT(*) FROM flat_zodiac_items")
flat_item_count = cursor.fetchone()[0]
print(f"flat_zodiac_items 记录数: {flat_item_count}")

conn.close()

print("\n" + "="*70)
if alloc_count == 707:
    print("号码模式数据完整 ✓")
else:
    print("警告：号码模式数据可能被修改")
print("="*70)
