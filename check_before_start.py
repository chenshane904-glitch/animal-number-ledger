"""
启动程序前的最终检查
"""
import sqlite3

db_path = 'data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*60)
print("启动程序前的数据库状态")
print("="*60)

# 检查账本
cursor.execute("SELECT id, ledger_date, status FROM ledgers")
ledgers = cursor.fetchall()
print(f"\n账本数: {len(ledgers)}")
for l in ledgers:
    print(f"  账本{l[0]}: {l[1]}, status={l[2]}")

# 检查批次
cursor.execute("SELECT id, play_mode, raw_input FROM batches ORDER BY id")
batches = cursor.fetchall()
print(f"\n批次数: {len(batches)}")
for b in batches:
    mode = b[1] if b[1] else 'NULL'
    input_preview = b[2][:20] if b[2] else ''
    print(f"  批次{b[0]}: mode={mode}, input={input_preview}...")

# 检查指令
cursor.execute("SELECT COUNT(*) FROM instructions")
inst_count = cursor.fetchone()[0]
print(f"\n指令数: {inst_count}")

# 检查分配
cursor.execute("SELECT COUNT(*) FROM allocations")
alloc_count = cursor.fetchone()[0]
print(f"分配数: {alloc_count}")

# 统计每种模式的数据
print("\n按模式统计:")
cursor.execute("""
    SELECT play_mode, COUNT(*) as cnt
    FROM batches
    GROUP BY play_mode
""")
for row in cursor.fetchall():
    mode = row[0] if row[0] else 'NULL'
    print(f"  {mode}: {row[1]} 批次")

conn.close()

print("\n" + "="*60)
print("准备就绪，可以启动程序测试")
print("="*60)
print("\n测试步骤:")
print("1. 启动程序")
print("2. 切换到【平特一肖】模式")
print("3. 输入：虎100\\n龙200")
print("4. 点击【确认追加】")
print("5. 检查右侧是否显示：虎100、龙200、今日总下注300")
print("6. 打开历史记录，检查是否有这笔数据")
print("7. 切换回【号码模式】，验证号码数据正常")
