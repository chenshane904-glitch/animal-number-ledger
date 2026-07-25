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

    def _chinese_to_number(self, text: str) -> str:
        """转换中文数字为阿拉伯数字"""
        # 中文数字映射
        chinese_map = {
            '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
            '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
            '十': '10', '百': '100'
        }

        # 常见组合
        combinations = {
            '十': '10',
            '二十': '20', '二十五': '25', '三十': '30',
            '四十': '40', '五十': '50', '六十': '60',
            '七十': '70', '八十': '80', '九十': '90',
            '一百': '100', '二百': '200', '三百': '300',
            '四百': '400', '五百': '500'
        }

        result = text
        # 先替换组合（长的先替换）
        for cn, num in sorted(combinations.items(), key=lambda x: -len(x[0])):
            result = result.replace(cn, num)

        # 再替换单个字符
        for cn, num in chinese_map.items():
            result = result.replace(cn, num)

        return result

    def _expand_range(self, text: str) -> str:
        """展开数字范围 14-16 -> 14,15,16"""
        # 查找所有范围模式：数字-数字
        pattern = r'(\d+)-(\d+)'

        def replace_range(match):
            start = int(match.group(1))
            end = int(match.group(2))
            if start < end and end - start <= 50:  # 限制范围，避免异常大的范围
                return ','.join(str(i) for i in range(start, end + 1))
            return match.group(0)  # 保持原样

        return re.sub(pattern, replace_range, text)

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
        """分割一行中的多条指令 - 智能语义解析"""
        # 标准化
        normalized = self._normalize_punctuation(line)

        # 定义所有可能的关键词分隔符
        keywords = EACH_SYNONYMS + ['数', '=', '：', ':']

        # 方案1: 查找所有 "关键词+金额" 组合
        pattern = r'(' + '|'.join(re.escape(k) for k in keywords) + r')\s*(\d+(?:\.\d+)?)'
        matches = list(re.finditer(pattern, normalized))

        if matches:
            # 有关键词，使用关键词分割
            return self._parse_with_keywords(line, line_num, normalized, matches)

        # 方案2: 没有关键词，尝试识别 "目标+数字" 模式
        # 查找所有独立的数字（可能是金额）
        # 模式：非数字 + 数字 + 非数字（或结尾）
        number_pattern = r'(?<!\d)(\d+(?:\.\d+)?)(?!\d)'
        number_matches = list(re.finditer(number_pattern, normalized))

        if len(number_matches) >= 2:
            # 有多个数字，可能是多条指令
            # 尝试将每个数字作为金额，前面的内容作为目标
            return self._parse_without_keywords(line, line_num, normalized, number_matches)

        # 方案3: 传统单条指令解析
        return [self._parse_single_instruction(line, line_num)]

    def _parse_without_keywords(self, line: str, line_num: int, normalized: str, number_matches: List) -> List[Instruction]:
        """解析没有关键词的格式：鼠豹50马名30"""
        instructions = []

        for i, match in enumerate(number_matches):
            amount_str = match.group(1)
            amount_end = match.end()

            # 确定目标部分的起始位置
            if i == 0:
                target_start = 0
            else:
                # 从上一个金额结束位置开始
                target_start = number_matches[i - 1].end()

            # 目标部分：从起始到当前数字之前
            target_part = normalized[target_start:match.start()].strip()

            if not target_part:
                continue

            # 解析金额
            try:
                amount = Decimal(amount_str)
                if amount < 0:
                    continue
                amount_integer = int(amount * AMOUNT_MULTIPLIER)
                if amount_integer > MAX_AMOUNT_INTEGER:
                    continue
            except (InvalidOperation, ValueError):
                continue

            # 从目标部分提取动物和号码
            animals_found = []
            for char in target_part:
                if char in self.animals:
                    animals_found.append(char)

            # 提取号码
            numbers_found = re.findall(r'\d+', target_part)
            numbers = []
            for num_str in numbers_found:
                try:
                    num = int(num_str)
                    if MIN_NUMBER <= num <= MAX_NUMBER:
                        numbers.append(str(num))
                except ValueError:
                    pass

            # 合并动物和号码（不去重动物和号码，保留所有重复）
            # 动物：保留所有，包括重复
            # 号码：也保留所有重复（用户可能故意多次下注同一号码）

            all_targets = []
            target_type = None

            if animals_found and numbers:
                # 混合模式：动物保留重复 + 号码也保留重复
                all_targets = animals_found + numbers
                target_type = 'mixed'
            elif animals_found:
                # 仅动物：保留所有重复
                all_targets = animals_found
                target_type = 'animal'
            elif numbers:
                # 仅号码：也保留所有重复
                all_targets = numbers
                target_type = 'number'
            else:
                continue

            # 创建指令（不再检查重复）
            warning = None

            instructions.append(instruction)

        return instructions if instructions else [self._parse_single_instruction(line, line_num)]

    def _parse_with_keywords(self, line: str, line_num: int, normalized: str, matches: List) -> List[Instruction]:
        """分割一行中的多条指令 - 智能语义解析"""
        # 标准化
        normalized = self._normalize_punctuation(line)

        # 定义所有可能的关键词分隔符
        keywords = EACH_SYNONYMS + ['数', '=', '：', ':']

        # 查找所有关键词+金额的位置
        # 模式：关键词 + 可选空格 + 数字（金额）
        instructions = []

        # 使用正则查找所有 "关键词+金额" 组合
        pattern = r'(' + '|'.join(re.escape(k) for k in keywords) + r')\s*(\d+(?:\.\d+)?)'
        matches = list(re.finditer(pattern, normalized))

        if not matches:
            # 没有找到标准格式，尝试传统解析
            return [self._parse_single_instruction(line, line_num)]

        # 处理每个匹配
        for i, match in enumerate(matches):
            keyword = match.group(1)
            amount_str = match.group(2)
            keyword_start = match.start()
            amount_end = match.end()

            # 确定目标部分的起始位置
            if i == 0:
                target_start = 0
            else:
                # 从上一个金额结束位置开始
                target_start = matches[i - 1].end()

            # 提取目标部分
            target_part = normalized[target_start:keyword_start].strip()

            if not target_part:
                continue

            # 解析金额
            try:
                amount = Decimal(amount_str)
                if amount < 0:
                    continue
                amount_integer = int(amount * AMOUNT_MULTIPLIER)
                if amount_integer > MAX_AMOUNT_INTEGER:
                    continue
            except (InvalidOperation, ValueError):
                continue

            # 从目标部分提取动物和号码
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

            # 合并动物和号码（不去重动物和号码，保留所有重复）
            # 动物：保留所有，包括重复
            # 号码：也保留所有重复

            all_targets = []
            target_type = None

            if animals_found and numbers_found:
                # 混合模式：动物保留重复 + 号码也保留重复
                all_targets = animals_found + numbers_found
                target_type = 'mixed'
            elif animals_found:
                # 仅动物：保留所有重复
                all_targets = animals_found
                target_type = 'animal'
            elif numbers_found:
                # 仅号码：也保留所有重复
                all_targets = numbers_found
                target_type = 'number'
            else:
                continue

            # 创建指令（不再检查重复）
            warning = None

            # 创建指令
            instruction = Instruction(
                source_line=line_num,
                original_text=line,
                normalized_text=normalized,
                target_type=target_type,
                targets=all_targets,
                amount_integer=amount_integer,
                warning=warning
            )

            instructions.append(instruction)

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

        # 如果没有关键词，尝试提取末尾的纯数字作为金额
        if not amount_match:
            # 匹配末尾的数字：非数字后面跟着数字直到结尾
            end_number_match = re.search(r'(\d+(?:\.\d+)?)$', normalized)
            if end_number_match:
                amount_match = end_number_match
                found_keyword = None  # 无关键词
            else:
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

        # 合并动物和号码（不去重动物和号码，保留所有重复）
        # 动物：保留所有，包括重复
        # 号码：也保留所有重复

        all_targets = []
        target_type = None

        if animals_found and numbers:
            # 混合模式：动物保留重复 + 号码也保留重复
            all_targets = animals_found + numbers
            target_type = 'mixed'
        elif animals_found:
            # 仅动物：保留所有重复
            all_targets = animals_found
            target_type = 'animal'
        elif numbers:
            # 仅号码：也保留所有重复
            all_targets = numbers
            target_type = 'number'
        else:
            raise ParserError(f"未找到有效目标: {line}")

        # 创建指令（不再检查重复）
        warning = None

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
        """标准化标点符号和输入格式 - 所有标点符号只作为分隔符"""
        # 1. 中文数字转阿拉伯数字
        text = self._chinese_to_number(text)

        # 2. 全角数字转半角
        for i in range(10):
            text = text.replace(chr(0xFF10 + i), str(i))

        # 3. 全角小数点转半角
        text = text.replace('．', '.')

        # 4. 所有标点符号统一替换为空格（作为分隔符）
        # 包括：~ . , / - — ～ 、 。 ； | \ _ 等
        separators = [
            '~', '～', '—', '-', ',', '，', '.', '。',
            '、', '；', ';', '/', '\\', '|', '_',
            '：', ':', '（', '(', '）', ')'
        ]
        for sep in separators:
            text = text.replace(sep, ' ')

        # 5. 清理连续空格和不可见字符
        text = ' '.join(text.split())

        return text
