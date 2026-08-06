from play_group_parser import PlayGroupsLoader, PlayGroupParser

loader = PlayGroupsLoader()
parser = PlayGroupParser(loader)

# 测试0尾
text1 = "0尾各20"
plays1 = parser.extract_play_groups(text1)
print(f"输入: {text1}")
print(f"识别到的玩法: {plays1}")
if plays1:
    numbers = parser.expand_play_group(plays1[0][0])
    print(f"展开号码: {numbers}")
print()

# 测试3尾
text2 = "3尾各50"
plays2 = parser.extract_play_groups(text2)
print(f"输入: {text2}")
print(f"识别到的玩法: {plays2}")
if plays2:
    numbers = parser.expand_play_group(plays2[0][0])
    print(f"展开号码: {numbers}")
