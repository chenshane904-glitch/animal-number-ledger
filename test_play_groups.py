# -*- coding: utf-8 -*-
"""
组合玩法功能测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING, AMOUNT_MULTIPLIER


def run_all_tests():
    """运行所有测试"""
    parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    print("=" * 60)
    print("组合玩法功能测试")
    print("=" * 60)

    passed = 0
    failed = 0

    # 测试1：红单各50
    print("\n[测试1] 红单各50")
    try:
        instructions = parser.parse_input("红单各50")
        assert len(instructions) == 1
        targets = instructions[0].targets
        assert len(targets) == 8, f"期望8个号码，实际{len(targets)}个"
        assert set(targets) == {'01', '07', '13', '19', '23', '29', '35', '45'}
        assert instructions[0].amount_integer == 50 * AMOUNT_MULTIPLIER
        total = len(targets) * 50
        assert total == 400
        print(f"  [OK] 展开{len(targets)}个号码，每号50，总金额{total}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试2：绿单各20
    print("\n[测试2] 绿单各20")
    try:
        instructions = parser.parse_input("绿单各20")
        assert len(instructions) == 1
        targets = instructions[0].targets
        assert len(targets) == 9, f"期望9个号码，实际{len(targets)}个"
        assert set(targets) == {'05', '11', '17', '21', '27', '33', '39', '43', '49'}
        total = len(targets) * 20
        assert total == 180
        print(f"  [OK] 展开{len(targets)}个号码，每号20，总金额{total}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试3：红波各10
    print("\n[测试3] 红波各10")
    try:
        instructions = parser.parse_input("红波各10")
        assert len(instructions) == 1
        targets = instructions[0].targets
        assert len(targets) == 17, f"期望17个号码，实际{len(targets)}个"
        total = len(targets) * 10
        assert total == 170
        print(f"  [OK] 展开{len(targets)}个号码，每号10，总金额{total}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试4：单各5
    print("\n[测试4] 单各5")
    try:
        instructions = parser.parse_input("单各5")
        assert len(instructions) == 1
        targets = instructions[0].targets
        assert len(targets) == 25, f"期望25个号码，实际{len(targets)}个"
        total = len(targets) * 5
        assert total == 125
        print(f"  [OK] 展开{len(targets)}个号码，每号5，总金额{total}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试5：双各5
    print("\n[测试5] 双各5")
    try:
        instructions = parser.parse_input("双各5")
        assert len(instructions) == 1
        targets = instructions[0].targets
        assert len(targets) == 24, f"期望24个号码，实际{len(targets)}个"
        total = len(targets) * 5
        assert total == 120
        print(f"  [OK] 展开{len(targets)}个号码，每号5，总金额{total}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试6：尾大各10
    print("\n[测试6] 尾大各10")
    try:
        instructions = parser.parse_input("尾大各10")
        assert len(instructions) == 1
        targets = instructions[0].targets
        assert len(targets) == 25, f"期望25个号码，实际{len(targets)}个"
        total = len(targets) * 10
        assert total == 250
        print(f"  [OK] 展开{len(targets)}个号码，每号10，总金额{total}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试7：尾小各10
    print("\n[测试7] 尾小各10")
    try:
        instructions = parser.parse_input("尾小各10")
        assert len(instructions) == 1
        targets = instructions[0].targets
        assert len(targets) == 24, f"期望24个号码，实际{len(targets)}个"
        total = len(targets) * 10
        assert total == 240
        print(f"  [OK] 展开{len(targets)}个号码，每号10，总金额{total}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试8：0尾各20
    print("\n[测试8] 0尾各20")
    try:
        instructions = parser.parse_input("0尾各20")
        assert len(instructions) == 1
        targets = instructions[0].targets
        assert len(targets) == 4, f"期望4个号码，实际{len(targets)}个"
        assert set(targets) == {'10', '20', '30', '40'}
        total = len(targets) * 20
        assert total == 80
        print(f"  [OK] 展开{len(targets)}个号码，每号20，总金额{total}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试9：9尾各20
    print("\n[测试9] 9尾各20")
    try:
        instructions = parser.parse_input("9尾各20")
        assert len(instructions) == 1
        targets = instructions[0].targets
        assert len(targets) == 5, f"期望5个号码，实际{len(targets)}个"
        assert set(targets) == {'09', '19', '29', '39', '49'}
        total = len(targets) * 20
        assert total == 100
        print(f"  [OK] 展开{len(targets)}个号码，每号20，总金额{total}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试10：混合输入
    print("\n[测试10] 混合输入：红单各50 虎各20 28各100 蓝波各30 0尾各10")
    try:
        instructions = parser.parse_input("红单各50\n虎各20\n28各100\n蓝波各30\n0尾各10")
        assert len(instructions) == 5
        print(f"  [OK] 识别{len(instructions)}条指令，组合玩法、生肖、号码混合正常")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试11：重复累计（01各100 + 红单各20 + 单各30 + 红波各40）
    print("\n[测试11] 重复累计：01各100 红单各20 单各30 红波各40")
    try:
        instructions = parser.parse_input("01各100\n红单各20\n单各30\n红波各40")
        # 统计01号的累计
        count_01 = 0
        for inst in instructions:
            if '01' in inst.targets or '1' in inst.targets:
                count_01 += inst.targets.count('01') + inst.targets.count('1')
        # 01号应该出现4次（01各100一次，红单包含01一次，单包含01一次，红波包含01一次）
        assert count_01 == 4, f"01号应出现4次，实际{count_01}次"
        print(f"  [OK] 01号出现{count_01}次，允许累计")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试12：各种标点符号
    print("\n[测试12] 标点符号测试")
    punctuation_tests = [
        ("红单，50", "逗号"),
        ("红单。50", "句号"),
        ("红单/50", "斜杠"),
        ("红单-50", "减号"),
        ("红单：50", "中文冒号"),
        ("红单=50", "等号"),
    ]
    punctuation_passed = 0
    for test_input, desc in punctuation_tests:
        try:
            instructions = parser.parse_input(test_input)
            assert len(instructions) == 1
            assert len(instructions[0].targets) == 8
            assert instructions[0].amount_integer == 50 * AMOUNT_MULTIPLIER
            punctuation_passed += 1
        except Exception as e:
            print(f"    [{desc}] FAIL: {e}")

    if punctuation_passed == len(punctuation_tests):
        print(f"  [OK] 所有{len(punctuation_tests)}种标点符号测试通过")
        passed += 1
    else:
        print(f"  [FAIL] 只通过{punctuation_passed}/{len(punctuation_tests)}个标点测试")
        failed += 1

    # 测试13：3尾不被误识别为号码03
    print("\n[测试13] 3尾各50（数字3属于玩法名称）")
    try:
        instructions = parser.parse_input("3尾各50")
        assert len(instructions) == 1
        targets = instructions[0].targets
        # 应该展开为03,13,23,33,43共5个号码
        assert len(targets) == 5, f"期望5个号码，实际{len(targets)}个"
        # 不应该额外包含号码03（除非是3尾展开的）
        print(f"  [OK] 3尾正确识别为玩法，展开{len(targets)}个号码")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 测试14：确认不包含大、小、合单、合双
    print("\n[测试14] 确认不包含大、小、合单、合双")
    try:
        from play_group_parser import PlayGroupsLoader
        loader = PlayGroupsLoader()
        play_names = loader.get_play_names()

        forbidden = ['大', '小', '合单', '合双']
        found_forbidden = [name for name in forbidden if name in play_names]

        assert len(found_forbidden) == 0, f"配置中包含禁止玩法: {found_forbidden}"
        print(f"  [OK] 配置文件不包含大、小、合单、合双")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1

    # 汇总
    print("\n" + "=" * 60)
    print(f"测试完成: {passed}个通过, {failed}个失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] 测试运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
