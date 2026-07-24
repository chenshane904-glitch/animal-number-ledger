import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

import re

# 测试新的解析逻辑
line = "蛇龙鼠兔 02.10.02.32.25.32.36.41.03各30斤"

print(f"测试输入: {line}")
print()

# 先找金额
amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:斤|元|块|￥|\$)?$', line)
if amount_match:
    amount_str = amount_match.group(1)
    print(f"金额: {amount_str}")
    
    # 剩余部分提取号码
    content_before = line[:amount_match.start()].strip()
    print(f"内容部分: {content_before}")
    
    # 提取所有数字
    numbers = re.findall(r'\d+', content_before)
    print(f"提取的号码: {numbers}")
    print()
    
    # 过滤1-49范围
    valid = [n for n in numbers if 1 <= int(n) <= 49]
    print(f"有效号码(1-49): {valid}")
