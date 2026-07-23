"""备份恢复测试"""
import unittest
import tempfile
import os
import json
from database import Database
from backup import BackupManager
from models import Batch, Instruction, Allocation
from constants import DEFAULT_ANIMAL_MAPPING, DB_VERSION


class TestBackup(unittest.TestCase):
    """备份恢复测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.backup_manager = BackupManager(self.db)

    def tearDown(self):
        """测试后清理"""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_export_import(self):
        """测试导出导入"""
        # 创建测试数据
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
        self.db.archive_ledger(ledger.id)

        # 导出
        temp_backup = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
        temp_backup.close()

        self.backup_manager.export_to_json(temp_backup.name)

        # 验证导出文件
        with open(temp_backup.name, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

        self.assertIn('version', backup_data)
        self.assertIn('settings', backup_data)
        self.assertIn('ledgers', backup_data)
        self.assertEqual(len(backup_data['ledgers']), 1)

        # 删除数据
        self.db.delete_ledgers([ledger.id])

        # 导入
        self.backup_manager.import_from_json(temp_backup.name)

        # 验证恢复
        totals = self.db.get_ledger_totals(ledger.id)
        self.assertEqual(totals[1], 1000)
        restored_ledger = self.db.get_ledger(ledger.id)
        self.assertEqual(restored_ledger.settled_total_integer, 1000)

        # 清理
        os.unlink(temp_backup.name)

    def test_validate_backup(self):
        """测试备份验证"""
        # 有效备份
        valid_backup = {
            "version": "1.0",
            "settings": {
                "db_version": str(DB_VERSION),
                "animal_mapping": json.dumps(DEFAULT_ANIMAL_MAPPING, ensure_ascii=False)
            },
            "ledgers": []
        }

        valid, error = self.backup_manager.validate_backup(valid_backup)
        self.assertTrue(valid)

        # 无效备份：缺少版本
        invalid_backup = {
            "settings": {},
            "ledgers": []
        }

        valid, error = self.backup_manager.validate_backup(invalid_backup)
        self.assertFalse(valid)

        # 无效备份：缺少必需设置，不能被接受后清空现有数据
        incomplete_backup = {
            "version": "1.0",
            "settings": {},
            "ledgers": []
        }
        valid, error = self.backup_manager.validate_backup(incomplete_backup)
        self.assertFalse(valid)


if __name__ == '__main__':
    unittest.main()
