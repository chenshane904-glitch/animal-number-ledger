"""诊断数据库问题"""
import sqlite3
import os
from pathlib import Path

print("="*60)
print("第一步：确认数据库路径")
print("="*60)

# 查找所有可能的数据库文件
possible_dbs = [
    'data.db',
    'ledger.db',
    Path.home() / 'AppData' / 'Local' / 'animal-number-ledger' / 'data.db',
    Path.home() / 'AppData' / 'Local' / 'animal-number-ledger' / 'ledger.db',
]

for db_path in possible_dbs:
    db_path_str = str(db_path)
    if os.path.exists(db_path_str):
        abs_path = os.path.abspath(db_path_str)
        size = os.path.getsize(db_path_str)
        print(f"找到数据库: {abs_path}")
        print(f"  文件大小: {size} bytes")
    else:
        print(f"不存在: {db_path_str}")

print("\n" + "="*60)
print("第二步：检查程序实际使用的数据库")
print("="*60)

# 读取 main.py 看数据库路径
try:
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'Database(' in content:
            # 提取Database()调用
            import re
            matches = re.findall(r'Database\([\'"]([^\'"]+)[\'"]', content)
            if matches:
                print(f"main.py 中的数据库路径: {matches}")
except Exception as e:
    print(f"无法读取 main.py: {e}")

print("\n" + "="*60)
print("第三步：PRAGMA table_info(batches)")
print("="*60)

db_path = 'data.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"连接数据库: {os.path.abspath(db_path)}")
    print("\n表结构:")
    cursor.execute("PRAGMA table_info(batches)")
    columns = cursor.fetchall()

    if not columns:
        print("ERROR: batches 表不存在")
    else:
        print(f"{'cid':<5} {'name':<20} {'type':<15} {'notnull':<10} {'dflt_value':<15} {'pk':<5}")
        print("-" * 75)
        for col in columns:
            print(f"{col[0]:<5} {col[1]:<20} {col[2]:<15} {col[3]:<10} {str(col[4]):<15} {col[5]:<5}")

        # 检查是否有 play_mode 字段
        column_names = [col[1] for col in columns]
        print(f"\n所有字段: {column_names}")

        if 'play_mode' in column_names:
            print("\n✓ play_mode 字段存在")
        else:
            print("\n✗ play_mode 字段不存在")

    conn.close()
else:
    print(f"ERROR: 数据库文件不存在: {db_path}")

print("\n" + "="*60)
print("第四步：测试 INSERT 语句")
print("="*60)

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 尝试执行 INSERT
    test_sql = """
        INSERT INTO batches
        (ledger_id, raw_input, total_before, total_after, mapping_snapshot, play_mode)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    print(f"测试 SQL:")
    print(test_sql)
    print(f"\n参数: (1, 'test', 0, 100, '{{}}', 'flat_zodiac')")

    try:
        cursor.execute(test_sql, (1, 'test', 0, 100, '{}', 'flat_zodiac'))
        print("\n✓ INSERT 执行成功")
        cursor.execute("SELECT last_insert_rowid()")
        batch_id = cursor.fetchone()[0]
        print(f"  插入的 batch_id: {batch_id}")

        # 回滚测试数据
        conn.rollback()
        print("  (测试数据已回滚)")
    except Exception as e:
        print(f"\n✗ INSERT 执行失败:")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {e}")

    conn.close()

print("\n" + "="*60)
print("诊断完成")
print("="*60)
