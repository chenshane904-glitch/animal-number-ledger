import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

print("="*60)
print("Database Tables")
print("="*60)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for t in tables:
    print(f"  - {t[0]}")

print("\n" + "="*60)
print("Check batches table")
print("="*60)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batches'")
result = cursor.fetchone()
if result:
    print("OK batches table exists")
    cursor.execute("SELECT COUNT(*) FROM batches")
    count = cursor.fetchone()[0]
    print(f"  Records: {count}")

    if count > 0:
        cursor.execute("SELECT id, ledger_id, raw_input, play_mode FROM batches ORDER BY id DESC LIMIT 3")
        print("\n  Last 3 records:")
        for row in cursor.fetchall():
            print(f"    ID={row[0]}, ledger_id={row[1]}, input={row[2]}, mode={row[3]}")
else:
    print("ERROR batches table does NOT exist")

print("\n" + "="*60)
print("Check input_history table")
print("="*60)
cursor.execute("SELECT COUNT(*) FROM input_history")
count = cursor.fetchone()[0]
print(f"Records: {count}")

if count > 0:
    cursor.execute("SELECT id, batch_id, raw_input, play_mode FROM input_history ORDER BY id DESC LIMIT 3")
    print("\nLast 3 records:")
    for row in cursor.fetchall():
        print(f"  ID={row[0]}, batch_id={row[1]}, input={row[2]}, mode={row[3]}")

conn.close()
