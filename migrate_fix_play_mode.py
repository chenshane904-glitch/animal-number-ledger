# -*- coding: utf-8 -*-
"""
数据库迁移：添加 play_mode 字段（修正版）
"""

import sqlite3
import os

def migrate_add_play_mode():
    """添加 play_mode 字段到相关表"""
    # 使用当前目录的 data.db
    db_path = 'data.db'

    if not os.path.exists(db_path):
        print(f"[ERROR] 数据库不存在: {db_path}")
        return False

    db_path = os.path.abspath(db_path)
    print(f"数据库路径: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查 input_history 表是否已有 play_mode 字段
        cursor.execute("PRAGMA table_info(input_history)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'play_mode' not in columns:
            print("[1] 添加 play_mode 字段到 input_history 表...")
            cursor.execute("""
                ALTER TABLE input_history
                ADD COLUMN play_mode TEXT NOT NULL DEFAULT 'number'
            """)
            print("  [OK] 字段添加成功")
        else:
            print("[1] play_mode 字段已存在于 input_history 表")

        # 检查 batches 表是否已有 play_mode 字段
        cursor.execute("PRAGMA table_info(batches)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'play_mode' not in columns:
            print("[2] 添加 play_mode 字段到 batches 表...")
            cursor.execute("""
                ALTER TABLE batches
                ADD COLUMN play_mode TEXT NOT NULL DEFAULT 'number'
            """)
            print("  [OK] 字段添加成功")
        else:
            print("[2] play_mode 字段已存在于 batches 表")

        conn.commit()
        print("\n[SUCCESS] 数据库迁移完成")

        # 验证
        print("\n验证迁移结果:")
        cursor.execute("PRAGMA table_info(batches)")
        columns = cursor.fetchall()
        print("batches 表字段:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

        return True

    except Exception as e:
        print(f"\n[ERROR] 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_add_play_mode()
