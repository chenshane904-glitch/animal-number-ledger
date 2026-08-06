"""检查 input_history 表"""
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
print("检查 input_history 表")
print("="*70)

conn = sqlite3.connect(str(real_db_path))
cursor = conn.cursor()

# 检查表结构
cursor.execute("PRAGMA table_info(input_history)")
columns = cursor.fetchall()
print("\n表结构:")
for col in columns:
    print(f"  {col[1]} {col[2]}")

# 检查记录数
cursor.execute("SELECT COUNT(*) FROM input_history")
count = cursor.fetchone()[0]
print(f"\n总记录数: {count}")

# 按 play_mode 分组
cursor.execute("SELECT play_mode, COUNT(*) FROM input_history GROUP BY play_mode")
print("\n按 play_mode 分组:")
for row in cursor.fetchall():
    print(f"  {row[0] if row[0] else 'NULL'}: {row[1]} 条")

# 最近10条记录
cursor.execute("""
    SELECT id, ledger_id, record_date, play_mode, entry_total, raw_input, status
    FROM input_history
    ORDER BY id DESC
    LIMIT 10
""")
print("\n最近10条记录:")
for row in cursor.fetchall():
    print(f"  ID={row[0]}, Ledger={row[1]}, Date={row[2]}, Mode={row[3]}, Total={row[4]}, Input={row[5][:20] if row[5] else 'NULL'}...")

conn.close()
