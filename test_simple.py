import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

tests = [
    "1.2.3各 0.50",
    "123各 0.50", 
    "1 2 3各 0.50",
    "蛇鼠猴鸡各 75"
]

for i, test in enumerate(tests, 1):
    print(f"Test {i}: {test}")
    try:
        result = parser.parse_input(test)
        print(f"  OK: {result[0].target_type} {result[0].targets}")
    except Exception as e:
        print(f"  FAIL: {e}")
    print()
