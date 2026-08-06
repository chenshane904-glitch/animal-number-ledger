"""检查真实数据库结构"""
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

# 真实数据库路径
real_db_path = get_app_data_dir() / 'ledger.db'

print("="*70)
print(f"真实数据库: {real_db_path}")
print("="*70)

conn = sqlite3.connect(str(real_db_path))
cursor = conn.cursor()

# 列出所有表
print("\n【所有表】")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
for table in tables:
    print(f"  {table}")

print(f"\n总共 {len(tables)} 张表")

# 检查关键表结构
print("\n" + "="*70)
print("【关键表结构】")
print("="*70)

for table_name in ['batches', 'allocations', 'instructions', 'flat_zodiac_batches', 'flat_zodiac_items']:
    print(f"\n--- {table_name} ---")
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        if columns:
            print(f"存在，字段数: {len(columns)}")
            for col in columns:
                print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PK' if col[5] else ''}")
        else:
            print("不存在")
    except Exception as e:
        print(f"不存在: {e}")

# 检查 batches 是否有 play_mode 字段
print("\n" + "="*70)
print("【batches 表 play_mode 字段检查】")
print("="*70)
cursor.execute("PRAGMA table_info(batches)")
columns = cursor.fetchall()
has_play_mode = any(col[1] == 'play_mode' for col in columns)
print(f"batches 是否有 play_mode 字段: {has_play_mode}")

# 检查数据库版本
print("\n" + "="*70)
print("【数据库版本】")
print("="*70)
cursor.execute("PRAGMA user_version")
user_version = cursor.fetchone()[0]
print(f"user_version: {user_version}")

# 检查是否有平特一肖迁移记录
print("\n" + "="*70)
print("【迁移检查】")
print("="*70)
print(f"flat_zodiac_batches 存在: {'flat_zodiac_batches' in tables}")
print(f"flat_zodiac_items 存在: {'flat_zodiac_items' in tables}")

conn.close()
