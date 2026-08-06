import sqlite3
import os
import json

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT value FROM settings WHERE key = 'animal_mapping'")
row = cursor.fetchone()

if row:
    mapping = json.loads(row[0])
    print("=== 数据库中存储的生肖映射 ===")
    for animal in ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]:
        if animal in mapping:
            numbers = mapping[animal]
            print(f"{animal}: {numbers}")
else:
    print("[INFO] 数据库中没有animal_mapping，将使用constants.py中的DEFAULT_ANIMAL_MAPPING")

conn.close()
