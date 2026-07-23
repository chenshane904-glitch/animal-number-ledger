"""计算器测试"""
import unittest
from calculator import Calculator
from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING


class TestCalculator(unittest.TestCase):
    """计算器测试"""

    def setUp(self):
        """测试前准备"""
        self.parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)
        self.calculator = Calculator(DEFAULT_ANIMAL_MAPPING)

    def test_single_number_calculation(self):
        """测试单个号码计算"""
        instructions = self.parser.parse_input("1号10")
        result = self.calculator.calculate(instructions)
        self.assertEqual(result.number_amounts[1], 1000)
        self.assertEqual(result.total_amount, 1000)
        self.assertEqual(result.non_zero_count, 1)

    def test_multiple_numbers(self):
        """测试多个号码"""
        instructions = self.parser.parse_input("1、7、20各10")
        result = self.calculator.calculate(instructions)
        self.assertEqual(result.number_amounts[1], 1000)
        self.assertEqual(result.number_amounts[7], 1000)
        self.assertEqual(result.number_amounts[20], 1000)
        self.assertEqual(result.total_amount, 3000)

    def test_animal_calculation(self):
        """测试动物计算"""
        instructions = self.parser.parse_input("马各号10")
        result = self.calculator.calculate(instructions)
        # 马有5个号码：1、13、25、37、49
        horse_numbers = DEFAULT_ANIMAL_MAPPING['马']
        for num in horse_numbers:
            self.assertEqual(result.number_amounts[num], 1000)
        self.assertEqual(result.total_amount, 5000)
        self.assertEqual(result.non_zero_count, 5)

    def test_accumulation(self):
        """测试累加"""
        text = """1号10
1号5
1号3"""
        instructions = self.parser.parse_input(text)
        result = self.calculator.calculate(instructions)
        self.assertEqual(result.number_amounts[1], 1800)

    def test_sources(self):
        """测试来源记录"""
        text = """1号10
7号20
1号5"""
        instructions = self.parser.parse_input(text)
        result = self.calculator.calculate(instructions)
        self.assertEqual(len(result.sources[1]), 2)
        self.assertEqual(len(result.sources[7]), 1)


if __name__ == '__main__':
    unittest.main()
