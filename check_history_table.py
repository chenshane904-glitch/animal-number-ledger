import sqlite3

db_path = "data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查表结构
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='input_history'")
table_exists = cursor.fetchone()

if table_exists:
    print("[OK] input_history表存在")
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(input_history)")
    columns = cursor.fetchall()
    print("\n表结构:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 检查记录数
    cursor.execute("SELECT COUNT(*) FROM input_history")
    count = cursor.fetchone()[0]
    print(f"\n当前记录数: {count}")
    
    if count > 0:
        # 显示最近3条
        cursor.execute("""
            SELECT id, record_date, created_at, raw_input, entry_total, status
            FROM input_history
            ORDER BY created_at DESC
            LIMIT 3
        """)
        print("\n最近3条记录:")
        for row in cursor.fetchall():
            print(f"  ID:{row[0]} | 日期:{row[1]} | 时间:{row[2]} | 输入:{row[3][:30]} | 金额:{row[4]} | 状态:{row[5]}")
else:
    print("[ERROR] input_history表不存在")

conn.close()
