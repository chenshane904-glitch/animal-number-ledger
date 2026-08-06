# -*- coding: utf-8 -*-
"""
平特一肖模式解析器 - 不展开号码
"""

from models import Instruction


class FlatZodiacParser:
    """平特一肖解析器 - 只识别生肖名称，不展开成号码"""

    def __init__(self):
        self.animals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

    def parse_input(self, raw_input: str) -> list:
        """
        解析平特一肖输入

        支持格式：
        - 虎100
        - 平特一肖100
        - 龙200

        Returns:
            list[Instruction]: 指令列表
        """
        if not raw_input or not raw_input.strip():
            return []

        lines = raw_input.strip().split('\n')
        instructions = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # 移除"平特一肖"前缀
            if line.startswith("平特一肖"):
                line = line[4:].strip()

            # 尝试识别生肖和金额
            animal = None
            amount_str = None

            # 遍历生肖名称
            for zodiac in self.animals:
                if line.startswith(zodiac):
                    animal = zodiac
                    amount_str = line[len(zodiac):].strip()
                    break

            if not animal:
                # 如果没有识别到生肖，跳过这一行
                continue

            # 解析金额
            try:
                # 移除"各"字
                amount_str = amount_str.replace("各", "").strip()
                amount = float(amount_str)
                amount_integer = int(amount * 100)
            except (ValueError, AttributeError):
                continue

            # 创建指令
            instruction = Instruction(
                source_line=line_num,
                target_type='animal',  # 平特模式的目标类型是animal
                targets=[animal],
                amount_integer=amount_integer,
                original_text=line,
                normalized_text=f"{animal}{amount}"
            )
            instructions.append(instruction)

        return instructions
