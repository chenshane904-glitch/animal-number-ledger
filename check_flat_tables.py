import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'flat_zodiac%'")
tables = cursor.fetchall()

if tables:
    print("平特一肖独立表已存在:")
    for t in tables:
        print(f"  {t[0]}")
else:
    print("平特一肖独立表不存在，需要创建")

conn.close()
