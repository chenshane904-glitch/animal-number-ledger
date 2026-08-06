"""
v1.22 回归测试报告
生成时间：{datetime}
"""

from datetime import datetime
import sys
import os
from pathlib import Path

print("="*70)
print("v1.22 最终回归测试")
print("="*70)
print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 检查数据库路径
def get_app_data_dir():
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home()))
        return base / 'AnimalNumberLedger'
    elif sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'AnimalNumberLedger'
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        return base / 'AnimalNumberLedger'

db_dir = get_app_data_dir()
db_path = db_dir / 'ledger.db'

print(f"\n数据库路径: {db_path}")
print(f"数据库存在: {db_path.exists()}")

if db_path.exists():
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    print("\n检查数据库表结构:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    required_tables = [
        'allocations',
        'batches',
        'instructions',
        'input_history',
        'flat_zodiac_batches',
        'flat_zodiac_items'
    ]

    for table in required_tables:
        exists = table in tables
        status = "[PASS]" if exists else "[FAIL]"
        print(f"  {table}: {status}")

    # 统计记录数
    print("\n数据库记录数:")
    for table in required_tables:
        if table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条")

    conn.close()

print("\n" + "="*70)
print("请手动完成以下功能测试，并报告结果")
print("="*70)

print("\n【号码模式测试】")
print("1. 输入: 02各20")
print("2. 点击确认追加")
print("3. 检查右侧显示")
print("4. 打开历史记录")
print("5. 检查历史显示")
print("6. 关闭并重启软件")
print("7. 检查数据是否保留")

print("\n【平特一肖模式测试】")
print("1. 切换到平特一肖模式")
print("2. 输入: 虎100")
print("3. 点击确认追加")
print("4. 检查顶部统计")
print("5. 检查右侧12生肖表")
print("6. 打开历史记录")
print("7. 检查历史显示")

print("\n【模式隔离测试】")
print("1. 号码模式历史不显示平特记录")
print("2. 平特模式历史不显示号码记录")
print("3. 切换模式后数据不混合")

print("\n" + "="*70)
