from database import Database

print("Initializing database...")
db = Database('data.db')
print("Database initialized successfully!")

cursor = db.conn.cursor()

print("\nChecking tables...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables found:")
for t in tables:
    print(f"  - {t[0]}")

print("\nChecking batches table...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batches'")
result = cursor.fetchone()
if result:
    print("OK batches table exists")
else:
    print("ERROR batches table does NOT exist")

db.conn.close()
