from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

# 在parse方法中添加调试
text = "0尾各20"
instructions = parser.parse_input(text)

print(f"最终指令数: {len(instructions)}")
print(f"targets: {instructions[0].targets}")
print(f"targets数量: {len(instructions[0].targets)}")
print(f"target_type: {instructions[0].target_type}")
