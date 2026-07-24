# -*- coding: utf-8 -*-
"""
智能解析器 - 提取任意格式的号码和金额
"""

import re
from decimal import Decimal, InvalidOperation
from typing import List, Tuple
from constants import (
    MIN_NUMBER, MAX_NUMBER,
    AMOUNT_MULTIPLIER, MAX_AMOUNT_INTEGER,
    EACH_SYNONYMS, DEFAULT_ANIMAL_MAPPING
)
from models import Instruction, ParserError


class InstructionParser:
    """智能指令解析器"""

    def __init__(self, animals: dict):
        self.animals = animals

    def parse_input(self, input_text: str) -> List[Instruction]:
        """解析输入文本为指令列表"""
        instructions = []
        lines = input_text.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            try:
                instruction = self._parse_line(line, line_num)
                instructions.append(instruction)
            except ParserError as e:
                raise ParserError(f"第{line_num}行错误: {e}")

        return instructions

    def _parse_line(self, line: str, line_num: int) -> Instruction:
        """智能解析单行 - 提取所有数字，最后一个作为金额"""
        original = line

        # 标准化：全角转半角
        normalized = self._normalize_punctuation(line)

        # 提取所有数字（包括小数）
        # 匹配模式：整数或小数
        all_numbers = re.findall(r'\d+\.?\d*', normalized)

        if not all_numbers:
            raise ParserError(f"未找到任何数字: {line}")

        # 最后一个数字作为金额
        amount_str = all_numbers[-1]

        # 其余数字作为号码
        number_strings = all_numbers[:-1]

        if not number_strings:
            raise ParserError(f"未找到号码（只有金额）: {line}")

        # 解析金额
        try:
            amount = Decimal(amount_str)
            if amount < 0:
                raise ParserError(f"金额不能为负数: {amount_str}")
            amount_integer = int(amount * AMOUNT_MULTIPLIER)
            if amount_integer > MAX_AMOUNT_INTEGER:
                raise ParserError(f"金额超出可存储范围: {amount_str}")
        except (InvalidOperation, ValueError):
            raise ParserError(f"无效的金额格式: {amount_str}")

        # 解析号码
        numbers = []
        for num_str in number_strings:
            # 移除小数点（号码不应该有小数）
            num_str = num_str.replace('.', '')

            if not num_str:
                continue

            try:
                num = int(num_str)
                if MIN_NUMBER <= num <= MAX_NUMBER:
                    numbers.append(str(num))
                # 号码超出范围，忽略（宽容处理）
            except ValueError:
                # 无法转换为整数，忽略
                pass

        if not numbers:
            raise ParserError(f"未找到有效号码（1-49范围内）: {line}")

        # 检查重复
        warning = None
        if len(numbers) != len(set(numbers)):
            seen = set()
            duplicates = []
            for n in numbers:
                if n in seen:
                    duplicates.append(n)
                seen.add(n)
            warning = f"同一行重复号码: {', '.join(duplicates)}"
            numbers = list(dict.fromkeys(numbers))  # 去重但保持顺序

        # 检测是否是"各数"模式
        is_each = any(keyword in normalized for keyword in EACH_SYNONYMS) or len(numbers) > 1

        # 创建指令
        instruction = Instruction(
            source_line=line_num,
            original_text=original,
            normalized_text=normalized,
            target_type='number',
            targets=numbers,
            amount_integer=amount_integer,
            warning=warning
        )

        return instruction

    def _normalize_punctuation(self, text: str) -> str:
        """标准化标点符号，将全角字符转换为半角"""
        # 全角数字转半角
        for i in range(10):
            text = text.replace(chr(0xFF10 + i), str(i))

        # 全角小数点转半角
        text = text.replace('．', '.')

        return text
