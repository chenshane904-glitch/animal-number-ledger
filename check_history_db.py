import sqlite3
import os

db_path = os.path.join(os.environ['APPDATA'], 'AnimalNumberLedger', 'ledger.db')
print(f"数据库: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查记录数
cursor.execute("SELECT COUNT(*) FROM input_history")
count = cursor.fetchone()[0]
print(f"\n总记录数: {count}")

if count > 0:
    # 显示所有记录
    cursor.execute("""
        SELECT id, ledger_id, record_date, week_start, raw_input, entry_total, status
        FROM input_history
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    print("\n最近10条记录:")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"ID:{row[0]} | ledger:{row[1]} | 日期:{row[2]} | 周:{row[3]} | "
              f"输入:{row[4][:20]} | 金额:{row[5]/100:.2f} | {row[6]}")

conn.close()
