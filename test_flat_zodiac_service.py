# -*- coding: utf-8 -*-
"""
平特一肖独立服务自动测试
使用临时数据库，不污染正式账本
"""

import sqlite3
import os
import tempfile
from flat_zodiac_service import FlatZodiacService
from constants import AMOUNT_MULTIPLIER


def create_test_db():
    """创建测试数据库"""
    # 使用临时文件
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建必要的表
    cursor.execute("""
        CREATE TABLE ledgers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ledger_date TEXT NOT NULL,
            sequence_number INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        )
    """)

    cursor.execute("""
        CREATE TABLE flat_zodiac_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ledger_id INTEGER NOT NULL,
            raw_input TEXT NOT NULL,
            entry_total INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ledger_id) REFERENCES ledgers(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE flat_zodiac_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            zodiac TEXT NOT NULL,
            amount INTEGER NOT NULL,
            odds REAL NOT NULL DEFAULT 1.0,
            payout INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES flat_zodiac_batches(id) ON DELETE CASCADE
        )
    """)

    # 创建测试账本
    cursor.execute("INSERT INTO ledgers (ledger_date, sequence_number, status) VALUES ('2026-08-06', 1, 'active')")
    ledger_id = cursor.lastrowid

    conn.commit()

    return conn, db_path, ledger_id


