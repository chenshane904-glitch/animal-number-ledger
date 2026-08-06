# -*- coding: utf-8 -*-
"""
平特一肖解析器兼容性测试
"""
from flat_zodiac_parser import FlatZodiacParser


def test_parser():
    parser = FlatZodiacParser()

    print("="*70)
    print("平特一肖解析器兼容性测试")
    print("="*70)

    # 测试用例
    test_cases = [
        # (输入, 预期生肖, 预期金额, 描述)
        ("虎100", "虎", 100, "基本格式"),
        ("虎 100", "虎", 100, "带空格"),
        ("虎各100", "虎", 100, "带各字"),
        ("平特虎100", "虎", 100, "平特前缀"),
        ("平特虎各100", "虎", 100, "平特+各"),
        ("平特一肖虎100", "虎", 100, "平特一肖前缀"),
        ("平特肖虎100", "虎", 100, "平特肖前缀"),
        ("龙200", "龙", 200, "基本格式-龙"),
        ("平特龙200", "龙", 200, "平特前缀-龙"),
    ]

    passed = 0
    failed = 0

    for input_text, expected_zodiac, expected_amount, desc in test_cases:
        try:
            entries = parser.parse(input_text)
            if len(entries) == 1:
                entry = entries[0]
                if entry.zodiac == expected_zodiac and entry.amount == expected_amount:
                    print(f"[PASS] {desc}: '{input_text}' -> {entry.zodiac} {entry.amount}")
                    passed += 1
                else:
                    print(f"[FAIL] {desc}: '{input_text}' -> 预期 {expected_zodiac} {expected_amount}, 实际 {entry.zodiac} {entry.amount}")
                    failed += 1
            else:
                print(f"[FAIL] {desc}: '{input_text}' -> 预期1条，实际{len(entries)}条")
                failed += 1
        except Exception as e:
            print(f"[FAIL] {desc}: '{input_text}' -> 错误: {e}")
            failed += 1

    # 测试组合输入
    print("\n" + "="*70)
    print("组合输入测试")
    print("="*70)

    combo_tests = [
        ("虎100,龙200", [("虎", 100), ("龙", 200)], "逗号分隔"),
        ("平特虎100，平特龙200", [("虎", 100), ("龙", 200)], "平特前缀+中文逗号"),
        ("虎100\n龙200", [("虎", 100), ("龙", 200)], "换行分隔"),
    ]

    for input_text, expected_list, desc in combo_tests:
        try:
            entries = parser.parse(input_text)
            if len(entries) == len(expected_list):
                all_match = True
                for i, (exp_zodiac, exp_amount) in enumerate(expected_list):
                    if entries[i].zodiac != exp_zodiac or entries[i].amount != exp_amount:
                        all_match = False
                        break

                if all_match:
                    result = ", ".join([f"{e.zodiac}{e.amount}" for e in entries])
                    print(f"[PASS] {desc}: -> {result}")
                    passed += 1
                else:
                    print(f"[FAIL] {desc}: 解析结果不匹配")
                    failed += 1
            else:
                print(f"[FAIL] {desc}: 预期{len(expected_list)}条，实际{len(entries)}条")
                failed += 1
        except Exception as e:
            print(f"[FAIL] {desc}: 错误: {e}")
            failed += 1

    # 测试错误情况
    print("\n" + "="*70)
    print("错误处理测试")
    print("="*70)

    error_tests = [
        ("虎", "缺少金额"),
        ("平特虎", "缺少金额"),
        ("02各100", "不支持号码"),
        ("abc100", "无法识别"),
        ("   ", "输入"),  # 空白输入
    ]

    for input_text, expected_error_keyword in error_tests:
        try:
            entries = parser.parse(input_text)
            print(f"[FAIL] '{input_text}' 应该报错但成功了: {len(entries)}条")
            failed += 1
        except ValueError as e:
            if expected_error_keyword in str(e):
                print(f"[PASS] '{input_text}' -> 正确报错: {e}")
                passed += 1
            else:
                print(f"[FAIL] '{input_text}' -> 错误信息不符: {e}")
                failed += 1
        except Exception as e:
            print(f"[FAIL] '{input_text}' -> 意外错误: {e}")
            failed += 1

    # 测试不展开号码
    print("\n" + "="*70)
    print("不展开号码测试")
    print("="*70)

    try:
        entries = parser.parse("平特虎100")
        if len(entries) == 1 and entries[0].zodiac == "虎":
            print(f"[PASS] 平特虎100 不展开号码，只返回1条记录（虎）")
            passed += 1
        else:
            print(f"[FAIL] 平特虎100 错误展开，返回{len(entries)}条")
            failed += 1
    except Exception as e:
        print(f"[FAIL] 平特虎100 错误: {e}")
        failed += 1

    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")

    if failed == 0:
        print("\n[PASS] 所有测试通过")
        return True
    else:
        print(f"\n[FAIL] {failed} 个测试失败")
        return False


if __name__ == "__main__":
    success = test_parser()
    exit(0 if success else 1)
