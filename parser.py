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
        """解析输入文本为指令列表 - 支持多条指令在同一行"""
        instructions = []
        lines = input_text.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            try:
                # 尝试分割同一行中的多条指令
                # 查找所有关键词位置（各、个、数等）
                sub_instructions = self._split_multi_instructions(line, line_num)
                instructions.extend(sub_instructions)
            except ParserError as e:
                raise ParserError(f"第{line_num}行错误: {e}")

        return instructions

    def _split_multi_instructions(self, line: str, line_num: int) -> List[Instruction]:
        """分割一行中的多条指令"""
        # 标准化
        normalized = self._normalize_punctuation(line)

        # 查找所有关键词位置
        keyword_positions = []
        for keyword in EACH_SYNONYMS + ['数']:
            pos = 0
            while True:
                pos = normalized.find(keyword, pos)
                if pos == -1:
                    break
                keyword_positions.append((pos, keyword))
                pos += len(keyword)

        if not keyword_positions:
            # 没有关键词，尝试传统解析
            return [self._parse_single_instruction(line, line_num)]

        # 按位置排序
        keyword_positions.sort(key=lambda x: x[0])

        # 根据关键词分割成多个片段
        instructions = []
        for i, (pos, keyword) in enumerate(keyword_positions):
            # 确定片段起始位置
            if i == 0:
                start = 0
            else:
                # 从上一个关键词后的数字结束位置开始
                prev_pos, prev_keyword = keyword_positions[i - 1]
                # 查找上一个关键词后的数字
                after_prev = normalized[prev_pos + len(prev_keyword):]
                num_match = re.match(r'\s*(\d+(?:\.\d+)?)', after_prev)
                if num_match:
                    start = prev_pos + len(prev_keyword) + len(num_match.group(0))
                else:
                    start = prev_pos + len(prev_keyword)

            # 确定片段结束位置（当前关键词+数字）
            after_keyword = normalized[pos + len(keyword):]
            num_match = re.match(r'\s*(\d+(?:\.\d+)?)', after_keyword)
            if num_match:
                end = pos + len(keyword) + len(num_match.group(0))
            else:
                end = pos + len(keyword)

            # 提取片段
            segment = normalized[start:end].strip()

            if segment:
                try:
                    instruction = self._parse_single_instruction(segment, line_num)
                    instructions.append(instruction)
                except ParserError:
                    # 忽略无法解析的片段
                    pass

        return instructions if instructions else [self._parse_single_instruction(line, line_num)]

    def _parse_single_instruction(self, line: str, line_num: int) -> Instruction:
        """解析单条指令 - 格式：目标+关键词+金额"""
        original = line

        # 标准化：全角转半角
        normalized = self._normalize_punctuation(line)

        # 查找关键词和金额
        # 匹配：关键词+金额（如"各50"、"数30"、"个0.50"）
        amount_match = None
        found_keyword = None

        for keyword in EACH_SYNONYMS + ['数']:
            # 查找：关键词后面跟着数字
            pattern = rf'{re.escape(keyword)}\s*(\d+(?:\.\d+)?)'
            match = re.search(pattern, normalized)
            if match:
                amount_match = match
                found_keyword = keyword
                break

        if not amount_match:
            raise ParserError(f"未找到金额: {line}")

        amount_str = amount_match.group(1)

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

        # 关键词之前的部分是目标
        target_part = normalized[:amount_match.start()].strip()

        # 移除常见的无关字符
        for char in ['号', '：', ':']:
            target_part = target_part.replace(char, ' ')

        target_part = ' '.join(target_part.split())

        if not target_part:
            raise ParserError(f"未找到目标: {line}")

        # 同时提取动物和号码
        animals_found = []
        for char in target_part:
            if char in self.animals:
                animals_found.append(char)

        # 提取号码（从目标部分提取所有数字）
        numbers_found = re.findall(r'\d+', target_part)
        numbers = []
        for num_str in numbers_found:
            try:
                num = int(num_str)
                if MIN_NUMBER <= num <= MAX_NUMBER:
                    numbers.append(str(num))
            except ValueError:
                pass

        # 合并动物和号码
        animals_unique = list(dict.fromkeys(animals_found))
        numbers_unique = list(dict.fromkeys(numbers))

        all_targets = []
        target_type = None

        if animals_unique and numbers_unique:
            # 混合模式
            all_targets = animals_unique + numbers_unique
            target_type = 'mixed'
        elif animals_unique:
            # 仅动物
            all_targets = animals_unique
            target_type = 'animal'
        elif numbers_unique:
            # 仅号码
            all_targets = numbers_unique
            target_type = 'number'
        else:
            raise ParserError(f"未找到有效目标: {line}")

        # 检查重复
        warning = None
        if len(animals_found) != len(animals_unique):
            duplicates = [a for a in set(animals_found) if animals_found.count(a) > 1]
            warning = f"重复动物: {', '.join(duplicates)}"
        if len(numbers_found) != len(numbers_unique):
            duplicates = [n for n in set(numbers_found) if numbers_found.count(n) > 1]
            if warning:
                warning += f"; 重复号码: {', '.join(duplicates)}"
            else:
                warning = f"重复号码: {', '.join(duplicates)}"

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
