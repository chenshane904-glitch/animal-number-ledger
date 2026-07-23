"""删除功能测试"""
import unittest
import tempfile
import os
from database import Database
from models import Batch, Instruction, Allocation
import json
from constants import DEFAULT_ANIMAL_MAPPING


class TestDeletion(unittest.TestCase):
    """删除功能测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)

    def tearDown(self):
        """测试后清理"""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_delete_batch(self):
        """测试删除批次"""
        ledger = self.db.get_or_create_active_ledger('2026-07-22')

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

        batch_id = self.db.add_batch(ledger.id, batch)

        # 添加分配
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id FROM instructions WHERE batch_id = ?", (batch_id,))
        inst_id = cursor.fetchone()[0]

        allocation = Allocation(
            number=1,
            animal='马',
            amount_integer=1000,
            instruction_id=inst_id
        )
        self.db.add_allocations([allocation])

        # 删除批次
        self.db.delete_batch(batch_id)

        # 验证删除
        cursor.execute("SELECT COUNT(*) FROM batches WHERE id = ?", (batch_id,))
        self.assertEqual(cursor.fetchone()[0], 0)

        cursor.execute("SELECT COUNT(*) FROM instructions WHERE batch_id = ?", (batch_id,))
        self.assertEqual(cursor.fetchone()[0], 0)

        cursor.execute("SELECT COUNT(*) FROM allocations WHERE instruction_id = ?", (inst_id,))
        self.assertEqual(cursor.fetchone()[0], 0)

    def test_delete_ledger(self):
        """测试删除账本"""
        ledger = self.db.get_or_create_active_ledger('2026-07-22')

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

        batch_id = self.db.add_batch(ledger.id, batch)

        # 删除账本
        self.db.delete_ledgers([ledger.id])

        # 验证删除
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ledgers WHERE id = ?", (ledger.id,))
        self.assertEqual(cursor.fetchone()[0], 0)

        cursor.execute("SELECT COUNT(*) FROM batches WHERE ledger_id = ?", (ledger.id,))
        self.assertEqual(cursor.fetchone()[0], 0)

    def test_delete_all_archived(self):
        """测试删除全部归档"""
        # 创建多个账本
        ledger1 = self.db.get_or_create_active_ledger('2026-07-22')
        self.db.archive_ledger(ledger1.id)

        ledger2 = self.db.get_or_create_active_ledger('2026-07-23')

        # 删除全部归档
        self.db.delete_all_archived_ledgers()

        # 验证
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ledgers WHERE status = 'archived'")
        self.assertEqual(cursor.fetchone()[0], 0)

        cursor.execute("SELECT COUNT(*) FROM ledgers WHERE status = 'active'")
        self.assertEqual(cursor.fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main()
