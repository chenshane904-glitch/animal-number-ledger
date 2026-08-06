import sqlite3
import os
import json

db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*70)
print("【第一部分：检查最近的批次记录】")
print("="*70)

# 查询最近10条批次记录
cursor.execute("""
    SELECT 
        id, ledger_id, raw_input, play_mode, 
        total_before, total_after, created_at
    FROM batches 
    ORDER BY id DESC 
    LIMIT 10
""")

batches = cursor.fetchall()
print(f"\n最近10条批次记录（batches表）：")
print("-"*70)
for row in batches:
    print(f"批次ID: {row[0]}")
    print(f"  账本ID: {row[1]}")
    print(f"  原始输入: {row[2]}")
    print(f"  play_mode: {row[3]}")
    print(f"  之前总额: {row[4] / 100:.2f}")
    print(f"  之后总额: {row[5] / 100:.2f}")
    print(f"  创建时间: {row[6]}")
    print("-"*70)

print("\n【第二部分：检查最近的分配记录】")
print("="*70)

# 查询最近10条分配记录
cursor.execute("""
    SELECT 
        a.id, a.batch_id, a.number, a.animal, 
        a.amount_integer, b.raw_input, b.play_mode
    FROM allocations a
    JOIN batches b ON a.batch_id = b.id
    ORDER BY a.id DESC 
    LIMIT 20
""")

allocations = cursor.fetchall()
print(f"\n最近20条分配记录（allocations表）：")
print("-"*70)
for row in allocations:
    print(f"分配ID: {row[0]}, 批次ID: {row[1]}")
    print(f"  号码: {row[2]}, 生肖: {row[3]}")
    print(f"  金额: {row[4] / 100:.2f}")
    print(f"  原始输入: {row[5]}")
    print(f"  play_mode: {row[6]}")
    print("-"*70)

print("\n【第三部分：检查最近的历史记录】")
print("="*70)

# 查询最近10条历史记录
cursor.execute("""
    SELECT 
        id, ledger_id, batch_id, raw_input, 
        play_mode, entry_total, created_at
    FROM input_history 
    ORDER BY id DESC 
    LIMIT 10
""")

histories = cursor.fetchall()
print(f"\n最近10条历史记录（input_history表）：")
print("-"*70)
for row in histories:
    print(f"历史ID: {row[0]}")
    print(f"  账本ID: {row[1]}, 批次ID: {row[2]}")
    print(f"  原始输入: {row[3]}")
    print(f"  play_mode: {row[4]}")
    print(f"  本次总额: {row[5] / 100:.2f}")
    print(f"  创建时间: {row[6]}")
    print("-"*70)

conn.close()
