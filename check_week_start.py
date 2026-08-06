"""检查 week_start 匹配问题"""
import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

def get_app_data_dir() -> Path:
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home()))
        app_dir = base / 'AnimalNumberLedger'
    elif sys.platform == 'darwin':
        app_dir = Path.home() / 'Library' / 'Application Support' / 'AnimalNumberLedger'
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        app_dir = base / 'AnimalNumberLedger'
    return app_dir

real_db_path = get_app_data_dir() / 'ledger.db'

print("="*70)
print("检查 week_start 匹配问题")
print("="*70)

conn = sqlite3.connect(str(real_db_path))
cursor = conn.cursor()

# 查看所有 week_start 值
cursor.execute("SELECT DISTINCT week_start, COUNT(*) FROM input_history GROUP BY week_start ORDER BY week_start DESC")
print("\n数据库中的 week_start 值:")
for row in cursor.fetchall():
    print(f"  '{row[0]}' : {row[1]} 条记录")

# 计算当前周起始日期（与 HistoryWindow 逻辑一致）
today = datetime.now().date()
week_start = today - timedelta(days=today.weekday())
week_start_str = week_start.strftime('%Y-%m-%d')

print(f"\n历史窗口计算的 week_start:")
print(f"  今天: {today}")
print(f"  weekday: {today.weekday()} (0=周一)")
print(f"  week_start: {week_start}")
print(f"  week_start_str: '{week_start_str}'")

# 测试查询
print(f"\n测试查询 1：不带 play_mode 过滤")
cursor.execute("""
    SELECT COUNT(*)
    FROM input_history
    WHERE week_start = ?
""", (week_start_str,))
count1 = cursor.fetchone()[0]
print(f"  结果: {count1} 条")

print(f"\n测试查询 2：play_mode = 'number'")
cursor.execute("""
    SELECT COUNT(*)
    FROM input_history
    WHERE week_start = ? AND play_mode = 'number'
""", (week_start_str,))
count2 = cursor.fetchone()[0]
print(f"  结果: {count2} 条")

print(f"\n测试查询 3：play_mode = 'flat_zodiac'")
cursor.execute("""
    SELECT COUNT(*)
    FROM input_history
    WHERE week_start = ? AND play_mode = 'flat_zodiac'
""", (week_start_str,))
count3 = cursor.fetchone()[0]
print(f"  结果: {count3} 条")

print(f"\n测试查询 4：不带 week_start，只按 ledger_id=10")
cursor.execute("""
    SELECT COUNT(*)
    FROM input_history
    WHERE ledger_id = 10
""")
count4 = cursor.fetchone()[0]
print(f"  结果: {count4} 条")

print(f"\n测试查询 5：不带任何条件")
cursor.execute("SELECT COUNT(*) FROM input_history")
count5 = cursor.fetchone()[0]
print(f"  结果: {count5} 条")

conn.close()

print("\n" + "="*70)
print("结论:")
if count1 == 0:
    print("  week_start 不匹配，所有记录被过滤掉")
else:
    print(f"  week_start 匹配正常，找到 {count1} 条记录")
