import sys
sys.path.insert(0, "C:/Users/2SS2/animal-number-ledger")

from parser import InstructionParser
from constants import DEFAULT_ANIMAL_MAPPING

parser = InstructionParser(DEFAULT_ANIMAL_MAPPING)

test_input = "1.2.3各0.50"
print(f"测试输入: {test_input}")
print()

try:
    # 测试解析
    instructions = parser.parse_input(test_input)
    print("✅ 解析成功！")
    print()
    for inst in instructions:
        print(f"目标类型: {inst.target_type}")
        print(f"目标: {inst.targets}")
        print(f"金额: {inst.amount}")
        print(f"是否各数: {inst.is_each}")
except Exception as e:
    print(f"❌ 解析失败: {e}")
    print()
    import traceback
    traceback.print_exc()
