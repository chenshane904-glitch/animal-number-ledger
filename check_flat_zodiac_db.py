import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

print("="*60)
print("数据库表结构")
print("="*60)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("所有表:")
for t in tables:
    print(f"  - {t[0]}")

print("\n" + "="*60)
print("最近5条批次记录")
print("="*60)
cursor.execute("""
    SELECT id, ledger_id, raw_input, total_before, total_after, play_mode, created_at
    FROM batch
    ORDER BY id DESC
    LIMIT 5
""")
rows = cursor.fetchall()
print(f"{'ID':<5} {'Ledger':<8} {'RawInput':<20} {'Before':<10} {'After':<10} {'PlayMode':<12} {'CreatedAt'}")
print("-" * 100)
for row in rows:
    print(f"{row[0]:<5} {row[1]:<8} {row[2]:<20} {row[3]:<10} {row[4]:<10} {row[5] or 'NULL':<12} {row[6]}")

print("\n" + "="*60)
print("最近5条分配记录")
print("="*60)
cursor.execute("""
    SELECT id, batch_id, number, amount, source
    FROM allocation
    ORDER BY id DESC
    LIMIT 5
""")
rows = cursor.fetchall()
print(f"{'ID':<5} {'BatchID':<8} {'Number':<8} {'Amount':<10} {'Source':<30}")
print("-" * 80)
for row in rows:
    print(f"{row[0]:<5} {row[1]:<8} {row[2]:<8} {row[3]:<10} {row[4]:<30}")

print("\n" + "="*60)
print("最近5条输入历史记录")
print("="*60)
cursor.execute("""
    SELECT id, ledger_id, batch_id, raw_input, play_mode, entry_total, created_at
    FROM input_history
    ORDER BY id DESC
    LIMIT 5
""")
rows = cursor.fetchall()
print(f"{'ID':<5} {'Ledger':<8} {'Batch':<8} {'RawInput':<20} {'PlayMode':<12} {'Total':<10} {'CreatedAt'}")
print("-" * 100)
for row in rows:
    print(f"{row[0]:<5} {row[1]:<8} {row[2]:<8} {row[3]:<20} {row[4] or 'NULL':<12} {row[5]:<10} {row[6]}")

conn.close()
