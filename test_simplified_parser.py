import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

test_cases = [
    "02~40~19~31各50",
    "马狗马猴各50",
    "14-16各二十五",
]

for test in test_cases:
    print(f"输入: {test}")
    try:
        instructions = parser.parse_input(test)
        for inst in instructions:
            print(f"  目标: {inst.targets}")
            print(f"  金额: {inst.amount_integer / 100}")
    except Exception as e:
        print(f"  错误: {e}")
    print()
