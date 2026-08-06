"""清空测试数据，重新测试"""
import sqlite3
import os

db_path = 'data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("清空测试数据...")

# 清空所有数据（保留表结构）
cursor.execute("DELETE FROM allocations")
cursor.execute("DELETE FROM instructions")
cursor.execute("DELETE FROM batches")
cursor.execute("DELETE FROM input_history")
cursor.execute("DELETE FROM ledgers")

conn.commit()

print("验证清空结果:")
for table in ['allocations', 'instructions', 'batches', 'input_history', 'ledgers']:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count} 条记录")

conn.close()
print("\n数据已清空，可以重新测试。")
