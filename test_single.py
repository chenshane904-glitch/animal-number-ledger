from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)
instructions = parser.parse_input("0尾各20")
print(f"指令数: {len(instructions)}")
print(f"targets: {instructions[0].targets}")
