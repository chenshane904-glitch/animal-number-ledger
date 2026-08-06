import re
from play_group_parser import PlayGroupsLoader, PlayGroupParser

loader = PlayGroupsLoader()
play_parser = PlayGroupParser(loader)

# 模拟完整流程
target_part = "0尾"  # 金额之前的部分

print(f"1. 原始target_part: '{target_part}'")

# 提取玩法
play_groups_found = []
target_after_plays = target_part

plays = play_parser.extract_play_groups(target_part)
print(f"2. 识别到的玩法: {plays}")

if plays:
    for play_name, start, end in reversed(plays):
        numbers = play_parser.expand_play_group(play_name)
        print(f"3. 玩法'{play_name}'展开为: {numbers}")
        if numbers:
            play_groups_found.extend(numbers)
            print(f"4. 移除前target_after_plays: '{target_after_plays}'")
            target_after_plays = target_after_plays[:start] + target_after_plays[end:]
            print(f"5. 移除后target_after_plays: '{target_after_plays}'")
    
    target_part = target_after_plays.strip()
    print(f"6. strip后的target_part: '{target_part}'")

print(f"7. play_groups_found: {play_groups_found}")

# 提取普通号码
numbers_found = re.findall(r'\d+', target_part)
print(f"8. 从target_part提取的普通号码: {numbers_found}")

print(f"9. 最终all_targets应该是: {play_groups_found + numbers_found}")
