import os
import sqlite3

# 检查数据库文件位置
print("=" * 60)
print("数据库文件检查")
print("=" * 60)

db_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.db'):
            full_path = os.path.abspath(os.path.join(root, file))
            db_files.append(full_path)

print(f"\n找到 {len(db_files)} 个数据库文件:")
for db in db_files:
    size = os.path.getsize(db) / 1024
    print(f"  {db} ({size:.2f} KB)")

# 检查主数据库
main_db = "data.db"
if os.path.exists(main_db):
    print(f"\n主数据库: {os.path.abspath(main_db)}")
    
    conn = sqlite3.connect(main_db)
    cursor = conn.cursor()
    
    # 列出所有表
    print("\n所有表:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")
    
    # 检查input_history表
    if ('input_history',) in tables:
        print("\n[OK] input_history表存在")
        
        # 表结构
        cursor.execute("PRAGMA table_info(input_history)")
        print("\n字段:")
        for col in cursor.fetchall():
            print(f"  {col[1]} {col[2]}")
        
        # 记录数
        cursor.execute("SELECT COUNT(*) FROM input_history")
        count = cursor.fetchone()[0]
        print(f"\n记录总数: {count}")
        
        if count > 0:
            # 显示所有记录
            cursor.execute("""
                SELECT id, ledger_id, record_date, created_at, raw_input, 
                       entry_total, status
                FROM input_history
                ORDER BY created_at DESC
            """)
            print("\n所有记录:")
            for row in cursor.fetchall():
                print(f"  ID:{row[0]} | ledger:{row[1]} | 日期:{row[2]} | "
                      f"时间:{row[3]} | 输入:{row[4][:20]} | 金额:{row[5]/100:.2f} | {row[6]}")
    else:
        print("\n[ERROR] input_history表不存在！")
    
    # 检查当前账本
    print("\n当前账本:")
    cursor.execute("SELECT id, ledger_date, status FROM ledgers ORDER BY id DESC LIMIT 3")
    for row in cursor.fetchall():
        print(f"  ID:{row[0]} | 日期:{row[1]} | 状态:{row[2]}")
    
    conn.close()
else:
    print(f"\n[ERROR] 主数据库不存在: {os.path.abspath(main_db)}")

