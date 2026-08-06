import sqlite3
import os

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("最近30条allocations记录（按ID倒序）：")
print("="*70)
cursor.execute("""
    SELECT id, instruction_id, number, animal, amount_integer
    FROM allocations
    ORDER BY id DESC
    LIMIT 30
""")

for row in cursor.fetchall():
    print(f"ID:{row[0]:4d}, 指令ID:{row[1]:4d}, 号码:{row[2]:02d}, 生肖:{row[3]:4s}, 金额:{row[4]/100:8.2f}")

# 查询最近几条虎和龙的记录
print("\n"+"="*70)
print("查找最近的'虎'和'龙'记录：")
print("="*70)
cursor.execute("""
    SELECT id, instruction_id, number, animal, amount_integer
    FROM allocations
    WHERE animal IN ('虎', '龙')
    ORDER BY id DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"ID:{row[0]:4d}, 指令ID:{row[1]:4d}, 号码:{row[2]:02d}, 生肖:{row[3]:4s}, 金额:{row[4]/100:8.2f}")

conn.close()
