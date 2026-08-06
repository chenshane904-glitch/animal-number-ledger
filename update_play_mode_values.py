import sqlite3
import os

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 更新input_history表
cursor.execute("UPDATE input_history SET play_mode = 'flat_zodiac' WHERE play_mode = 'animal'")
updated_history = cursor.rowcount

# 更新batches表
cursor.execute("UPDATE batches SET play_mode = 'flat_zodiac' WHERE play_mode = 'animal'")
updated_batches = cursor.rowcount

conn.commit()
conn.close()

print(f"[OK] 已更新 input_history 表: {updated_history} 条记录")
print(f"[OK] 已更新 batches 表: {updated_batches} 条记录")
