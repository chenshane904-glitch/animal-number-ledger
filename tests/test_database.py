"""数据库测试"""
import unittest
import tempfile
import os
from database import Database, DatabaseError
from constants import DEFAULT_ANIMAL_MAPPING


class TestDatabase(unittest.TestCase):
    """数据库测试"""

    def setUp(self):
        """测试前准备"""
        # 使用临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)

    def tearDown(self):
        """测试后清理"""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_init_db(self):
        """测试数据库初始化"""
        mapping = self.db.get_animal_mapping()
        self.assertEqual(len(mapping), 12)

    def test_validate_animal_mapping(self):
        """测试动物映射验证"""
        # 有效映射
        valid, error = self.db.validate_animal_mapping(DEFAULT_ANIMAL_MAPPING)
        self.assertTrue(valid)

        # 无效映射：缺少动物
        invalid_mapping = DEFAULT_ANIMAL_MAPPING.copy()
        invalid_mapping.pop('马')
        valid, error = self.db.validate_animal_mapping(invalid_mapping)
        self.assertFalse(valid)

        # 无效映射：重复号码
        invalid_mapping = DEFAULT_ANIMAL_MAPPING.copy()
        invalid_mapping['马'] = [1, 1, 13, 25, 37]
        valid, error = self.db.validate_animal_mapping(invalid_mapping)
        self.assertFalse(valid)

    def test_create_ledger(self):
        """测试创建账本"""
        ledger = self.db.get_or_create_active_ledger('2026-07-22')
        self.assertIsNotNone(ledger.id)
        self.assertEqual(ledger.ledger_date, '2026-07-22')
        self.assertEqual(ledger.sequence_number, 1)
        self.assertEqual(ledger.status, 'active')

    def test_ledger_totals(self):
        """测试账本累计"""
        from models import Batch, Instruction, Allocation
        import json

        ledger = self.db.get_or_create_active_ledger('2026-07-22')

        # 添加批次
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

        # 获取instruction的ID
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id FROM instructions WHERE batch_id = ?", (batch_id,))
        inst_id = cursor.fetchone()[0]

        # 添加分配
        allocation = Allocation(
            number=1,
            animal='马',
            amount_integer=1000,
            instruction_id=inst_id
        )
        self.db.add_allocations([allocation])

        # 验证累计
        totals = self.db.get_ledger_totals(ledger.id)
        self.assertEqual(totals[1], 1000)

    def test_atomic_batch_with_allocations(self):
        """批次、指令和分配必须在同一事务中保存"""
        from models import Batch, Instruction
        import json

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

        self.db.add_batch_with_allocations(
            ledger.id, batch, DEFAULT_ANIMAL_MAPPING
        )

        cursor = self.db.conn.cursor()
        self.assertEqual(cursor.execute("SELECT COUNT(*) FROM batches").fetchone()[0], 1)
        self.assertEqual(cursor.execute("SELECT COUNT(*) FROM instructions").fetchone()[0], 1)
        self.assertEqual(cursor.execute("SELECT COUNT(*) FROM allocations").fetchone()[0], 1)

    def test_atomic_batch_rolls_back_on_failure(self):
        """分配生成失败时不得留下半成品批次"""
        from models import Batch, Instruction
        import json

        ledger = self.db.get_or_create_active_ledger('2026-07-22')
        invalid_instruction = Instruction(
            source_line=1,
            original_text="50号10",
            normalized_text="50号10",
            target_type='number',
            targets=['50'],
            amount_integer=1000
        )
        batch = Batch(
            raw_input="50号10",
            total_before=0,
            total_after=1000,
            mapping_snapshot=json.dumps(DEFAULT_ANIMAL_MAPPING, ensure_ascii=False),
            instructions=[invalid_instruction]
        )

        with self.assertRaises(DatabaseError):
            self.db.add_batch_with_allocations(
                ledger.id, batch, DEFAULT_ANIMAL_MAPPING
            )

        cursor = self.db.conn.cursor()
        self.assertEqual(cursor.execute("SELECT COUNT(*) FROM batches").fetchone()[0], 0)
        self.assertEqual(cursor.execute("SELECT COUNT(*) FROM instructions").fetchone()[0], 0)
        self.assertEqual(cursor.execute("SELECT COUNT(*) FROM allocations").fetchone()[0], 0)

    def test_archive_ledger(self):
        """测试归档账本"""
        ledger = self.db.get_or_create_active_ledger('2026-07-22')
        settled_total = self.db.archive_ledger(ledger.id)

        # 验证状态
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT status FROM ledgers WHERE id = ?", (ledger.id,))
        status = cursor.fetchone()[0]
        self.assertEqual(status, 'archived')
        self.assertEqual(settled_total, 0)
        self.assertEqual(self.db.get_ledger(ledger.id).settled_total_integer, 0)

    def test_existing_archived_ledger_total_is_backfilled(self):
        """升级旧数据库时补算已归档账本的结算金额"""
        ledger = self.db.get_or_create_active_ledger('2026-07-21')
        self.db.archive_ledger(ledger.id)
        self.db.conn.execute(
            "UPDATE ledgers SET settled_total_integer = NULL WHERE id = ?",
            (ledger.id,)
        )
        self.db.conn.commit()
        self.db.close()

        self.db = Database(self.temp_db.name)
        restored = self.db.get_ledger(ledger.id)
        self.assertEqual(restored.settled_total_integer, 0)

    def test_delete_cascade(self):
        """测试级联删除"""
        from models import Batch, Instruction, Allocation
        import json

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

        # 获取instruction的ID并添加分配
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

        # 删除账本
        self.db.delete_ledgers([ledger.id])

        # 验证级联删除
        cursor.execute("SELECT COUNT(*) FROM batches WHERE id = ?", (batch_id,))
        self.assertEqual(cursor.fetchone()[0], 0)

        cursor.execute("SELECT COUNT(*) FROM instructions WHERE id = ?", (inst_id,))
        self.assertEqual(cursor.fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
