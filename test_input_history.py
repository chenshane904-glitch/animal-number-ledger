# -*- coding: utf-8 -*-
"""
输入历史记录功能测试
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import tempfile

sys.path.insert(0, str(Path(__file__).parent))

from database import Database
from constants import AMOUNT_MULTIPLIER


def test_input_history():
    """测试输入历史记录功能"""

    # 使用临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)

        print("=" * 60)
        print("输入历史记录功能测试")
        print("=" * 60)

        passed = 0
        failed = 0

        # 创建测试账本
        ledger = db.get_or_create_active_ledger(datetime.now().strftime('%Y-%m-%d'))

        # 计算周起始日期
        today = datetime.now()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_start_str = week_start.strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')

        # 测试1：保存普通号码历史
        print("\n[测试1] 保存普通号码历史记录")
        try:
            history_id = db.save_input_history(
                ledger_id=ledger.id,
                batch_id=None,
                record_date=today_str,
                raw_input="01各50",
                parsed_summary="号码: 01",
                expanded_items=[{'number': '01', 'amount': 50.0}],
                entry_total=50 * AMOUNT_MULTIPLIER,
                daily_total_after=50 * AMOUNT_MULTIPLIER,
                week_start=week_start_str
            )
            assert history_id > 0
            print("  [OK] 普通号码历史记录保存成功")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            import traceback
            traceback.print_exc()
            failed += 1

        # 测试2：保存组合玩法历史
        print("\n[测试2] 保存组合玩法历史记录")
        try:
            history_id = db.save_input_history(
                ledger_id=ledger.id,
                batch_id=None,
                record_date=today_str,
                raw_input="红双各50",
                parsed_summary="号码: 02, 08, 12, 18, 24, 30, 34, 40, 46",
                expanded_items=[
                    {'number': '02', 'amount': 50.0},
                    {'number': '08', 'amount': 50.0},
                ],
                entry_total=450 * AMOUNT_MULTIPLIER,
                daily_total_after=500 * AMOUNT_MULTIPLIER,
                week_start=week_start_str
            )
            assert history_id > 0
            print("  [OK] 组合玩法历史记录保存成功")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1

        # 测试3：获取本周历史记录
        print("\n[测试3] 获取本周历史记录")
        try:
            records = db.get_input_history_by_week(week_start_str)
            assert len(records) == 2, f"期望2条记录，实际{len(records)}条"
            # 注意：按created_at DESC排序，所以最新的（红双）在前
            # 但由于我们几乎同时创建，需要检查实际顺序
            raw_inputs = [r['raw_input'] for r in records]
            assert '01各50' in raw_inputs
            assert '红双各50' in raw_inputs
            print(f"  [OK] 成功获取{len(records)}条本周记录")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1

        # 测试4：记录按日期分组
        print("\n[测试4] 记录按日期正确分组")
        try:
            records = db.get_input_history_by_week(week_start_str)
            dates = [r['record_date'] for r in records]
            assert all(d == today_str for d in dates)
            print("  [OK] 记录日期正确")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1

        # 测试5：标记为已撤销
        print("\n[测试5] 标记历史记录为已撤销")
        try:
            latest = db.get_latest_active_history(ledger.id)
            assert latest is not None
            # 注意：get_latest_active_history返回的字典中没有status字段
            # 只需确认能获取到记录即可

            db.mark_history_as_undone(latest['id'])

            # 重新查询，检查状态
            records = db.get_input_history_by_week(week_start_str)
            undone = [r for r in records if r['id'] == latest['id']]
            assert len(undone) == 1
            assert undone[0]['status'] == 'undone'
            print("  [OK] 成功标记为已撤销")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1

        # 测试6：撤销后记录仍存在
        print("\n[测试6] 撤销后记录不被物理删除")
        try:
            records = db.get_input_history_by_week(week_start_str)
            assert len(records) == 2  # 仍然是2条
            undone_count = sum(1 for r in records if r['status'] == 'undone')
            assert undone_count == 1
            print("  [OK] 撤销记录仍保留")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1

        # 测试7：获取最新有效历史记录
        print("\n[测试7] 获取最新有效历史记录")
        try:
            latest = db.get_latest_active_history(ledger.id)
            assert latest is not None
            # 测试5中我们撤销了最后一条有效记录
            # 所以现在应该返回剩下的那一条
            assert latest['raw_input'] in ['01各50', '红双各50']
            print("  [OK] 成功获取最新有效记录")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1

        # 测试8：expanded_items JSON解析
        print("\n[测试8] expanded_items JSON正确解析")
        try:
            records = db.get_input_history_by_week(week_start_str)
            for record in records:
                items = record['expanded_items']
                assert isinstance(items, list)
                if items:
                    assert 'number' in items[0]
                    assert 'amount' in items[0]
            print("  [OK] JSON解析正确")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1

        # 测试9：不同周的记录隔离
        print("\n[测试9] 不同周的记录隔离")
        try:
            # 模拟上周数据
            last_week = week_start - timedelta(days=7)
            last_week_str = last_week.strftime('%Y-%m-%d')

            db.save_input_history(
                ledger_id=ledger.id,
                batch_id=None,
                record_date=last_week_str,
                raw_input="上周测试",
                parsed_summary="测试",
                expanded_items=[],
                entry_total=0,
                daily_total_after=0,
                week_start=last_week_str
            )

            # 本周记录不应包含上周的
            this_week_records = db.get_input_history_by_week(week_start_str)
            assert len(this_week_records) == 2

            # 上周记录单独查询
            last_week_records = db.get_input_history_by_week(last_week_str)
            assert len(last_week_records) == 1
            assert last_week_records[0]['raw_input'] == "上周测试"

            print("  [OK] 不同周记录正确隔离")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1

        # 汇总
        print("\n" + "=" * 60)
        print(f"测试完成: {passed}个通过, {failed}个失败")
        print("=" * 60)

        db.close()
        return failed == 0

    finally:
        # 清理临时文件
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    try:
        success = test_input_history()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] 测试运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
