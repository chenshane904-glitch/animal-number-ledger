"""跨日归档测试"""
import unittest
import tempfile
import os
from datetime import datetime
from database import Database
from daily_rollover import DailyRollover
from models import Batch, Instruction
from constants import DEFAULT_ANIMAL_MAPPING
import json


class TestRollover(unittest.TestCase):
    """跨日归档测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)

    def tearDown(self):
        """测试后清理"""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_no_rollover_same_day(self):
        """测试同一天不归档"""
        def mock_time():
            return datetime(2026, 7, 22, 10, 0, 0)

        rollover = DailyRollover(self.db, mock_time)
        ledger = self.db.get_or_create_active_ledger('2026-07-22')

        # 首次检查
        rolled, date = rollover.check_and_rollover(ledger.id)
        self.assertFalse(rolled)
        self.assertEqual(date, '2026-07-22')

        # 同一天再次检查
        rolled, date = rollover.check_and_rollover(ledger.id)
        self.assertFalse(rolled)
        self.assertEqual(date, '2026-07-22')

    def test_rollover_next_day(self):
        """测试跨日归档"""
        current_date = datetime(2026, 7, 22, 23, 59, 0)

        def mock_time():
            return current_date

        rollover = DailyRollover(self.db, mock_time)
        ledger = self.db.get_or_create_active_ledger('2026-07-22')

        # 首次检查
        rolled, date = rollover.check_and_rollover(ledger.id)
        self.assertFalse(rolled)

        # 跨日
        current_date = datetime(2026, 7, 23, 0, 1, 0)

        rolled, date = rollover.check_and_rollover(ledger.id)
        self.assertTrue(rolled)
        self.assertEqual(date, '2026-07-23')

        # 验证归档
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT status FROM ledgers WHERE id = ?", (ledger.id,))
        status = cursor.fetchone()[0]
        self.assertEqual(status, 'archived')

    def test_multiple_rollover_prevention(self):
        """测试防止重复归档"""
        current_date = datetime(2026, 7, 22, 10, 0, 0)

        def mock_time():
            return current_date

        rollover = DailyRollover(self.db, mock_time)
        ledger = self.db.get_or_create_active_ledger('2026-07-22')

        rollover.check_and_rollover(ledger.id)

        # 跨到第二天
        current_date = datetime(2026, 7, 23, 10, 0, 0)
        rolled, _ = rollover.check_and_rollover(ledger.id)
        self.assertTrue(rolled)

        # 同一天不应该再次归档
        rolled, _ = rollover.check_and_rollover(ledger.id)
        self.assertFalse(rolled)

    def test_startup_archives_stale_ledger_with_total(self):
        """跨日关闭后再启动也必须结算旧账本"""
        old_ledger = self.db.get_or_create_active_ledger('2026-07-21')
        instruction = Instruction(
            source_line=1,
            original_text="1号10",
            normalized_text="1号10",
            target_type='number',
            targets=['1'],
            amount_integer=1000
        )
        batch = Batch(
            raw_input="1号10",
            total_before=0,
            total_after=1000,
            mapping_snapshot=json.dumps(DEFAULT_ANIMAL_MAPPING, ensure_ascii=False),
            instructions=[instruction]
        )
        self.db.add_batch_with_allocations(
            old_ledger.id, batch, DEFAULT_ANIMAL_MAPPING
        )

        rollover = DailyRollover(
            self.db, lambda: datetime(2026, 7, 22, 9, 0, 0)
        )
        settlements = rollover.initialize()

        self.assertEqual(settlements, [(old_ledger.id, '2026-07-21', 1000)])
        archived = self.db.get_ledger(old_ledger.id)
        self.assertEqual(archived.status, 'archived')
        self.assertEqual(archived.settled_total_integer, 1000)


if __name__ == '__main__':
    unittest.main()
