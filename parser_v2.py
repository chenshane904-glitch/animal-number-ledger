# -*- coding: utf-8 -*-
"""
解析器 v2.0
统一的号码解析引擎
"""

import re
from typing import List, Tuple
from decimal import Decimal, InvalidOperation
from models import Instruction
from rule_analyzer import get_rule_analyzer
from number_filter_engine import get_filter_engine
from constants import MIN_NUMBER, MAX_NUMBER, AMOUNT_MULTIPLIER, MAX_AMOUNT_INTEGER


class ParserV2:
    """解析器 v2.0"""

    def __init__(self):
        self.rule_analyzer = get_rule_analyzer()
        self.filter_engine = get_filter_engine()

    def parse(self, text: str) -> List[Instruction]:
        """
        解析输入文本

        Args:
            text: 输入文本

        Returns:
            指令列表
        """
        text = text.strip()
        if not text:
            return []

        # 步骤1: 尝试规则分析（颜色、头数、尾数等）
        conditions, amount_integer, remaining = self.rule_analyzer.analyze(text)

        # 如果有条件且有金额，使用规则过滤
        if conditions and amount_integer is not None:
            numbers = self.filter_engine.filter_numbers(conditions)
            if numbers:
                instruction = Instruction(
                    source_line=1,
                    original_text=text,
                    normalized_text=text,
                    target_type='number',
                    targets=[str(num) for num in numbers],
                    amount_integer=amount_integer,
                    warning=None
                )
                return [instruction]

        # 步骤2: 尝试解析为普通号码列表
        # 识别分隔符: 各、个、- 等
        # 禁止自动范围展开！
        number_instruction = self._parse_number_list(text)
        if number_instruction:
            return [number_instruction]

        return []

    def _parse_number_list(self, text: str) -> Instruction:
        """
        解析普通号码列表

        例如: "07-19-27-06-18各250" → [07, 19, 27, 06, 18] 金额250
        注意: - 是分隔符，不是范围符号！
        """
        # 查找金额关键词和金额
        amount_keywords = ['各', '个', '数', '=', '：', ':']
        amount_integer = None
        number_part = text

        for keyword in amount_keywords:
            if keyword in text:
                parts = text.split(keyword, 1)
                if len(parts) == 2:
                    number_part = parts[0].strip()
                    amount_str = parts[1].strip()
                    # 提取数字
                    amount_match = re.search(r'(\d+(?:\.\d+)?)', amount_str)
                    if amount_match:
                        try:
                            amount = Decimal(amount_match.group(1))
                            amount_integer = int(amount * AMOUNT_MULTIPLIER)
                            break
                        except (InvalidOperation, ValueError):
                            continue

        if amount_integer is None:
            return None

        # 提取号码：使用多种分隔符
        # 分隔符: 空格, 逗号, 中文逗号, -, /
        separators = r'[\s,，\-/]+'
        number_strs = re.split(separators, number_part)

        numbers = []
        for num_str in number_strs:
            num_str = num_str.strip()
            if not num_str:
                continue
            try:
                num = int(num_str)
                if MIN_NUMBER <= num <= MAX_NUMBER:
                    numbers.append(str(num).zfill(2))  # 补零：7 → 07
            except ValueError:
                continue

        if not numbers:
            return None

        return Instruction(
            source_line=1,
            original_text=text,
            normalized_text=text,
            target_type='number',
            targets=numbers,
            amount_integer=amount_integer,
            warning=None
        )

    def parse_batch(self, text: str) -> List[Instruction]:
        """
        批量解析（支持多行）

        Args:
            text: 多行输入

        Returns:
            所有指令列表
        """
        instructions = []
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 解析每一行
            line_instructions = self.parse(line)
            instructions.extend(line_instructions)

        return instructions


# 全局实例
_parser_v2 = ParserV2()


def get_parser_v2() -> ParserV2:
    """获取解析器v2实例"""
    return _parser_v2
