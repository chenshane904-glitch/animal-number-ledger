"""指令解析器"""
import re
from decimal import Decimal, InvalidOperation
from typing import List, Tuple, Optional
from constants import (
    SEPARATORS, EACH_SYNONYMS, MIN_NUMBER, MAX_NUMBER,
    AMOUNT_MULTIPLIER, MAX_AMOUNT_INTEGER
)
from models import Instruction


class ParserError(Exception):
    """解析错误"""
    pass


class InstructionParser:
    """指令解析器"""

    def __init__(self, animal_mapping: dict):
        """
        初始化解析器

        Args:
            animal_mapping: 动物号码映射 {动物名: [号码列表]}
        """
        self.animal_mapping = animal_mapping
        self.animals = set(animal_mapping.keys())

    def parse_input(self, text: str) -> List[Instruction]:
        """
        解析输入文本，返回指令列表

        Args:
            text: 输入文本（多行）

        Returns:
            指令列表

        Raises:
            ParserError: 解析失败
        """
        instructions = []
        lines = text.strip().split('\n')

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
        """解析单行指令"""
        original = line

        # 预处理：标准化标点符号和数字
        normalized = self._normalize_punctuation(line)

        # 第一步：先找关键词位置（各、个、元等）
        # 这样可以避免把号码中的小数点误认为金额小数点
        keyword_pos = -1
        found_keyword = None
        is_each = False

        for synonym in EACH_SYNONYMS:
            pos = normalized.find(synonym)
            if pos != -1:
                keyword_pos = pos
                found_keyword = synonym
                is_each = True
                break

        # 如果没有找到关键词，尝试找"元"或"￥"
        if keyword_pos == -1:
            for keyword in ['元', '￥', '$']:
                pos = normalized.find(keyword)
                if pos != -1:
                    keyword_pos = pos
                    found_keyword = keyword
                    break

        # 第二步：根据关键词分割号码部分和金额部分
        if keyword_pos != -1:
            # 关键词之前是号码部分
            target_part = normalized[:keyword_pos].strip()
            # 关键词之后是金额部分
            amount_part = normalized[keyword_pos + len(found_keyword):].strip()
        else:
            # 如果没有关键词，尝试从末尾提取金额
            # 这种情况下使用原来的逻辑
            amount_match = re.search(r'(?<![\d.])(\d+(?:\.\d{1,2})?)斤?$', normalized)
            if not amount_match:
                raise ParserError(f"无法识别金额分隔符(各/个/元等): {line}")

            target_part = normalized[:amount_match.start()].strip()
            amount_part = amount_match.group(1)

        # 第三步：解析金额
        # 提取金额数字（移除可能的"斤"字）
        amount_part = amount_part.replace('斤', '').strip()
        amount_match = re.match(r'^(\d+(?:\.\d{1,2})?).*', amount_part)
        if not amount_match:
            raise ParserError(f"无法识别金额: {line}")

        amount_str = amount_match.group(1)
        try:
            amount = Decimal(amount_str)
            if amount < 0:
                raise ParserError(f"金额不能为负数: {amount_str}")
            amount_integer = int(amount * AMOUNT_MULTIPLIER)
            if amount_integer > MAX_AMOUNT_INTEGER:
                raise ParserError(f"金额超出可存储范围: {amount_str}")
        except (InvalidOperation, ValueError):
            raise ParserError(f"无效的金额格式: {amount_str}")

        # 第四步：处理号码部分
        # 移除"号"字
        target_part = target_part.replace('号', ' ')

        # 移除"数"字（可能是"各数"的残留）
        target_part = target_part.replace('数', ' ')

        # 清理空白
        target_part = ' '.join(target_part.split())

        # 分割目标（支持多种分隔符）
        targets_raw = self._split_targets(target_part)

        if not targets_raw:
            raise ParserError(f"无法识别目标: {line}")

        # 判断目标类型（号码或动物）
        target_type, targets = self._classify_targets(targets_raw, line)

        # 检查重复
        warning = None
        if len(targets) != len(set(targets)):
            seen = set()
            duplicates = []
            for t in targets:
                if t in seen:
                    duplicates.append(t)
                seen.add(t)
            warning = f"同一行重复目标: {', '.join(duplicates)}"
            targets = list(set(targets))  # 去重

        # 如果不是"各数"模式但有多个目标，报错
        if not is_each and len(targets) > 1:
            # 实际上"1、7、20、49各13"这种格式已经被is_each捕获
            # 但"1、7、20、49 13"这种没有"各"的格式应该报错
            # 根据需求，多个目标必须有"各数"关键词
            raise ParserError(f"多个目标必须使用'各号'、'各'等关键词: {line}")

        instruction = Instruction(
            source_line=line_num,
            original_text=original,
            normalized_text=normalized,
            target_type=target_type,
            targets=targets,
            amount_integer=amount_integer,
            warning=warning
        )

        return instruction

    def _split_targets(self, text: str) -> List[str]:
        """分割目标字符串

        支持两种方式：
        1. 有分隔符：用分隔符分割
        2. 无分隔符：尝试逐个字符识别动物
        """
        # 先尝试用分隔符分割
        temp_text = text
        for sep in SEPARATORS:
            temp_text = temp_text.replace(sep, '|')

        parts = [p.strip() for p in temp_text.split('|') if p.strip()]

        # 如果分割成功（有多个部分或单个数字），直接返回
        if len(parts) > 1:
            return parts
        if len(parts) == 1 and parts[0].isdigit():
            return parts

        # 如果只有一个部分且不是纯数字，尝试拆分动物名称
        if len(parts) == 1:
            single_part = parts[0]

            # 检查是否全是动物名称（连续的单字符动物）
            animals_found = []
            for char in single_part:
                if char in self.animals:
                    animals_found.append(char)
                else:
                    # 包含非动物字符，按原样返回
                    return parts

            # 如果全是动物名称，返回拆分结果
            if animals_found:
                return animals_found

        # 默认返回原始分割结果
        return parts if parts else []

    def _classify_targets(self, targets_raw: List[str], original_line: str) -> Tuple[str, List[str]]:
        """
        分类目标（号码或动物）

        Returns:
            (target_type, targets)
        """
        numbers = []
        animals = []

        for t in targets_raw:
            # 尝试解析为号码
            if t.isdigit():
                num = int(t)
                if MIN_NUMBER <= num <= MAX_NUMBER:
                    numbers.append(str(num))
                    continue
                else:
                    raise ParserError(f"号码超出范围(1-49): {t}")

            # 尝试解析为动物
            if t in self.animals:
                animals.append(t)
                continue

            # 无法识别
            raise ParserError(f"无法识别的目标: {t}")

        # 不能混合号码和动物
        if numbers and animals:
            raise ParserError(f"同一行不能混合动物与号码: {original_line}")

        if numbers:
            return 'number', numbers
        elif animals:
            return 'animal', animals
        else:
            raise ParserError(f"无有效目标: {original_line}")

    def _normalize_punctuation(self, text: str) -> str:
        """
        标准化标点符号，将全角字符转换为半角

        Args:
            text: 原始文本

        Returns:
            标准化后的文本
        """
        # 全角数字转半角
        full_to_half_digit = str.maketrans(
            '０１２３４５６７８９',
            '0123456789'
        )
        text = text.translate(full_to_half_digit)

        # 全角小数点转半角
        text = text.replace('．', '.')

        return text
