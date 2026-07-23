"""解析器测试"""
import unittest
from parser import InstructionParser, ParserError
from constants import DEFAULT_ANIMAL_MAPPING


class TestParser(unittest.TestCase):
    """解析器测试"""

    def setUp(self):
        """测试前准备"""
        self.parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

    def test_single_number(self):
        """测试单个号码"""
        instructions = self.parser.parse_input("1号13斤")
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].target_type, 'number')
        self.assertEqual(instructions[0].targets, ['1'])
        self.assertEqual(instructions[0].amount_integer, 1300)

    def test_multiple_numbers_with_each(self):
        """测试多个号码（带各）"""
        instructions = self.parser.parse_input("1、7、20、49各13")
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].target_type, 'number')
        self.assertEqual(set(instructions[0].targets), {'1', '7', '20', '49'})
        self.assertEqual(instructions[0].amount_integer, 1300)

    def test_animal_each(self):
        """测试动物各号"""
        instructions = self.parser.parse_input("龙各号20")
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].target_type, 'animal')
        self.assertEqual(instructions[0].targets, ['龙'])
        self.assertEqual(instructions[0].amount_integer, 2000)

    def test_multiple_animals(self):
        """测试多个动物"""
        instructions = self.parser.parse_input("龙、牛各数20")
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0].target_type, 'animal')
        self.assertEqual(set(instructions[0].targets), {'龙', '牛'})
        self.assertEqual(instructions[0].amount_integer, 2000)

    def test_decimal_amount(self):
        """测试小数金额"""
        instructions = self.parser.parse_input("1号0.50")
        self.assertEqual(instructions[0].amount_integer, 50)

    def test_decimal_amount_is_exact(self):
        """测试容易触发二进制浮点误差的小数"""
        cases = {
            "1号0.29": 29,
            "1号1.15": 115,
            "1号2.30": 230,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                instruction = self.parser.parse_input(text)[0]
                self.assertEqual(instruction.amount_integer, expected)

    def test_more_than_two_decimal_places_error(self):
        """金额最多支持两位小数"""
        with self.assertRaises(ParserError):
            self.parser.parse_input("1号1.005")

    def test_amount_overflow_error(self):
        """超出SQLite整数范围的金额必须拒绝"""
        with self.assertRaises(ParserError):
            self.parser.parse_input("1号999999999999999999999999")

    def test_multiline(self):
        """测试多行输入"""
        text = """1号13
7号20
龙各号15"""
        instructions = self.parser.parse_input(text)
        self.assertEqual(len(instructions), 3)

    def test_duplicate_warning(self):
        """测试同行重复警告"""
        instructions = self.parser.parse_input("1、1、7各10")
        self.assertEqual(len(instructions), 1)
        self.assertIsNotNone(instructions[0].warning)
        self.assertEqual(set(instructions[0].targets), {'1', '7'})

    def test_mixed_error(self):
        """测试混合错误"""
        with self.assertRaises(ParserError):
            self.parser.parse_input("1、龙各10")

    def test_no_amount_error(self):
        """测试缺少金额错误"""
        with self.assertRaises(ParserError):
            self.parser.parse_input("1号")

    def test_invalid_number_error(self):
        """测试无效号码错误"""
        with self.assertRaises(ParserError):
            self.parser.parse_input("50号10")

    def test_multiple_without_each_error(self):
        """测试多个目标未使用各号错误"""
        with self.assertRaises(ParserError):
            self.parser.parse_input("1、7、20 13")


if __name__ == '__main__':
    unittest.main()
