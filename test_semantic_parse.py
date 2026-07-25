import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

import re

# 测试用例
test_cases = [
    "鼠豹50马名30",
    "鼠豹数50马名数30",
    "05.09.30各8",
    "05-09-30=8",
]

# 关键词
keywords = ['各', '个', '数', '=', '：', ':']

for test in test_cases:
    print(f"\n输入: {test}")
    
    # 查找所有关键词+金额
    pattern = r'(' + '|'.join(re.escape(k) for k in keywords) + r')\s*(\d+(?:\.\d+)?)'
    matches = list(re.finditer(pattern, test))
    
    print(f"找到 {len(matches)} 个指令")
    
    for i, match in enumerate(matches):
        keyword = match.group(1)
        amount = match.group(2)
        
        if i == 0:
            target_start = 0
        else:
            target_start = matches[i-1].end()
        
        target_part = test[target_start:match.start()].strip()
        
        # 提取号码
        numbers = re.findall(r'\d+', target_part)
        
        print(f"  指令{i+1}: 目标={target_part}, 号码={numbers}, 金额={amount}")
