import sqlite3
import os
import json

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT animal_name, numbers_json FROM animal_mapping ORDER BY animal_name")
rows = cursor.fetchall()

print("=== 数据库中的生肖号码映射 ===")
for animal, numbers_json in rows:
    numbers = json.loads(numbers_json)
    print(f"{animal}: {', '.join(numbers)}")

conn.close()
