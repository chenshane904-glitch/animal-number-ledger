import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

test_cases = [
    "26-80",
    "26.80",
    "26/80",
    "26~80",
    "26 80",
    "14、15、16各80",
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
