import sqlite3
import os

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(batches)")
columns = cursor.fetchall()

print("batches表结构：")
for col in columns:
    print(f"  {col[1]:20s} {col[2]:15s} NOT NULL={col[3]} DEFAULT={col[4]}")

conn.close()
