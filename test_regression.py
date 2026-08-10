# -*- coding: utf-8 -*-
"""
完整回归测试套件
包含所有业务场景的真实测试
"""

import sys
import os
from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING


class RegressionTestSuite:
    """回归测试套件"""

    def __init__(self):
        self.parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)
        self.passed = 0
        self.failed = 0
        self.results = []

    def test(self, name, func):
        """运行单个测试"""
        print(f"\n[测试] {name}")
        try:
            func()
            self.passed += 1
            self.results.append((name, "PASS", None))
            print("  PASS")
        except AssertionError as e:
            self.failed += 1
            self.results.append((name, "FAIL", str(e)))
            print(f"  FAIL: {e}")
        except Exception as e:
            self.failed += 1
            self.results.append((name, "ERROR", str(e)))
            print(f"  ERROR: {e}")

    def test_1_head_20(self):
        """测试1: 1头20 - 必须按头数规则，不能按号码1"""
        result = self.parser.parse_input("1头20")
        assert len(result) == 1, "应返回1个指令"

        targets = [int(n) for n in result[0].targets]
        expected = list(range(10, 20))

        print(f"  输入: 1头20")
        print(f"  结果: {targets}")

        assert targets == expected, f"应该是10-19，不是号码1"
        assert result[0].amount_integer == 2000, "金额应该是2000"

    def test_2_head_20(self):
        """测试2: 2头20"""
        result = self.parser.parse_input("2头20")
        targets = [int(n) for n in result[0].targets]
        expected = list(range(20, 30))

        print(f"  输入: 2头20")
        print(f"  结果: {targets}")

        assert targets == expected, f"应该是20-29"

    def test_3_head_20(self):
        """测试3: 3头20"""
        result = self.parser.parse_input("3头20")
        targets = [int(n) for n in result[0].targets]
        expected = list(range(30, 40))

        print(f"  输入: 3头20")
        print(f"  结果: {targets}")

        assert targets == expected, f"应该是30-39"

    def test_4_head_20(self):
        """测试4: 4头20"""
        result = self.parser.parse_input("4头20")
        targets = [int(n) for n in result[0].targets]
        expected = list(range(40, 50))

        print(f"  输入: 4头20")
        print(f"  结果: {targets}")

        assert targets == expected, f"应该是40-49"

    def test_real_number_list_1(self):
        """测试5: 真实号码列表 - 禁止自动展开"""
        input_text = "07-19-27-06-18-30-34-46-22-40-23-35-08-40-24-12-38-44各250"
        result = self.parser.parse_input(input_text)

        targets = result[0].targets

        print(f"  输入: {input_text}")
        print(f"  结果: {len(targets)}个号码")

        # 禁止出现的号码
        forbidden = ['09', '10', '11', '13', '14', '15', '16', '17']
        for num in forbidden:
            assert num not in targets, f"不应该出现号码 {num} (自动展开)"

        # 必须包含的号码
        required = ['07', '19', '27', '06', '18', '30', '34', '46', '22', '40', '23', '35', '08', '24', '12', '38', '44']
        for num in required:
            assert num in targets, f"缺少号码 {num}"

    def test_real_number_list_2(self):
        """测试6: 30-40-34-23-08-07各250 - 只能是这些号码"""
        input_text = "30-40-34-23-08-07各250"
        result = self.parser.parse_input(input_text)

        targets = result[0].targets
        expected = ['30', '40', '34', '23', '08', '07']

        print(f"  输入: {input_text}")
        print(f"  结果: {targets}")

        # 禁止扩展
        forbidden = ['31', '32', '33', '35', '36', '37', '38', '39']
        for num in forbidden:
            assert num not in targets, f"不应该出现号码 {num} (自动扩展)"

        # 检查必需号码
        for num in expected:
            assert num in targets, f"缺少号码 {num}"

    def test_18_1300(self):
        """测试7: 18-1300 - 必须是号码18金额1300，不是范围"""
        input_text = "18-1300"
        result = self.parser.parse_input(input_text)

        targets = result[0].targets
        amount = result[0].amount_integer

        print(f"  输入: {input_text}")
        print(f"  结果: {targets}")
        print(f"  金额: {amount}")

        # 应该只有号码18
        assert '18' in targets, "应该包含号码18"

        # 不应该有1300号码（超出范围）
        assert '1300' not in targets, "不应该有号码1300"

        # 金额应该是1300
        assert amount == 130000, f"金额应该是130000，实际: {amount}"

    def test_blue_even_200(self):
        """测试8: 蓝波双200 - 蓝色+双数组合"""
        input_text = "蓝波双200"
        result = self.parser.parse_input(input_text)

        targets = [int(n) for n in result[0].targets]
        amount = result[0].amount_integer

        print(f"  输入: {input_text}")
        print(f"  结果: {targets}")
        print(f"  金额: {amount / 100}")

        # 验证蓝波
        blue_nums = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
        for num in targets:
            assert num in blue_nums, f"{num} 不是蓝波"

        # 验证双数
        for num in targets:
            assert num % 2 == 0, f"{num} 不是双数"

        # 验证金额
        assert amount == 20000, f"金额错误"

    def test_red_big_100(self):
        """测试9: 红波大100"""
        input_text = "红波大100"
        result = self.parser.parse_input(input_text)

        targets = [int(n) for n in result[0].targets]

        print(f"  输入: {input_text}")
        print(f"  结果: {targets}")

        red_nums = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
        for num in targets:
            assert num in red_nums, f"{num} 不是红波"
            assert num > 24, f"{num} 不是大号"

    def test_simple_numbers(self):
        """测试10: 普通号码 20 50"""
        input_text = "20 50"
        result = self.parser.parse_input(input_text)

        print(f"  输入: {input_text}")
        print(f"  结果: {result[0].targets}")

        assert '20' in result[0].targets, "应该包含号码20"

    def run_all(self):
        """运行所有测试"""
        print("="*60)
        print("完整回归测试套件")
        print("="*60)

        tests = [
            ("1头20 (头数规则)", self.test_1_head_20),
            ("2头20", self.test_2_head_20),
            ("3头20", self.test_3_head_20),
            ("4头20", self.test_4_head_20),
            ("真实号码列表1 (禁止展开)", self.test_real_number_list_1),
            ("真实号码列表2 (30-40-34...)", self.test_real_number_list_2),
            ("18-1300 (号码+金额)", self.test_18_1300),
            ("蓝波双200", self.test_blue_even_200),
            ("红波大100", self.test_red_big_100),
            ("普通号码", self.test_simple_numbers),
        ]

        for name, func in tests:
            self.test(name, func)

        self.print_report()
        return self.failed == 0

    def print_report(self):
        """打印测试报告"""
        print("\n" + "="*60)
        print("回归测试报告")
        print("="*60)
        print(f"\n总数: {self.passed + self.failed}")
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")

        if self.failed > 0:
            print("\n失败的测试:")
            for name, status, error in self.results:
                if status != "PASS":
                    print(f"  - {name}: {error}")

        print("\n" + "="*60)


if __name__ == '__main__':
    suite = RegressionTestSuite()
    success = suite.run_all()
    sys.exit(0 if success else 1)
