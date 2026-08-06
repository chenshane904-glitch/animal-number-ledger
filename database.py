"""数据库操作模块"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from constants import (
    DEFAULT_ANIMAL_MAPPING, MIN_NUMBER, MAX_NUMBER, DB_VERSION,
    TOTAL_ANIMALS, ANIMAL_WITH_5_NUMBERS, ANIMAL_WITH_4_NUMBERS
)
from models import Ledger, Batch, Instruction, Allocation


def _convert_timestamp(raw_value: bytes) -> datetime:
    """显式解析SQLite时间戳，避免依赖Python已弃用的默认转换器。"""
    return datetime.fromisoformat(raw_value.decode('utf-8'))


sqlite3.register_converter("TIMESTAMP", _convert_timestamp)


class DatabaseError(Exception):
    """数据库错误"""
    pass


class Database:
    """数据库操作类"""

    def __init__(self, db_path: str):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._init_db()

    def _connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self.conn.row_factory = sqlite3.Row
            # 启用外键约束
            self.conn.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            raise DatabaseError(f"无法连接数据库: {e}")

    def _init_db(self):
        """初始化数据库结构"""
        try:
            cursor = self.conn.cursor()

            # settings表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # ledgers表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ledgers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ledger_date TEXT NOT NULL,
                    sequence_number INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    archived_at TIMESTAMP,
                    settled_total_integer INTEGER,
                    UNIQUE(ledger_date, sequence_number)
                )
            """)

            # 兼容v1.0数据库：为已存在的ledgers表补充结算金额字段。
            cursor.execute("PRAGMA table_info(ledgers)")
            ledger_columns = {row[1] for row in cursor.fetchall()}
            if 'settled_total_integer' not in ledger_columns:
                cursor.execute(
                    "ALTER TABLE ledgers ADD COLUMN settled_total_integer INTEGER"
                )

            # batches表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ledger_id INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    raw_input TEXT NOT NULL,
                    total_before INTEGER NOT NULL,
                    total_after INTEGER NOT NULL,
                    mapping_snapshot TEXT NOT NULL,
                    FOREIGN KEY (ledger_id) REFERENCES ledgers(id) ON DELETE CASCADE
                )
            """)

            # instructions表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS instructions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id INTEGER NOT NULL,
                    source_line INTEGER NOT NULL,
                    original_text TEXT NOT NULL,
                    normalized_text TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    targets TEXT NOT NULL,
                    amount_integer INTEGER NOT NULL,
                    warning TEXT,
                    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
                )
            """)

            # allocations表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS allocations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instruction_id INTEGER NOT NULL,
                    number INTEGER NOT NULL,
                    animal TEXT NOT NULL,
                    amount_integer INTEGER NOT NULL,
                    FOREIGN KEY (instruction_id) REFERENCES instructions(id) ON DELETE CASCADE
                )
            """)

            # settlements表 - 每日开奖结算记录
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settlements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ledger_id INTEGER NOT NULL,
                    settlement_date TEXT NOT NULL,
                    winning_number INTEGER NOT NULL,
                    winning_amount INTEGER NOT NULL,
                    odds INTEGER NOT NULL,
                    payout_amount INTEGER NOT NULL,
                    total_bet INTEGER NOT NULL,
                    profit_loss INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ledger_id) REFERENCES ledgers(id) ON DELETE CASCADE,
                    UNIQUE(ledger_id, settlement_date)
                )
            """)

            # input_history表 - 输入历史记录
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

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ledgers_date
                ON ledgers(ledger_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_batches_ledger
                ON batches(ledger_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_instructions_batch
                ON instructions(batch_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_allocations_instruction
                ON allocations(instruction_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_settlements_ledger
                ON settlements(ledger_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_settlements_date
                ON settlements(settlement_date)
            """)

            # 平特一肖独立表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flat_zodiac_batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ledger_id INTEGER NOT NULL,
                    raw_input TEXT NOT NULL,
                    entry_total REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'undone')),
                    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                    FOREIGN KEY (ledger_id) REFERENCES ledgers(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flat_zodiac_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id INTEGER NOT NULL,
                    zodiac TEXT NOT NULL CHECK(zodiac IN ('鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪')),
                    amount REAL NOT NULL DEFAULT 0,
                    odds REAL NOT NULL DEFAULT 1.0,
                    payout REAL NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                    FOREIGN KEY (batch_id) REFERENCES flat_zodiac_batches(id) ON DELETE CASCADE
                )
            """)

            # 平特一肖索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_flat_zodiac_batches_ledger_status
                ON flat_zodiac_batches(ledger_id, status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_flat_zodiac_batches_created
                ON flat_zodiac_batches(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_flat_zodiac_items_batch
                ON flat_zodiac_items(batch_id)
            """)

            # v1.0已归档账本没有结算字段，升级时按现有明细补算一次。
            cursor.execute("""
                UPDATE ledgers
                SET settled_total_integer = (
                    SELECT COALESCE(SUM(a.amount_integer), 0)
                    FROM allocations a
                    JOIN instructions i ON a.instruction_id = i.id
                    JOIN batches b ON i.batch_id = b.id
                    WHERE b.ledger_id = ledgers.id
                )
                WHERE status = 'archived' AND settled_total_integer IS NULL
            """)

            self.conn.commit()

            # 初始化设置
            self._init_settings()

        except sqlite3.Error as e:
            raise DatabaseError(f"初始化数据库失败: {e}")

    def _init_settings(self):
        """初始化设置"""
        cursor = self.conn.cursor()

        # 检查是否已有设置
        cursor.execute("SELECT value FROM settings WHERE key = 'db_version'")
        if cursor.fetchone() is None:
            # 首次初始化
            cursor.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                ('db_version', str(DB_VERSION))
            )
            cursor.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                ('animal_mapping', json.dumps(DEFAULT_ANIMAL_MAPPING, ensure_ascii=False))
            )
            self.conn.commit()

    def get_animal_mapping(self) -> dict:
        """获取当前动物号码映射"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'animal_mapping'")
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return DEFAULT_ANIMAL_MAPPING.copy()

    def validate_animal_mapping(self, mapping: dict) -> Tuple[bool, Optional[str]]:
        """
        验证动物号码映射

        Returns:
            (是否有效, 错误信息)
        """
        # 1. 必须有12个动物
        if len(mapping) != TOTAL_ANIMALS:
            return False, f"必须有{TOTAL_ANIMALS}个动物，当前有{len(mapping)}个"

        # 收集所有号码
        all_numbers = []
        for animal, numbers in mapping.items():
            if not isinstance(numbers, list):
                return False, f"动物'{animal}'的号码必须是列表"
            all_numbers.extend(numbers)

        # 2. 号码只能是1-49
        for num in all_numbers:
            if not isinstance(num, int) or num < MIN_NUMBER or num > MAX_NUMBER:
                return False, f"号码必须是{MIN_NUMBER}到{MAX_NUMBER}之间的整数，发现无效号码: {num}"

        # 3. 1-49必须全部出现
        all_numbers_set = set(all_numbers)
        expected = set(range(MIN_NUMBER, MAX_NUMBER + 1))
        if all_numbers_set != expected:
            missing = expected - all_numbers_set
            extra = all_numbers_set - expected
            if missing:
                return False, f"缺少号码: {sorted(missing)}"
            if extra:
                return False, f"多余号码: {sorted(extra)}"

        # 4. 每个号码只能出现一次
        if len(all_numbers) != len(all_numbers_set):
            duplicates = []
            seen = set()
            for num in all_numbers:
                if num in seen:
                    duplicates.append(num)
                seen.add(num)
            return False, f"重复号码: {sorted(set(duplicates))}"

        # 5. 正好一个动物有5个号码
        count_5 = sum(1 for numbers in mapping.values() if len(numbers) == 5)
        if count_5 != ANIMAL_WITH_5_NUMBERS:
            return False, f"必须有{ANIMAL_WITH_5_NUMBERS}个动物有5个号码，当前有{count_5}个"

        # 6. 另外11个动物各有4个号码
        count_4 = sum(1 for numbers in mapping.values() if len(numbers) == 4)
        if count_4 != ANIMAL_WITH_4_NUMBERS:
            return False, f"必须有{ANIMAL_WITH_4_NUMBERS}个动物有4个号码，当前有{count_4}个"

        return True, None

    def update_animal_mapping(self, mapping: dict):
        """更新动物号码映射"""
        # 验证
        valid, error = self.validate_animal_mapping(mapping)
        if not valid:
            raise DatabaseError(f"动物映射验证失败: {error}")

        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE settings SET value = ? WHERE key = 'animal_mapping'",
            (json.dumps(mapping, ensure_ascii=False),)
        )
        self.conn.commit()

    def get_or_create_active_ledger(self, date: str) -> Ledger:
        """
        获取或创建指定日期的活动账本

        Args:
            date: 日期字符串 YYYY-MM-DD

        Returns:
            账本对象
        """
        cursor = self.conn.cursor()

        # 查找活动账本
        cursor.execute("""
            SELECT id, ledger_date, sequence_number, status, created_at,
                   archived_at, settled_total_integer
            FROM ledgers
            WHERE ledger_date = ? AND status = 'active'
            ORDER BY sequence_number DESC
            LIMIT 1
        """, (date,))

        row = cursor.fetchone()
        if row:
            return Ledger(
                id=row['id'],
                ledger_date=row['ledger_date'],
                sequence_number=row['sequence_number'],
                status=row['status'],
                created_at=row['created_at'],
                archived_at=row['archived_at'],
                settled_total_integer=row['settled_total_integer']
            )

        # 创建新账本
        cursor.execute("""
            SELECT COALESCE(MAX(sequence_number), 0) + 1
            FROM ledgers
            WHERE ledger_date = ?
        """, (date,))
        next_seq = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO ledgers (ledger_date, sequence_number, status)
            VALUES (?, ?, 'active')
        """, (date, next_seq))

        ledger_id = cursor.lastrowid
        self.conn.commit()

        return Ledger(
            id=ledger_id,
            ledger_date=date,
            sequence_number=next_seq,
            status='active',
            created_at=datetime.now()
        )

    def add_batch(self, ledger_id: int, batch: Batch) -> int:
        """
        添加批次

        Args:
            ledger_id: 账本ID
            batch: 批次对象

        Returns:
            批次ID
        """
        cursor = self.conn.cursor()

        try:
            # 插入批次
            cursor.execute("""
                INSERT INTO batches (ledger_id, raw_input, total_before, total_after, mapping_snapshot)
                VALUES (?, ?, ?, ?, ?)
            """, (
                ledger_id,
                batch.raw_input,
                batch.total_before,
                batch.total_after,
                batch.mapping_snapshot
            ))
            batch_id = cursor.lastrowid

            # 插入指令
            for instruction in batch.instructions:
                cursor.execute("""
                    INSERT INTO instructions
                    (batch_id, source_line, original_text, normalized_text, target_type, targets, amount_integer, warning)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    batch_id,
                    instruction.source_line,
                    instruction.original_text,
                    instruction.normalized_text,
                    instruction.target_type,
                    json.dumps(instruction.targets, ensure_ascii=False),
                    instruction.amount_integer,
                    instruction.warning
                ))
                instruction_id = cursor.lastrowid

                # 插入分配（从calculator计算结果中获取）
                # 这里需要额外的allocations参数或从instruction重新计算
                # 为了简化，我们在add_batch时传入完整的allocations

            self.conn.commit()
            return batch_id

        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"添加批次失败: {e}")

    def add_batch_with_allocations(self, ledger_id: int, batch: Batch,
                                   animal_mapping: dict) -> int:
        """在同一个事务中保存批次、指令及全部号码分配。"""
        from calculator import Calculator

        cursor = self.conn.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("""
                INSERT INTO batches
                (ledger_id, raw_input, total_before, total_after, mapping_snapshot)
                VALUES (?, ?, ?, ?, ?)
            """, (
                ledger_id,
                batch.raw_input,
                batch.total_before,
                batch.total_after,
                batch.mapping_snapshot
            ))
            batch_id = cursor.lastrowid

            for instruction in batch.instructions:
                cursor.execute("""
                    INSERT INTO instructions
                    (batch_id, source_line, original_text, normalized_text,
                     target_type, targets, amount_integer, warning)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    batch_id,
                    instruction.source_line,
                    instruction.original_text,
                    instruction.normalized_text,
                    instruction.target_type,
                    json.dumps(instruction.targets, ensure_ascii=False),
                    instruction.amount_integer,
                    instruction.warning
                ))
                instruction.id = cursor.lastrowid
                instruction.batch_id = batch_id

            calculator = Calculator(animal_mapping)
            result = calculator.calculate(batch.instructions)
            for allocation in result.allocations:
                cursor.execute("""
                    INSERT INTO allocations
                    (instruction_id, number, animal, amount_integer)
                    VALUES (?, ?, ?, ?)
                """, (
                    allocation.instruction_id,
                    allocation.number,
                    allocation.animal,
                    allocation.amount_integer
                ))

            self.conn.commit()
            return batch_id
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"原子追加批次失败: {e}") from e

    def add_allocations(self, allocations: List[Allocation]):
        """添加分配记录"""
        cursor = self.conn.cursor()
        try:
            for allocation in allocations:
                cursor.execute("""
                    INSERT INTO allocations (instruction_id, number, animal, amount_integer)
                    VALUES (?, ?, ?, ?)
                """, (
                    allocation.instruction_id,
                    allocation.number,
                    allocation.animal,
                    allocation.amount_integer
                ))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"添加分配记录失败: {e}")

    def get_ledger_totals(self, ledger_id: int) -> Dict[int, int]:
        """
        获取账本的当前累计金额

        Returns:
            {号码: 金额整数}
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.number, SUM(a.amount_integer) as total
            FROM allocations a
            JOIN instructions i ON a.instruction_id = i.id
            JOIN batches b ON i.batch_id = b.id
            WHERE b.ledger_id = ?
            GROUP BY a.number
        """, (ledger_id,))

        totals = {i: 0 for i in range(MIN_NUMBER, MAX_NUMBER + 1)}
        for row in cursor.fetchall():
            totals[row['number']] = row['total']

        return totals

    def get_ledger_sources(self, ledger_id: int) -> Dict[int, List[str]]:
        """
        获取账本中每个号码的来源

        Returns:
            {号码: [来源文本列表]}
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.number, i.original_text
            FROM allocations a
            JOIN instructions i ON a.instruction_id = i.id
            JOIN batches b ON i.batch_id = b.id
            WHERE b.ledger_id = ?
            ORDER BY b.created_at, i.source_line
        """, (ledger_id,))

        sources = {i: [] for i in range(MIN_NUMBER, MAX_NUMBER + 1)}
        for row in cursor.fetchall():
            sources[row['number']].append(row['original_text'])

        return sources

    def get_ledger_totals_by_mode(self, ledger_id: int, play_mode: str) -> Dict:
        """
        统一查询接口：根据玩法模式返回对应维度的累计

        Args:
            ledger_id: 账本ID
            play_mode: 玩法模式 ('number', 'flat_zodiac', 'wave', 'tail', 等)

        Returns:
            号码模式: {号码(int): 金额整数}
            生肖模式: {生肖(str): 金额整数}
            其他模式: {目标(str): 金额整数}
        """
        cursor = self.conn.cursor()

        if play_mode == 'number':
            # 号码模式：从 allocations 查询
            cursor.execute("""
                SELECT a.number, SUM(a.amount_integer) as total
                FROM allocations a
                JOIN instructions i ON a.instruction_id = i.id
                JOIN batches b ON i.batch_id = b.id
                WHERE b.ledger_id = ?
                GROUP BY a.number
            """, (ledger_id,))

            totals = {i: 0 for i in range(MIN_NUMBER, MAX_NUMBER + 1)}
            for row in cursor.fetchall():
                totals[row['number']] = row['total']

            return totals
        else:
            # 生肖模式（平特一肖、波色、尾数等）：从 instructions 查询
            cursor.execute("""
                SELECT i.targets, i.amount_integer
                FROM instructions i
                JOIN batches b ON i.batch_id = b.id
                WHERE b.ledger_id = ? AND b.play_mode = ?
                ORDER BY b.created_at, i.source_line
            """, (ledger_id, play_mode))

            totals = {}
            for row in cursor.fetchall():
                # targets 是 JSON 数组字符串，如 '["虎"]'
                import json
                targets = json.loads(row['targets'])
                amount = row['amount_integer']

                # 累加到每个目标
                for target in targets:
                    if target not in totals:
                        totals[target] = 0
                    totals[target] += amount

            return totals

    def _calculate_ledger_total(self, cursor, ledger_id: int) -> int:
        """使用指定游标计算账本总金额。"""
        cursor.execute("""
            SELECT COALESCE(SUM(a.amount_integer), 0)
            FROM allocations a
            JOIN instructions i ON a.instruction_id = i.id
            JOIN batches b ON i.batch_id = b.id
            WHERE b.ledger_id = ?
        """, (ledger_id,))
        return int(cursor.fetchone()[0])

    def archive_ledger(self, ledger_id: int) -> int:
        """归档并固化结算总金额，返回结算金额整数。"""
        cursor = self.conn.cursor()
        try:
            total = self._calculate_ledger_total(cursor, ledger_id)
            cursor.execute("""
                UPDATE ledgers
                SET status = 'archived',
                    archived_at = CURRENT_TIMESTAMP,
                    settled_total_integer = ?
                WHERE id = ?
            """, (total, ledger_id))
            if cursor.rowcount != 1:
                raise DatabaseError(f"账本不存在: {ledger_id}")
            self.conn.commit()
            return total
        except Exception as e:
            self.conn.rollback()
            if isinstance(e, DatabaseError):
                raise
            raise DatabaseError(f"归档账本失败: {e}") from e

    def archive_stale_active_ledgers(self, current_date: str) -> List[Tuple[int, str, int]]:
        """归档所有非当前日期的活动账本，并返回结算结果。"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, ledger_date
                FROM ledgers
                WHERE status = 'active' AND ledger_date <> ?
                ORDER BY ledger_date, sequence_number
            """, (current_date,))
            stale_ledgers = cursor.fetchall()
            settlements = []

            for row in stale_ledgers:
                total = self._calculate_ledger_total(cursor, row['id'])
                cursor.execute("""
                    UPDATE ledgers
                    SET status = 'archived',
                        archived_at = CURRENT_TIMESTAMP,
                        settled_total_integer = ?
                    WHERE id = ?
                """, (total, row['id']))
                settlements.append((row['id'], row['ledger_date'], total))

            self.conn.commit()
            return settlements
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"跨日结算失败: {e}") from e

    def get_last_batch_id(self, ledger_id: int) -> Optional[int]:
        """获取账本的最后一个批次ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id FROM batches
            WHERE ledger_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """, (ledger_id,))
        row = cursor.fetchone()
        return row['id'] if row else None

    def delete_batch(self, batch_id: int):
        """删除批次（级联删除关联的instructions和allocations）"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM batches WHERE id = ?", (batch_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"删除批次失败: {e}")

    def get_all_ledgers(self) -> List[Ledger]:
        """获取所有账本"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, ledger_date, sequence_number, status, created_at,
                   archived_at, settled_total_integer
            FROM ledgers
            ORDER BY ledger_date DESC, sequence_number DESC
        """)

        ledgers = []
        for row in cursor.fetchall():
            ledgers.append(Ledger(
                id=row['id'],
                ledger_date=row['ledger_date'],
                sequence_number=row['sequence_number'],
                status=row['status'],
                created_at=row['created_at'],
                archived_at=row['archived_at'],
                settled_total_integer=row['settled_total_integer']
            ))

        return ledgers

    def get_ledger(self, ledger_id: int) -> Optional[Ledger]:
        """按ID获取账本。"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, ledger_date, sequence_number, status, created_at,
                   archived_at, settled_total_integer
            FROM ledgers
            WHERE id = ?
        """, (ledger_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Ledger(
            id=row['id'],
            ledger_date=row['ledger_date'],
            sequence_number=row['sequence_number'],
            status=row['status'],
            created_at=row['created_at'],
            archived_at=row['archived_at'],
            settled_total_integer=row['settled_total_integer']
        )

    def delete_ledgers(self, ledger_ids: List[int]):
        """永久删除账本（级联删除所有关联数据）"""
        cursor = self.conn.cursor()
        try:
            placeholders = ','.join('?' * len(ledger_ids))
            cursor.execute(f"""
                DELETE FROM ledgers
                WHERE id IN ({placeholders})
            """, ledger_ids)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"删除账本失败: {e}")

    def delete_all_archived_ledgers(self):
        """删除所有已归档的账本"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM ledgers WHERE status = 'archived'")
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"删除全部历史记录失败: {e}")

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    # ==================== 结算相关方法 ====================

    def save_settlement(self, ledger_id: int, settlement_date: str, winning_number: int,
                       winning_amount: int, odds: int, payout_amount: int,
                       total_bet: int, profit_loss: int) -> int:
        """
        保存结算记录

        Args:
            ledger_id: 账本ID
            settlement_date: 结算日期
            winning_number: 中奖号码
            winning_amount: 中奖金额（分）
            odds: 赔率
            payout_amount: 应赔金额（分）
            total_bet: 总下注（分）
            profit_loss: 盈亏（分）

        Returns:
            结算记录ID
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO settlements (
                    ledger_id, settlement_date, winning_number, winning_amount,
                    odds, payout_amount, total_bet, profit_loss
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ledger_id, settlement_date, winning_number, winning_amount,
                  odds, payout_amount, total_bet, profit_loss))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"保存结算记录失败: {e}")

    def get_settlement_by_date(self, settlement_date: str):
        """
        获取指定日期的结算记录

        Args:
            settlement_date: 结算日期

        Returns:
            结算记录字典，如果不存在返回None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, ledger_id, settlement_date, winning_number, winning_amount,
                   odds, payout_amount, total_bet, profit_loss, created_at
            FROM settlements
            WHERE settlement_date = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (settlement_date,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            'id': row['id'],
            'ledger_id': row['ledger_id'],
            'settlement_date': row['settlement_date'],
            'winning_number': row['winning_number'],
            'winning_amount': row['winning_amount'],
            'odds': row['odds'],
            'payout_amount': row['payout_amount'],
            'total_bet': row['total_bet'],
            'profit_loss': row['profit_loss'],
            'created_at': row['created_at']
        }

    def get_settlement_history(self, limit: int = 30):
        """
        获取结算历史记录

        Args:
            limit: 返回记录数量限制

        Returns:
            结算记录列表
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, ledger_id, settlement_date, winning_number, winning_amount,
                   odds, payout_amount, total_bet, profit_loss, created_at
            FROM settlements
            ORDER BY settlement_date DESC, created_at DESC
            LIMIT ?
        """, (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'ledger_id': row['ledger_id'],
                'settlement_date': row['settlement_date'],
                'winning_number': row['winning_number'],
                'winning_amount': row['winning_amount'],
                'odds': row['odds'],
                'payout_amount': row['payout_amount'],
                'total_bet': row['total_bet'],
                'profit_loss': row['profit_loss'],
                'created_at': row['created_at']
            })
        return results

    def save_input_history(self, ledger_id: int, batch_id: Optional[int], record_date: str,
                          raw_input: str, parsed_summary: str, expanded_items: List[Dict],
                          entry_total: int, daily_total_after: int, week_start: str, play_mode: str = 'number'):
        """保存输入历史记录"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO input_history (
                    ledger_id, batch_id, record_date, raw_input, parsed_summary,
                    expanded_items_json, entry_total, daily_total_after, status, week_start, play_mode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
            """, (
                ledger_id, batch_id, record_date, raw_input, parsed_summary,
                json.dumps(expanded_items, ensure_ascii=False),
                entry_total, daily_total_after, week_start, play_mode
            ))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"保存输入历史失败: {e}")

    def get_input_history_by_week(self, week_start: str, play_mode: str = None) -> List[Dict]:
        """获取指定周的输入历史记录，可按玩法模式过滤"""
        try:
            cursor = self.conn.cursor()

            if play_mode:
                # 按玩法模式过滤
                cursor.execute("""
                    SELECT id, ledger_id, batch_id, record_date, created_at, raw_input,
                           parsed_summary, expanded_items_json, entry_total, daily_total_after, status, play_mode
                    FROM input_history
                    WHERE week_start = ? AND play_mode = ?
                    ORDER BY record_date DESC, created_at DESC
                """, (week_start, play_mode))
            else:
                # 不过滤，获取所有（向后兼容）
                cursor.execute("""
                    SELECT id, ledger_id, batch_id, record_date, created_at, raw_input,
                           parsed_summary, expanded_items_json, entry_total, daily_total_after, status, play_mode
                    FROM input_history
                WHERE week_start = ?
                ORDER BY record_date DESC, created_at DESC
            """, (week_start,))

            results = []
            for row in cursor.fetchall():
                # 处理 play_mode 字段（可能为 NULL）
                try:
                    play_mode = row['play_mode'] if row['play_mode'] else 'number'
                except (KeyError, IndexError):
                    play_mode = 'number'

                results.append({
                    'id': row['id'],
                    'ledger_id': row['ledger_id'],
                    'batch_id': row['batch_id'],
                    'record_date': row['record_date'],
                    'created_at': row['created_at'],
                    'raw_input': row['raw_input'],
                    'parsed_summary': row['parsed_summary'],
                    'expanded_items': json.loads(row['expanded_items_json']) if row['expanded_items_json'] else [],
                    'entry_total': row['entry_total'],
                    'daily_total_after': row['daily_total_after'],
                    'status': row['status'],
                    'play_mode': play_mode
                })
            return results
        except sqlite3.Error as e:
            raise DatabaseError(f"获取输入历史失败: {e}")

    def mark_history_as_undone(self, history_id: int):
        """将历史记录标记为已撤销"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE input_history
                SET status = 'undone'
                WHERE id = ?
            """, (history_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"标记历史记录失败: {e}")

    def get_latest_active_history(self, ledger_id: int) -> Optional[Dict]:
        """获取指定账本的最新有效历史记录"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, batch_id, record_date, created_at, raw_input,
                       parsed_summary, expanded_items_json, entry_total, daily_total_after
                FROM input_history
                WHERE ledger_id = ? AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            """, (ledger_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'batch_id': row['batch_id'],
                    'record_date': row['record_date'],
                    'created_at': row['created_at'],
                    'raw_input': row['raw_input'],
                    'parsed_summary': row['parsed_summary'],
                    'expanded_items': json.loads(row['expanded_items_json']),
                    'entry_total': row['entry_total'],
                    'daily_total_after': row['daily_total_after']
                }
            return None
        except sqlite3.Error as e:
            raise DatabaseError(f"获取最新历史记录失败: {e}")
