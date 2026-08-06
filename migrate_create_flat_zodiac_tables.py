# -*- coding: utf-8 -*-
"""
数据库迁移：创建平特一肖独立表
"""

import sqlite3
import os

def create_flat_zodiac_tables():
    """创建平特一肖独立表"""
    db_path = 'data.db'

    if not os.path.exists(db_path):
        print(f"[ERROR] 数据库不存在: {db_path}")
        return False

    db_path = os.path.abspath(db_path)
    print(f"数据库路径: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 创建 flat_zodiac_batches 表
        print("[1] 创建 flat_zodiac_batches 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flat_zodiac_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ledger_id INTEGER NOT NULL,
                raw_input TEXT NOT NULL,
                entry_total INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ledger_id) REFERENCES ledgers(id) ON DELETE CASCADE
            )
        """)
        print("  [OK] flat_zodiac_batches 表创建成功")

        # 创建 flat_zodiac_items 表
        print("[2] 创建 flat_zodiac_items 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flat_zodiac_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                zodiac TEXT NOT NULL CHECK(zodiac IN ('鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪')),
                amount INTEGER NOT NULL,
                odds REAL NOT NULL DEFAULT 1.0,
                payout INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES flat_zodiac_batches(id) ON DELETE CASCADE
            )
        """)
        print("  [OK] flat_zodiac_items 表创建成功")

        # 创建索引
        print("[3] 创建索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flat_zodiac_batches_ledger
            ON flat_zodiac_batches(ledger_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flat_zodiac_batches_status
            ON flat_zodiac_batches(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flat_zodiac_items_batch
            ON flat_zodiac_items(batch_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flat_zodiac_items_zodiac
            ON flat_zodiac_items(zodiac)
        """)
        print("  [OK] 索引创建成功")

        conn.commit()
        print("\n[SUCCESS] 平特一肖独立表创建完成")

        # 验证
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'flat_zodiac%'")
        tables = cursor.fetchall()
        print(f"\n创建的表: {[t[0] for t in tables]}")

        return True

    except Exception as e:
        print(f"\n[ERROR] 创建表失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    create_flat_zodiac_tables()
