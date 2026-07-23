"""测试解析器"""
from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

# 创建解析器
parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

# 测试输入
test_inputs = [
    "01.32.45.41.01.01各30斤",
    "01.32.45.41.01.01各30",
    "1,32,45,41,1各30",
]

for test in test_inputs:
    print(f"\n测试输入: {test}")
    try:
        instructions = parser.parse_input(test)
        for inst in instructions:
            print(f"  ✓ 成功: {inst.targets} -> {inst.amount_integer / 100:.2f}")
    except Exception as e:
        print(f"  ✗ 错误: {e}")
