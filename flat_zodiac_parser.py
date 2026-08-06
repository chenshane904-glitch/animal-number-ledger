# -*- coding: utf-8 -*-
"""
平特一肖解析器 - 只解析生肖和金额，不展开号码
"""
import re
from typing import List, Tuple


class FlatZodiacEntry:
    """平特一肖单条记录 - 兼容 Instruction 接口"""
    def __init__(self, zodiac: str, amount: float, line_number: int = 1):
        self.zodiac = zodiac
        self.amount = amount
        self.amount_int = int(amount * 100)  # 保留兼容性

        # 兼容 Instruction 接口（用于预览）
        self.target_type = 'animal'
        self.targets = [zodiac]
        self.amount_integer = self.amount_int
        self.source_line = line_number
        self.warning = None


class FlatZodiacParser:
    """平特一肖解析器"""

    ZODIACS = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

    def parse_input(self, input_text: str) -> List[FlatZodiacEntry]:
        """
        解析输入（兼容 UI 调用）

        Args:
            input_text: 原始输入文本

        Returns:
            解析后的记录列表
        """
        return self.parse(input_text)

    def parse(self, input_text: str) -> List[FlatZodiacEntry]:
        """
        解析平特一肖输入

        支持格式：
        - 虎100
        - 虎 100
        - 虎各100
        - 平特虎100
        - 平特一肖虎100
        - 平特虎100，龙200

        Args:
            input_text: 原始输入文本

        Returns:
            解析后的记录列表

        Raises:
            ValueError: 解析失败
        """
        if not input_text or not input_text.strip():
            raise ValueError("输入不能为空")

        # 标准化输入
        normalized = self._normalize_input(input_text)

        # 分割成多个条目（支持逗号、顿号、分号、换行）
        items = re.split(r'[,，、;；\n]+', normalized)

        entries = []
        for i, item in enumerate(items, 1):
            item = item.strip()
            if not item:
                continue

            # 解析单个条目
            try:
                zodiac, amount = self._parse_single_item(item)
                entries.append(FlatZodiacEntry(zodiac, amount, line_number=i))
            except ValueError as e:
                raise ValueError(f"第{i}项：{e}")

        if not entries:
            raise ValueError("没有有效的输入")

        return entries

    def _normalize_input(self, text: str) -> str:
        """
        标准化输入文本

        处理：
        1. 去除每项开头的"平特一肖"、"平特肖"、"平特"前缀
        2. 去除生肖和金额之间的空格
        3. 保留"各"字但不影响后续解析
        """
        # 按分隔符分割
        items = re.split(r'[,，、;；\n]+', text)

        normalized_items = []
        for item in items:
            item = item.strip()
            if not item:
                continue

            # 去除开头的平特一肖相关前缀
            item = re.sub(r'^平特一肖', '', item)
            item = re.sub(r'^平特肖', '', item)
            item = re.sub(r'^平特', '', item)

            # 去除所有空格
            item = item.replace(' ', '')

            normalized_items.append(item)

        return '\n'.join(normalized_items)

    def _parse_single_item(self, item: str) -> Tuple[str, float]:
        """
        解析单个条目

        Args:
            item: 标准化后的单个条目，例如 "虎100"、"虎各100"

        Returns:
            (生肖, 金额)

        Raises:
            ValueError: 解析失败
        """
        # 移除"各"字
        item = item.replace('各', '')

        # 检查是否包含数字（号码）
        if re.search(r'^\d+', item):
            raise ValueError("平特一肖模式不支持号码输入，请使用号码模式")

        # 查找生肖
        zodiac = None
        for z in self.ZODIACS:
            if z in item:
                zodiac = z
                break

        if not zodiac:
            raise ValueError(f"无法识别生肖：{item}")

        # 提取金额
        # 匹配整数或小数
        amount_match = re.search(r'(\d+\.?\d*)', item)
        if not amount_match:
            raise ValueError(f'已识别生肖"{zodiac}"，但缺少金额，请输入"{zodiac}100"或"平特{zodiac}100"')

        try:
            amount = float(amount_match.group(1))
            if amount <= 0:
                raise ValueError(f"金额必须大于0")
            return zodiac, amount
        except ValueError:
            raise ValueError(f"金额格式错误：{amount_match.group(1)}")
