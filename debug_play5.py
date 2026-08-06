import re
from constants import EACH_SYNONYMS

text = "0尾各20"
normalized = text

# 方案1：查找关键词和金额
amount_match = None
found_keyword = None
target_part = None

for keyword in EACH_SYNONYMS + ['数']:
    pattern = rf'{re.escape(keyword)}\s*(\d+(?:\.\d+)?)'
    match = re.search(pattern, normalized)
    if match:
        amount_match = match
        found_keyword = keyword
        # 关键词之前的部分是目标
        target_part = normalized[:amount_match.start()].strip()
        break

print(f"输入: {normalized}")
print(f"找到关键词: {found_keyword}")
print(f"金额匹配: {amount_match}")
print(f"target_part: '{target_part}'")
pattern = r'\d+'
all_nums = re.findall(pattern, normalized)
print(f"从normalized中提取所有数字: {all_nums}")
