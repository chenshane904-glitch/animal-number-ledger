# -*- coding: utf-8 -*-
"""
验证历史记录数据库读取
"""

import sqlite3
from datetime import datetime, timedelta

db_path = "data.db"

def check_history_records():
    """检查历史记录"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 60)
    print("历史记录数据库验证")
    print("=" * 60)

    # 1. 检查表是否存在
    print("\n[1] 检查input_history表")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='input_history'")
    if cursor.fetchone():
        print("  ✓ 表存在")
    else:
        print("  ✗ 表不存在")
        conn.close()
        return

    # 2. 检查总记录数
    print("\n[2] 检查记录总数")
    cursor.execute("SELECT COUNT(*) as count FROM input_history")
    total = cursor.fetchone()['count']
    print(f"  总记录数: {total}")

    if total == 0:
        print("  提示: 数据库中暂无记录，请先在澳门版中输入数据")
        conn.close()
        return

    # 3. 按日期分组统计
    print("\n[3] 按日期分组统计")
    cursor.execute("""
        SELECT record_date, COUNT(*) as count, SUM(entry_total) as total
        FROM input_history
        GROUP BY record_date
        ORDER BY record_date DESC
    """)
    for row in cursor.fetchall():
        date = row['record_date']
        count = row['count']
        total = row['total'] / 100.0
        print(f"  {date}: {count}条记录, 总金额 {total:.2f}")

    # 4. 计算当前周
    print("\n[4] 当前周记录")
    today = datetime.now()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_start_str = week_start.strftime('%Y-%m-%d')

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM input_history
        WHERE week_start = ?
    """, (week_start_str,))
    week_count = cursor.fetchone()['count']
    print(f"  周起始日期: {week_start_str}")
    print(f"  本周记录数: {week_count}")

    # 5. 显示最近5条记录
    print("\n[5] 最近5条记录详情")
    cursor.execute("""
        SELECT id, record_date, created_at, raw_input, entry_total,
               daily_total_after, status, batch_id
        FROM input_history
        ORDER BY created_at DESC
        LIMIT 5
    """)

    records = cursor.fetchall()
    if records:
        for i, row in enumerate(records, 1):
            print(f"\n  记录 {i}:")
            print(f"    ID: {row['id']}")
            print(f"    日期: {row['record_date']}")
            print(f"    时间: {row['created_at']}")
            print(f"    输入: {row['raw_input']}")
            print(f"    本次金额: {row['entry_total'] / 100.0:.2f}")
            print(f"    今日累计: {row['daily_total_after'] / 100.0:.2f}")
            print(f"    状态: {row['status']}")
            print(f"    关联批次: {row['batch_id']}")

    # 6. 检查已撤销记录
    print("\n[6] 已撤销记录")
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM input_history
        WHERE status = 'undone'
    """)
    undone_count = cursor.fetchone()['count']
    print(f"  已撤销记录数: {undone_count}")

    # 7. 显示数据库读取SQL
    print("\n[7] 历史记录查询SQL")
    print("  按周查询:")
    print("    SELECT id, ledger_id, batch_id, record_date, created_at,")
    print("           raw_input, parsed_summary, expanded_items_json,")
    print("           entry_total, daily_total_after, status")
    print("    FROM input_history")
    print("    WHERE week_start = ?")
    print("    ORDER BY record_date DESC, created_at DESC")

    print("\n  获取最新有效记录:")
    print("    SELECT * FROM input_history")
    print("    WHERE ledger_id = ? AND status = 'active'")
    print("    ORDER BY created_at DESC")
    print("    LIMIT 1")

    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)

    conn.close()

if __name__ == "__main__":
    try:
        check_history_records()
    except Exception as e:
        print(f"\n[ERROR] 验证失败: {e}")
        import traceback
        traceback.print_exc()
