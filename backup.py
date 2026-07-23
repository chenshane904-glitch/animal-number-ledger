"""备份与恢复模块"""
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from database import Database, DatabaseError
from constants import (
    BACKUP_VERSION, DB_VERSION, MIN_NUMBER, MAX_NUMBER, MAX_AMOUNT_INTEGER
)


class BackupError(Exception):
    """备份错误"""
    pass


class BackupManager:
    """备份管理器"""

    def __init__(self, db: Database):
        """
        初始化备份管理器

        Args:
            db: 数据库实例
        """
        self.db = db

    def export_to_json(self, output_path: str):
        """
        导出完整备份到JSON

        Args:
            output_path: 输出文件路径
        """
        try:
            cursor = self.db.conn.cursor()

            # 收集所有数据
            backup_data = {
                "version": BACKUP_VERSION,
                "exported_at": datetime.now().isoformat(),
                "settings": {},
                "ledgers": []
            }

            # 导出设置
            cursor.execute("SELECT key, value FROM settings")
            for row in cursor.fetchall():
                backup_data["settings"][row['key']] = row['value']

            # 导出账本
            cursor.execute("""
                SELECT id, ledger_date, sequence_number, status, created_at,
                       archived_at, settled_total_integer
                FROM ledgers
                ORDER BY ledger_date, sequence_number
            """)
            ledgers = cursor.fetchall()

            for ledger_row in ledgers:
                ledger_data = {
                    "id": ledger_row['id'],
                    "ledger_date": ledger_row['ledger_date'],
                    "sequence_number": ledger_row['sequence_number'],
                    "status": ledger_row['status'],
                    "created_at": str(ledger_row['created_at']),
                    "archived_at": str(ledger_row['archived_at']) if ledger_row['archived_at'] else None,
                    "settled_total_integer": ledger_row['settled_total_integer'],
                    "batches": []
                }

                # 导出批次
                cursor.execute("""
                    SELECT id, created_at, raw_input, total_before, total_after, mapping_snapshot
                    FROM batches
                    WHERE ledger_id = ?
                    ORDER BY created_at
                """, (ledger_row['id'],))
                batches = cursor.fetchall()

                for batch_row in batches:
                    batch_data = {
                        "id": batch_row['id'],
                        "created_at": str(batch_row['created_at']),
                        "raw_input": batch_row['raw_input'],
                        "total_before": batch_row['total_before'],
                        "total_after": batch_row['total_after'],
                        "mapping_snapshot": batch_row['mapping_snapshot'],
                        "instructions": []
                    }

                    # 导出指令
                    cursor.execute("""
                        SELECT id, source_line, original_text, normalized_text,
                               target_type, targets, amount_integer, warning
                        FROM instructions
                        WHERE batch_id = ?
                        ORDER BY source_line
                    """, (batch_row['id'],))
                    instructions = cursor.fetchall()

                    for inst_row in instructions:
                        inst_data = {
                            "id": inst_row['id'],
                            "source_line": inst_row['source_line'],
                            "original_text": inst_row['original_text'],
                            "normalized_text": inst_row['normalized_text'],
                            "target_type": inst_row['target_type'],
                            "targets": inst_row['targets'],
                            "amount_integer": inst_row['amount_integer'],
                            "warning": inst_row['warning'],
                            "allocations": []
                        }

                        # 导出分配
                        cursor.execute("""
                            SELECT id, number, animal, amount_integer
                            FROM allocations
                            WHERE instruction_id = ?
                            ORDER BY number
                        """, (inst_row['id'],))
                        allocations = cursor.fetchall()

                        for alloc_row in allocations:
                            alloc_data = {
                                "id": alloc_row['id'],
                                "number": alloc_row['number'],
                                "animal": alloc_row['animal'],
                                "amount_integer": alloc_row['amount_integer']
                            }
                            inst_data["allocations"].append(alloc_data)

                        batch_data["instructions"].append(inst_data)

                    ledger_data["batches"].append(batch_data)

                backup_data["ledgers"].append(ledger_data)

            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise BackupError(f"导出备份失败: {e}")

    def validate_backup(self, backup_data: dict) -> tuple[bool, str]:
        """
        验证备份数据

        Returns:
            (是否有效, 错误信息)
        """
        if not isinstance(backup_data, dict):
            return False, "备份根节点必须是对象"

        # 检查版本
        if "version" not in backup_data:
            return False, "备份数据缺少版本信息"
        if backup_data["version"] != BACKUP_VERSION:
            return False, f"不支持的备份版本: {backup_data['version']}"

        # 检查必需字段
        if "settings" not in backup_data or not isinstance(backup_data["settings"], dict):
            return False, "备份数据缺少设置信息"

        if "ledgers" not in backup_data or not isinstance(backup_data["ledgers"], list):
            return False, "备份数据缺少账本信息"

        settings = backup_data["settings"]
        for required_setting in ("db_version", "animal_mapping"):
            if required_setting not in settings:
                return False, f"备份设置缺少: {required_setting}"

        if str(settings["db_version"]) != str(DB_VERSION):
            return False, f"不支持的数据库版本: {settings['db_version']}"

        # 验证动物映射
        try:
            mapping = json.loads(settings["animal_mapping"])
            valid, error = self.db.validate_animal_mapping(mapping)
            if not valid:
                return False, f"备份中的动物映射无效: {error}"
        except (json.JSONDecodeError, TypeError):
            return False, "备份中的动物映射格式错误"

        def is_integer(value):
            return isinstance(value, int) and not isinstance(value, bool)

        def valid_amount(value):
            return is_integer(value) and 0 <= value <= MAX_AMOUNT_INTEGER

        ledger_ids = set()
        batch_ids = set()
        instruction_ids = set()
        allocation_ids = set()

        for ledger_index, ledger in enumerate(backup_data["ledgers"], 1):
            if not isinstance(ledger, dict):
                return False, f"第{ledger_index}个账本格式错误"

            required_ledger = (
                "id", "ledger_date", "sequence_number", "status",
                "created_at", "batches"
            )
            for field in required_ledger:
                if field not in ledger:
                    return False, f"第{ledger_index}个账本缺少字段: {field}"

            if not is_integer(ledger["id"]) or ledger["id"] <= 0:
                return False, f"第{ledger_index}个账本ID无效"
            if ledger["id"] in ledger_ids:
                return False, f"账本ID重复: {ledger['id']}"
            ledger_ids.add(ledger["id"])

            try:
                datetime.strptime(ledger["ledger_date"], "%Y-%m-%d")
            except (TypeError, ValueError):
                return False, f"第{ledger_index}个账本日期无效"

            if not is_integer(ledger["sequence_number"]) or ledger["sequence_number"] <= 0:
                return False, f"第{ledger_index}个账本编号无效"
            if ledger["status"] not in ("active", "archived"):
                return False, f"第{ledger_index}个账本状态无效"
            if not isinstance(ledger["batches"], list):
                return False, f"第{ledger_index}个账本批次格式错误"

            settled_total = ledger.get("settled_total_integer")
            if settled_total is not None and not valid_amount(settled_total):
                return False, f"第{ledger_index}个账本结算金额无效"

            ledger_total = 0
            previous_total = None
            for batch_index, batch in enumerate(ledger["batches"], 1):
                if not isinstance(batch, dict):
                    return False, f"账本{ledger_index}的第{batch_index}个批次格式错误"

                required_batch = (
                    "id", "created_at", "raw_input", "total_before",
                    "total_after", "mapping_snapshot", "instructions"
                )
                for field in required_batch:
                    if field not in batch:
                        return False, f"批次{batch_index}缺少字段: {field}"

                if not is_integer(batch["id"]) or batch["id"] <= 0:
                    return False, f"批次ID无效: {batch.get('id')}"
                if batch["id"] in batch_ids:
                    return False, f"批次ID重复: {batch['id']}"
                batch_ids.add(batch["id"])

                if not valid_amount(batch["total_before"]) or not valid_amount(batch["total_after"]):
                    return False, f"批次{batch['id']}累计金额无效"
                if previous_total is not None and batch["total_before"] != previous_total:
                    return False, f"批次{batch['id']}与上一批次累计金额不连续"

                try:
                    snapshot = json.loads(batch["mapping_snapshot"])
                    valid, error = self.db.validate_animal_mapping(snapshot)
                    if not valid:
                        return False, f"批次{batch['id']}动物映射无效: {error}"
                except (json.JSONDecodeError, TypeError):
                    return False, f"批次{batch['id']}动物映射格式错误"

                if not isinstance(batch["instructions"], list):
                    return False, f"批次{batch['id']}指令格式错误"

                reverse_mapping = {
                    number: animal
                    for animal, numbers in snapshot.items()
                    for number in numbers
                }
                batch_delta = 0
                source_lines = set()

                for instruction in batch["instructions"]:
                    if not isinstance(instruction, dict):
                        return False, f"批次{batch['id']}包含无效指令"

                    required_instruction = (
                        "id", "source_line", "original_text", "normalized_text",
                        "target_type", "targets", "amount_integer", "allocations"
                    )
                    for field in required_instruction:
                        if field not in instruction:
                            return False, f"批次{batch['id']}指令缺少字段: {field}"

                    instruction_id = instruction["id"]
                    if not is_integer(instruction_id) or instruction_id <= 0:
                        return False, f"指令ID无效: {instruction_id}"
                    if instruction_id in instruction_ids:
                        return False, f"指令ID重复: {instruction_id}"
                    instruction_ids.add(instruction_id)

                    source_line = instruction["source_line"]
                    if not is_integer(source_line) or source_line <= 0 or source_line in source_lines:
                        return False, f"批次{batch['id']}指令行号无效或重复"
                    source_lines.add(source_line)

                    if instruction["target_type"] not in ("number", "animal"):
                        return False, f"指令{instruction_id}目标类型无效"
                    if not valid_amount(instruction["amount_integer"]):
                        return False, f"指令{instruction_id}金额无效"

                    try:
                        targets = json.loads(instruction["targets"])
                    except (json.JSONDecodeError, TypeError):
                        return False, f"指令{instruction_id}目标格式错误"
                    if not isinstance(targets, list) or not targets:
                        return False, f"指令{instruction_id}没有有效目标"

                    expected_allocations = []
                    if instruction["target_type"] == "number":
                        for target in targets:
                            try:
                                number = int(target)
                            except (TypeError, ValueError):
                                return False, f"指令{instruction_id}号码无效"
                            if number not in reverse_mapping:
                                return False, f"指令{instruction_id}号码超出范围"
                            expected_allocations.append(
                                (number, reverse_mapping[number], instruction["amount_integer"])
                            )
                    else:
                        for animal in targets:
                            if animal not in snapshot:
                                return False, f"指令{instruction_id}动物无效: {animal}"
                            for number in snapshot[animal]:
                                expected_allocations.append(
                                    (number, animal, instruction["amount_integer"])
                                )

                    if not isinstance(instruction["allocations"], list):
                        return False, f"指令{instruction_id}分配记录格式错误"

                    actual_allocations = []
                    for allocation in instruction["allocations"]:
                        if not isinstance(allocation, dict):
                            return False, f"指令{instruction_id}包含无效分配记录"
                        for field in ("id", "number", "animal", "amount_integer"):
                            if field not in allocation:
                                return False, f"指令{instruction_id}分配记录缺少字段: {field}"

                        allocation_id = allocation["id"]
                        if not is_integer(allocation_id) or allocation_id <= 0:
                            return False, f"分配记录ID无效: {allocation_id}"
                        if allocation_id in allocation_ids:
                            return False, f"分配记录ID重复: {allocation_id}"
                        allocation_ids.add(allocation_id)

                        number = allocation["number"]
                        amount = allocation["amount_integer"]
                        if not is_integer(number) or not MIN_NUMBER <= number <= MAX_NUMBER:
                            return False, f"分配记录{allocation_id}号码无效"
                        if not isinstance(allocation["animal"], str) or not valid_amount(amount):
                            return False, f"分配记录{allocation_id}内容无效"
                        actual_allocations.append((number, allocation["animal"], amount))

                    if sorted(actual_allocations) != sorted(expected_allocations):
                        return False, f"指令{instruction_id}分配记录与目标不一致"

                    instruction_total = sum(item[2] for item in actual_allocations)
                    if instruction_total > MAX_AMOUNT_INTEGER - batch_delta:
                        return False, f"批次{batch['id']}金额超出范围"
                    batch_delta += instruction_total

                if batch["total_after"] != batch["total_before"] + batch_delta:
                    return False, f"批次{batch['id']}累计金额校验失败"

                previous_total = batch["total_after"]
                if batch_delta > MAX_AMOUNT_INTEGER - ledger_total:
                    return False, f"账本{ledger['id']}金额超出范围"
                ledger_total += batch_delta

            if ledger["status"] == "archived" and settled_total is not None:
                if settled_total != ledger_total:
                    return False, f"账本{ledger['id']}结算金额与明细不一致"

        return True, ""

    def import_from_json(self, input_path: str):
        """
        从JSON恢复备份

        Args:
            input_path: 输入文件路径
        """
        try:
            # 读取文件
            with open(input_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            # 验证
            valid, error = self.validate_backup(backup_data)
            if not valid:
                raise BackupError(f"备份验证失败: {error}")

            # 使用事务恢复
            cursor = self.db.conn.cursor()
            cursor.execute("BEGIN TRANSACTION")

            try:
                # 清空现有数据（保留表结构）
                cursor.execute("DELETE FROM allocations")
                cursor.execute("DELETE FROM instructions")
                cursor.execute("DELETE FROM batches")
                cursor.execute("DELETE FROM ledgers")
                cursor.execute("DELETE FROM settings")

                # 恢复设置
                for key, value in backup_data["settings"].items():
                    cursor.execute(
                        "INSERT INTO settings (key, value) VALUES (?, ?)",
                        (key, value)
                    )

                # 恢复账本
                for ledger in backup_data["ledgers"]:
                    cursor.execute("""
                        INSERT INTO ledgers
                        (id, ledger_date, sequence_number, status, created_at,
                         archived_at, settled_total_integer)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ledger['id'],
                        ledger['ledger_date'],
                        ledger['sequence_number'],
                        ledger['status'],
                        ledger['created_at'],
                        ledger.get('archived_at'),
                        ledger.get('settled_total_integer')
                    ))

                    # 恢复批次
                    for batch in ledger['batches']:
                        cursor.execute("""
                            INSERT INTO batches (id, ledger_id, created_at, raw_input, total_before, total_after, mapping_snapshot)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            batch['id'],
                            ledger['id'],
                            batch['created_at'],
                            batch['raw_input'],
                            batch['total_before'],
                            batch['total_after'],
                            batch['mapping_snapshot']
                        ))

                        # 恢复指令
                        for instruction in batch['instructions']:
                            cursor.execute("""
                                INSERT INTO instructions (id, batch_id, source_line, original_text, normalized_text,
                                                         target_type, targets, amount_integer, warning)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                instruction['id'],
                                batch['id'],
                                instruction['source_line'],
                                instruction['original_text'],
                                instruction['normalized_text'],
                                instruction['target_type'],
                                instruction['targets'],
                                instruction['amount_integer'],
                                instruction['warning']
                            ))

                            # 恢复分配
                            for allocation in instruction['allocations']:
                                cursor.execute("""
                                    INSERT INTO allocations (id, instruction_id, number, animal, amount_integer)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (
                                    allocation['id'],
                                    instruction['id'],
                                    allocation['number'],
                                    allocation['animal'],
                                    allocation['amount_integer']
                                ))

                # 兼容旧备份：如归档账本没有结算字段，则由明细重新计算。
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

                cursor.execute("PRAGMA foreign_key_check")
                if cursor.fetchone() is not None:
                    raise BackupError("备份包含无效的数据关联")

                cursor.execute("COMMIT")

            except Exception as e:
                cursor.execute("ROLLBACK")
                raise BackupError(f"恢复数据时发生错误，已回滚: {e}")

        except json.JSONDecodeError as e:
            raise BackupError(f"备份文件格式错误: {e}")
        except FileNotFoundError:
            raise BackupError(f"备份文件不存在: {input_path}")
        except Exception as e:
            raise BackupError(f"导入备份失败: {e}")

    def export_csv(self, ledger_id: int, output_path: str):
        """
        导出指定账本为CSV

        Args:
            ledger_id: 账本ID
            output_path: 输出文件路径
        """
        import csv

        try:
            cursor = self.db.conn.cursor()

            # 获取所有分配记录
            cursor.execute("""
                SELECT
                    l.ledger_date,
                    l.sequence_number,
                    b.created_at,
                    i.original_text,
                    a.number,
                    a.animal,
                    a.amount_integer
                FROM allocations a
                JOIN instructions i ON a.instruction_id = i.id
                JOIN batches b ON i.batch_id = b.id
                JOIN ledgers l ON b.ledger_id = l.id
                WHERE l.id = ?
                ORDER BY b.created_at, i.source_line, a.number
            """, (ledger_id,))

            rows = cursor.fetchall()

            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['日期', '账本编号', '添加时间', '原始指令', '号码', '动物', '金额'])

                for row in rows:
                    writer.writerow([
                        row['ledger_date'],
                        row['sequence_number'],
                        row['created_at'],
                        row['original_text'],
                        row['number'],
                        row['animal'],
                        row['amount_integer'] / 100  # 转换回小数
                    ])

        except Exception as e:
            raise BackupError(f"导出CSV失败: {e}")
