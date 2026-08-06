import sqlite3
import os

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 这些批次ID是平特模式被错误保存为号码模式的记录
wrong_batch_ids = [54, 55, 56, 57]

print("删除错误的测试数据...")
for batch_id in wrong_batch_ids:
    # 删除allocations
    cursor.execute("DELETE FROM allocations WHERE instruction_id IN (SELECT id FROM instructions WHERE batch_id = ?)", (batch_id,))
    print(f"  删除批次{batch_id}的allocations: {cursor.rowcount}条")
    
    # 删除instructions
    cursor.execute("DELETE FROM instructions WHERE batch_id = ?", (batch_id,))
    print(f"  删除批次{batch_id}的instructions: {cursor.rowcount}条")
    
    # 删除input_history
    cursor.execute("DELETE FROM input_history WHERE batch_id = ?", (batch_id,))
    print(f"  删除批次{batch_id}的input_history: {cursor.rowcount}条")
    
    # 删除batch
    cursor.execute("DELETE FROM batches WHERE id = ?", (batch_id,))
    print(f"  删除批次{batch_id}的batches: {cursor.rowcount}条")

conn.commit()
conn.close()

print("\n[OK] 错误数据已清理")
