import sqlite3
import os

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=== 数据库中的表 ===")
for table in tables:
    print(f"  {table[0]}")

# 检查是否有mapping相关的配置
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%mapping%'")
mapping_tables = cursor.fetchall()

if mapping_tables:
    print("\n=== Mapping相关的表 ===")
    for table in mapping_tables:
        print(f"  {table[0]}")
else:
    print("\n[INFO] 没有mapping表，可能存储在JSON文件中")

conn.close()
