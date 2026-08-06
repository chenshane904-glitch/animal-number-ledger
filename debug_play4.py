text = "0尾各20"
target_part = "0尾"  # 金额之前的部分

# 模拟移除玩法
play_name = "0尾"
start = 0
end = 2
target_after_plays = target_part[:start] + target_part[end:]
print(f"原始target_part: '{target_part}'")
print(f"移除'{play_name}'后: '{target_after_plays}'")
print(f"strip后: '{target_after_plays.strip()}'")

# 提取普通号码
import re
numbers_found = re.findall(r'\d+', target_after_plays.strip())
print(f"提取到的普通号码: {numbers_found}")