def test_parse_input():
    """测试1：解析输入"""
    print("="*60)
    print("测试1：解析输入")
    print("="*60)

    conn, db_path, ledger_id = create_test_db()
    service = FlatZodiacService(conn)

    input_text = """虎100
龙200"""

    print(f"输入:\n{input_text}\n")

    try:
        entries = service.parse_input(input_text)

        print(f"解析结果: {len(entries)} 条记录")
        total = 0
        for e in entries:
            print(f"  {e.zodiac} = {e.amount:.2f}元")
            total += e.amount

        print(f"\n本次总额: {total:.2f}元")

        # 验证
        assert len(entries) == 2, f"期望2条记录，实际{len(entries)}"
        assert entries[0].zodiac == '虎', f"期望虎，实际{entries[0].zodiac}"
        assert entries[0].amount == 100.0, f"期望100.0，实际{entries[0].amount}"
        assert entries[1].zodiac == '龙', f"期望龙，实际{entries[1].zodiac}"
        assert entries[1].amount == 200.0, f"期望200.0，实际{entries[1].amount}"
        assert total == 300.0, f"期望总额300.0，实际{total}"

        print("\n[PASS] 测试1通过")
        return True

    except Exception as e:
        print(f"\n[FAIL] 测试1失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()
        os.remove(db_path)


def test_add_batch():
    """测试2：添加批次并查询"""
    print("\n" + "="*60)
    print("测试2：添加批次并查询")
    print("="*60)

    conn, db_path, ledger_id = create_test_db()
    service = FlatZodiacService(conn)

    input_text = """虎100
龙200"""

    try:
        # 解析
        entries = service.parse_input(input_text)

        # 添加批次
        batch_id = service.add_batch(ledger_id, input_text, entries)
        print(f"批次ID: {batch_id}")

        # 验证数据库
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM flat_zodiac_batches WHERE ledger_id = ?", (ledger_id,))
        batch_count = cursor.fetchone()[0]
        print(f"批次数: {batch_count}")

        cursor.execute("SELECT COUNT(*) FROM flat_zodiac_items WHERE batch_id = ?", (batch_id,))
        item_count = cursor.fetchone()[0]
        print(f"明细数: {item_count}")

        # 查询汇总
        summary = service.get_summary(ledger_id)

        print(f"\n查询结果:")
        print(f"  总下注: {summary['total_bet'] / AMOUNT_MULTIPLIER:.2f}元")
        print(f"  非零生肖: {summary['non_zero_count']}")
        print(f"  最高下注生肖: {summary['max_zodiac']}")
        print(f"  最高金额: {summary['max_amount'] / AMOUNT_MULTIPLIER:.2f}元")
        print(f"\n  生肖明细:")
        for zodiac, amount in summary['zodiac_amounts'].items():
            if amount > 0:
                print(f"    {zodiac} = {amount / AMOUNT_MULTIPLIER:.2f}元")

        # 验证
        assert batch_count == 1, f"期望1条批次，实际{batch_count}"
        assert item_count == 2, f"期望2条明细，实际{item_count}"
        assert summary['total_bet'] == 30000, f"期望30000分，实际{summary['total_bet']}"
        assert summary['non_zero_count'] == 2, f"期望2个非零生肖，实际{summary['non_zero_count']}"
        assert summary['max_zodiac'] == '龙', f"期望龙，实际{summary['max_zodiac']}"
        assert summary['max_amount'] == 20000, f"期望20000分，实际{summary['max_amount']}"
        assert summary['zodiac_amounts']['虎'] == 10000, f"期望虎10000分，实际{summary['zodiac_amounts']['虎']}"
        assert summary['zodiac_amounts']['龙'] == 20000, f"期望龙20000分，实际{summary['zodiac_amounts']['龙']}"

        print("\n[PASS] 测试2通过")
        return True

    except Exception as e:
        print(f"\n[FAIL] 测试2失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()
        os.remove(db_path)


def test_accumulate():
    """测试3：累加测试"""
    print("\n" + "="*60)
    print("测试3：累加测试")
    print("="*60)

    conn, db_path, ledger_id = create_test_db()
    service = FlatZodiacService(conn)

    try:
        # 第一次：虎100、龙200
        input1 = """虎100
龙200"""
        entries1 = service.parse_input(input1)
        service.add_batch(ledger_id, input1, entries1)

        print(f"第一次添加: 虎100、龙200")

        # 第二次：虎50
        input2 = "虎50"
        entries2 = service.parse_input(input2)
        service.add_batch(ledger_id, input2, entries2)

        print(f"第二次添加: 虎50")

        # 查询汇总
        summary = service.get_summary(ledger_id)

        print(f"\n累加后结果:")
        print(f"  虎 = {summary['zodiac_amounts']['虎'] / AMOUNT_MULTIPLIER:.2f}元")
        print(f"  龙 = {summary['zodiac_amounts']['龙'] / AMOUNT_MULTIPLIER:.2f}元")
        print(f"  总下注 = {summary['total_bet'] / AMOUNT_MULTIPLIER:.2f}元")

        # 验证
        assert summary['zodiac_amounts']['虎'] == 15000, f"期望虎15000分，实际{summary['zodiac_amounts']['虎']}"
        assert summary['zodiac_amounts']['龙'] == 20000, f"期望龙20000分，实际{summary['zodiac_amounts']['龙']}"
        assert summary['total_bet'] == 35000, f"期望35000分，实际{summary['total_bet']}"

        print("\n[PASS] 测试3通过")
        return True

    except Exception as e:
        print(f"\n[FAIL] 测试3失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()
        os.remove(db_path)


def test_no_allocations():
    """测试4：确认没有allocations数据"""
    print("\n" + "="*60)
    print("测试4：确认没有allocations数据")
    print("="*60)

    conn, db_path, ledger_id = create_test_db()

    # 添加allocations表（如果存在）
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instruction_id INTEGER NOT NULL,
            number INTEGER NOT NULL,
            animal TEXT NOT NULL,
            amount_integer INTEGER NOT NULL
        )
    """)
    conn.commit()

    service = FlatZodiacService(conn)

    try:
        # 添加平特一肖数据
        input_text = """虎100
龙200"""
        entries = service.parse_input(input_text)
        service.add_batch(ledger_id, input_text, entries)

        # 检查allocations表
        cursor.execute("SELECT COUNT(*) FROM allocations")
        alloc_count = cursor.fetchone()[0]

        print(f"allocations表记录数: {alloc_count}")

        # 验证
        assert alloc_count == 0, f"期望0条allocations，实际{alloc_count}"

        print("\n[PASS] 测试4通过 - 平特一肖不写入allocations")
        return True

    except Exception as e:
        print(f"\n[FAIL] 测试4失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()
        os.remove(db_path)


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("平特一肖独立服务 - 自动测试")
    print("="*70 + "\n")

    results = []

    results.append(("测试1: 解析输入", test_parse_input()))
    results.append(("测试2: 添加批次并查询", test_add_batch()))
    results.append(("测试3: 累加测试", test_accumulate()))
    results.append(("测试4: 确认无allocations", test_no_allocations()))

    print("\n" + "="*70)
    print("测试总结")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\n通过率: {passed}/{total}")

    if passed == total:
        print("\n所有测试通过！可以连接UI。")
        return True
    else:
        print(f"\n还有 {total - passed} 个测试失败，请修复后再连接UI。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
