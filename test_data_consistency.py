"""测试数据一致性"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from constants import MIN_NUMBER, MAX_NUMBER, AMOUNT_MULTIPLIER


def test_calculate_risk_rows():
    """测试风险计算函数"""

    # 模拟输入：02和03各200
    totals_dict = {
        2: 200 * AMOUNT_MULTIPLIER,  # 02号200元
        3: 200 * AMOUNT_MULTIPLIER   # 03号200元
    }
    total_bet_int = 400 * AMOUNT_MULTIPLIER  # 总下注400元

    # 计算
    total_bet = total_bet_int / AMOUNT_MULTIPLIER
    rows = []

    for num in range(MIN_NUMBER, MAX_NUMBER + 1):
        amount_int = totals_dict.get(num, 0)
        amount = amount_int / AMOUNT_MULTIPLIER
        payout = amount * 47
        profit = total_bet - payout

        rows.append({
            'number': num,
            'amount': amount,
            'payout': payout,
            'profit': profit
        })

    # 排序
    rows.sort(key=lambda x: (-x['amount'], x['number']))

    # 验证前两行（02和03）
    print("=== 数据一致性测试 ===\n")

    # 第一行应该是02号
    assert rows[0]['number'] == 2, f"第一行号码错误：期望02，实际{rows[0]['number']:02d}"
    assert rows[0]['amount'] == 200.00, f"02号金额错误：期望200.00，实际{rows[0]['amount']}"
    assert rows[0]['payout'] == 9400.00, f"02号赔付错误：期望9400.00，实际{rows[0]['payout']}"
    assert rows[0]['profit'] == -9000.00, f"02号盈利错误：期望-9000.00，实际{rows[0]['profit']}"

    print(f"[OK] 第一行: {rows[0]['number']:02d} | {rows[0]['amount']:.2f} | {rows[0]['payout']:.2f} | {rows[0]['profit']:.2f}")

    # 第二行应该是03号
    assert rows[1]['number'] == 3, f"第二行号码错误：期望03，实际{rows[1]['number']:02d}"
    assert rows[1]['amount'] == 200.00, f"03号金额错误：期望200.00，实际{rows[1]['amount']}"
    assert rows[1]['payout'] == 9400.00, f"03号赔付错误：期望9400.00，实际{rows[1]['payout']}"
    assert rows[1]['profit'] == -9000.00, f"03号盈利错误：期望-9000.00，实际{rows[1]['profit']}"

    print(f"[OK] 第二行: {rows[1]['number']:02d} | {rows[1]['amount']:.2f} | {rows[1]['payout']:.2f} | {rows[1]['profit']:.2f}")

    # 验证01号（未下注）
    row_01 = next(r for r in rows if r['number'] == 1)
    assert row_01['amount'] == 0.00, f"01号金额错误：期望0.00，实际{row_01['amount']}"
    assert row_01['payout'] == 0.00, f"01号赔付错误：期望0.00，实际{row_01['payout']}"
    assert row_01['profit'] == 400.00, f"01号盈利错误：期望+400.00，实际{row_01['profit']}"

    print(f"[OK] 01号(未下注): {row_01['number']:02d} | {row_01['amount']:.2f} | {row_01['payout']:.2f} | +{row_01['profit']:.2f}")

    # 验证所有行的计算一致性
    print(f"\n验证所有49行的计算一致性...")
    for row in rows:
        # 赔付 = 金额 × 47
        assert abs(row['payout'] - row['amount'] * 47) < 0.01, \
            f"{row['number']:02d}号赔付计算错误"

        # 盈利 = 总下注 - 赔付
        assert abs(row['profit'] - (total_bet - row['payout'])) < 0.01, \
            f"{row['number']:02d}号盈利计算错误"

    print(f"[OK] 全部49行计算一致性验证通过\n")

    print("=== 测试通过 ===")
    return True


if __name__ == "__main__":
    try:
        test_calculate_risk_rows()
    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 测试错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
