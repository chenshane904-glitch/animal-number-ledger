import sqlite3

db_path = "data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 添加input_history表 ===")

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS input_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ledger_id INTEGER NOT NULL,
            batch_id INTEGER,
            record_date TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            raw_input TEXT NOT NULL,
            parsed_summary TEXT NOT NULL,
            expanded_items_json TEXT NOT NULL,
            entry_total INTEGER NOT NULL,
            daily_total_after INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            week_start TEXT NOT NULL,
            FOREIGN KEY (ledger_id) REFERENCES ledgers(id) ON DELETE CASCADE,
            FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE SET NULL
        )
    """)
    
    conn.commit()
    print("[OK] input_history表创建成功")
    
    # 验证
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='input_history'")
    if cursor.fetchone():
        print("[OK] 验证：表已存在")
    else:
        print("[ERROR] 验证失败")
        
except Exception as e:
    print(f"[ERROR] 创建表失败: {e}")
    conn.rollback()

conn.close()
