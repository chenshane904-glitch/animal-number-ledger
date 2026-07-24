import sys
sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")

import re
from constants import DEFAULT_ANIMAL_MAPPING

# 测试输入
line = "蛇龙鼠兔 02.10.02.32.25.32.36.41.03各30斤"

print(f"原始输入: {line}")
print()

# 提取所有数字
all_numbers = re.findall(r'\d+\.?\d*', line)
print(f"提取的所有数字: {all_numbers}")
print()

# 最后一个是金额
if all_numbers:
    amount = all_numbers[-1]
    numbers = all_numbers[:-1]
    print(f"金额: {amount}")
    print(f"号码字符串: {numbers}")
    print()

# 提取动物
animals = DEFAULT_ANIMAL_MAPPING
animals_found = []
for char in line:
    if char in animals:
        animals_found.append(char)

print(f"识别的动物: {animals_found}")
print()

# 处理号码
valid_numbers = []
for num_str in numbers:
    clean = num_str.replace('.', '')
    if clean:
        try:
            num = int(clean)
            if 1 <= num <= 49:
                valid_numbers.append(num)
        except:
            pass

print(f"有效号码: {valid_numbers}")
