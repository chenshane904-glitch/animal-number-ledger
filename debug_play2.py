from play_group_parser import PlayGroupsLoader, PlayGroupParser
from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

loader = PlayGroupsLoader()
parser_play = PlayGroupParser(loader)
parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

# 测试0尾
text1 = "0尾各20"
print(f"=== 测试: {text1} ===")
plays1 = parser_play.extract_play_groups(text1)
print(f"玩法识别: {plays1}")

# 完整解析
try:
    instructions = parser.parse_input(text1)
    print(f"指令数量: {len(instructions)}")
    if instructions:
        print(f"目标数量: {len(instructions[0].targets)}")
        print(f"目标: {instructions[0].targets}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
