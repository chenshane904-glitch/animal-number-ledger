import sqlite3
import os
import json

# 用户明确要求的正确映射
CORRECT_MAPPING = {
    "鼠": [7, 19, 31, 43],
    "牛": [6, 18, 30, 42],
    "虎": [3, 15, 27, 39],  # 用户明确要求
    "兔": [4, 16, 28, 40],
    "龙": [5, 17, 29, 41],
    "蛇": [2, 14, 26, 38],
    "马": [1, 13, 25, 37, 49],
    "羊": [12, 24, 36, 48],
    "猴": [11, 23, 35, 47],
    "鸡": [10, 22, 34, 46],
    "狗": [9, 21, 33, 45],
    "猪": [8, 20, 32, 44]
}

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 更新数据库中的映射
cursor.execute("""
    UPDATE settings 
    SET value = ? 
    WHERE key = 'animal_mapping'
""", (json.dumps(CORRECT_MAPPING, ensure_ascii=False),))

conn.commit()
conn.close()

print("=== 已更新数据库中的生肖映射 ===")
print("虎: [3, 15, 27, 39]")
print("龙: [5, 17, 29, 41]")
print("")
print("[OK] 数据库更新完成")
