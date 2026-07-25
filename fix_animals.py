import re

with open("parser.py", "r", encoding="utf-8") as f:
    content = f.read()

# 替换1: 移除 animals_unique = list(dict.fromkeys(animals_found))
# 替换2: 保持 numbers_unique = list(dict.fromkeys(numbers...))
# 替换3: 将 animals_unique 替换为 animals_found
# 替换4: 移除重复动物的警告检查

# 全局替换 animals_unique 为 animals_found
content = content.replace("animals_unique", "animals_found")

# 移除动物去重的行
content = re.sub(r'\s*animals_found = list\(dict\.fromkeys\(animals_found\)\)\n', '', content)

# 移除重复动物警告
pattern = r'if len\(animals_found\) != len\(animals_found\):.*?\n.*?"重复动物:.*?\n'
content = re.sub(pattern, '', content, flags=re.DOTALL)

with open("parser.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✓ 已修复动物去重问题")
