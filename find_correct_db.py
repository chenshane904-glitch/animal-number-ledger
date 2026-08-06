import os
import sqlite3

print("=" * 60)
print("查找包含ledgers表的数据库")
print("=" * 60)

# 搜索当前目录及子目录
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.db'):
            db_path = os.path.join(root, file)
            full_path = os.path.abspath(db_path)
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 获取所有表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in cursor.fetchall()]
                
                print(f"\n数据库: {full_path}")
                print(f"大小: {os.path.getsize(db_path) / 1024:.2f} KB")
                print(f"表: {', '.join(tables)}")
                
                # 如果有ledgers表，这是正确的数据库
                if 'ledgers' in tables:
                    print(">>> [正确的数据库] <<<")
                    
                    # 检查账本
                    cursor.execute("SELECT id, ledger_date, status FROM ledgers ORDER BY id DESC LIMIT 3")
                    print("\n最近账本:")
                    for row in cursor.fetchall():
                        print(f"  ID:{row[0]} | 日期:{row[1]} | 状态:{row[2]}")
                    
                    # 检查是否有input_history表
                    if 'input_history' in tables:
                        cursor.execute("SELECT COUNT(*) FROM input_history")
                        count = cursor.fetchone()[0]
                        print(f"\ninput_history记录数: {count}")
                    else:
                        print("\n[警告] 没有input_history表！")
                
                conn.close()
                
            except Exception as e:
                print(f"\n数据库: {full_path}")
                print(f"错误: {e}")

