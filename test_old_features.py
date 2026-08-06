from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

print("测试旧功能...")

# 测试1: 普通号码
instructions = parser.parse_input("01各50\n02各30")
assert len(instructions) == 2
print("[OK] 普通号码识别")

# 测试2: 动物识别
instructions = parser.parse_input("龙各20")
assert len(instructions) == 1
print("[OK] 动物识别")

# 测试3: 混合输入
instructions = parser.parse_input("龙各20\n01各30")
assert len(instructions) == 2
print("[OK] 混合输入")

print("\n所有旧功能测试通过")
