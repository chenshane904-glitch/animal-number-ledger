import sqlite3
import os

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看allocations表结构
cursor.execute("PRAGMA table_info(allocations)")
columns = cursor.fetchall()
print("allocations表结构：")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\n最近20条allocations记录：")
cursor.execute("""
    SELECT id, ledger_id, number, animal, amount_integer, instruction_id
    FROM allocations
    ORDER BY id DESC
    LIMIT 20
""")

for row in cursor.fetchall():
    print(f"ID:{row[0]}, 账本:{row[1]}, 号码:{row[2]}, 生肖:{row[3]}, 金额:{row[4]/100:.2f}")

conn.close()
