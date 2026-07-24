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
from models import Instruction


class ParserError(Exception):
    """解析错误"""
    pass


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
        """智能解析单行 - 同时支持数字和动物（混合）"""
        original = line

        # 标准化：全角转半角
        normalized = self._normalize_punctuation(line)

        # 先查找金额（最后一个可能带小数点的数字）
        # 从后往前找第一个数字序列（可能是 "30" 或 "0.50"）
        amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:斤|元|块|￥|\$)?$', normalized)
        if not amount_match:
            raise ParserError(f"未找到金额: {line}")

        amount_str = amount_match.group(1)

        # 移除金额部分，剩余部分提取所有单独的数字
        content_before_amount = normalized[:amount_match.start()].strip()

        # 提取所有单独的数字（不匹配小数）
        all_numbers = re.findall(r'\d+', content_before_amount)

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

        # 移除金额部分，剩余部分尝试识别号码和动物
        amount_pos = normalized.rfind(amount_str)
        target_part = normalized[:amount_pos].strip()

        # 移除常见的关键词
        for keyword in EACH_SYNONYMS + ['元', '￥', '$', '号', '数', '斤']:
            target_part = target_part.replace(keyword, ' ')

        # 清理空白
        target_part = ' '.join(target_part.split())

        # 同时提取动物和号码
        animals_found = []
        for char in target_part:
            if char in self.animals:
                animals_found.append(char)

        # 提取号码（除去金额的其他数字）
        number_strings = all_numbers[:-1]
        numbers = []
        for num_str in number_strings:
            # 移除小数点
            num_str = num_str.replace('.', '')
            if not num_str:
                continue
            try:
                num = int(num_str)
                if MIN_NUMBER <= num <= MAX_NUMBER:
                    numbers.append(str(num))
            except ValueError:
                pass

        # 合并动物和号码
        all_targets = []
        target_type = None

        # 去重但保持顺序
        animals_unique = list(dict.fromkeys(animals_found))
        numbers_unique = list(dict.fromkeys(numbers))

        if animals_unique and numbers_unique:
            # 同时有动物和号码：合并
            all_targets = animals_unique + numbers_unique
            target_type = 'mixed'  # 混合类型
        elif animals_unique:
            # 只有动物
            all_targets = animals_unique
            target_type = 'animal'
        elif numbers_unique:
            # 只有号码
            all_targets = numbers_unique
            target_type = 'number'
        else:
            raise ParserError(f"未找到号码或动物: {line}")

        # 检查重复
        warning = None
        if animals_found and len(animals_found) != len(animals_unique):
            duplicates = [a for a in set(animals_found) if animals_found.count(a) > 1]
            warning = f"重复动物: {', '.join(duplicates)}"
        if numbers and len(numbers) != len(numbers_unique):
            duplicates = [n for n in set(numbers) if numbers.count(n) > 1]
            if warning:
                warning += f"; 重复号码: {', '.join(duplicates)}"
            else:
                warning = f"重复号码: {', '.join(duplicates)}"

        # 检测是否是"各数"模式
        is_each = any(keyword in normalized for keyword in EACH_SYNONYMS) or len(all_targets) > 1

        # 创建指令
        instruction = Instruction(
            source_line=line_num,
            original_text=original,
            normalized_text=normalized,
            target_type=target_type,
            targets=all_targets,
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
