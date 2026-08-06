from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

text = "0尾各20"
print(f"原始输入: {text}")

# 标准化
normalized = parser._normalize_punctuation(text)
print(f"标准化后: {normalized}")

# 提取玩法
plays = parser.play_parser.extract_play_groups(normalized)
print(f"识别到的玩法: {plays}")

if plays:
    for play_name, start, end in plays:
        print(f"  玩法名称: {play_name}")
        print(f"  位置: {start}-{end}")
        numbers = parser.play_parser.expand_play_group(play_name)
        print(f"  展开号码: {numbers}")
        print(f"  号码数量: {len(numbers)}")

# 完整解析
instructions = parser.parse_input(text)
print(f"\n最终结果:")
print(f"  指令数: {len(instructions)}")
print(f"  目标: {instructions[0].targets}")
print(f"  目标数量: {len(instructions[0].targets)}")
