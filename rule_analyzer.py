# -*- coding: utf-8 -*-
"""
规则分析器
将输入文本转换为过滤条件
"""

import re
from typing import List, Tuple, Optional
from decimal import Decimal, InvalidOperation
from number_filter_engine import FilterCondition
from constants import AMOUNT_MULTIPLIER, MAX_AMOUNT_INTEGER


class RuleAnalyzer:
    """规则分析器"""

    def __init__(self):
        # 关键词映射（优先级从高到低）
        self.color_keywords = {
            '红波': 'red',
            '蓝波': 'blue',
            '绿波': 'green',
        }

        self.parity_keywords = {
            '单': 'odd',
            '双': 'even',
        }

        self.size_keywords = {
            '大': 'big',
            '小': 'small',
        }

        self.head_keywords = {
            '1头': 1, '一头': 1,
            '2头': 2, '二头': 2,
            '3头': 3, '三头': 3,
            '4头': 4, '四头': 4,
        }

        self.tail_keywords = {
            '尾': 'tail',
        }

        self.tail_size_keywords = {
            '尾大': 'big',
            '尾小': 'small',
        }

    def analyze(self, text: str) -> Tuple[List[FilterCondition], Optional[int], str]:
        """
        分析输入文本

        Returns:
            (条件列表, 金额整数, 剩余文本)
        """
        text = text.strip()
        conditions = []
        remaining = text

        # 优先级1: 尾数大小（必须在尾数之前）
        for keyword, value in self.tail_size_keywords.items():
            if keyword in remaining:
                conditions.append(FilterCondition('tail_size', value))
                remaining = remaining.replace(keyword, '', 1)
                break

        # 优先级2: 头数
        for keyword, value in self.head_keywords.items():
            if keyword in remaining:
                conditions.append(FilterCondition('head', value))
                remaining = remaining.replace(keyword, '', 1)
                break

        # 优先级3: 颜色
        for keyword, value in self.color_keywords.items():
            if keyword in remaining:
                conditions.append(FilterCondition('color', value))
                remaining = remaining.replace(keyword, '', 1)
                break

        # 优先级4: 尾数（具体数字）
        # 匹配 "尾5", "尾0" 等
        tail_match = re.search(r'尾(\d)', remaining)
        if tail_match:
            tail_num = int(tail_match.group(1))
            conditions.append(FilterCondition('tail', tail_num))
            remaining = remaining.replace(tail_match.group(0), '', 1)

        # 优先级5: 单双
        for keyword, value in self.parity_keywords.items():
            if keyword in remaining:
                conditions.append(FilterCondition('parity', value))
                remaining = remaining.replace(keyword, '', 1)
                break

        # 优先级6: 大小
        for keyword, value in self.size_keywords.items():
            if keyword in remaining:
                conditions.append(FilterCondition('size', value))
                remaining = remaining.replace(keyword, '', 1)
                break

        # 提取金额
        amount_integer = self._extract_amount(remaining)

        return conditions, amount_integer, remaining

    def _extract_amount(self, text: str) -> Optional[int]:
        """提取金额"""
        # 查找所有数字
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        if not numbers:
            return None

        # 取第一个数字作为金额
        try:
            amount = Decimal(numbers[0])
            if amount < 0:
                return None
            amount_integer = int(amount * AMOUNT_MULTIPLIER)
            if amount_integer > MAX_AMOUNT_INTEGER:
                return None
            return amount_integer
        except (InvalidOperation, ValueError):
            return None


# 全局实例
_rule_analyzer = RuleAnalyzer()


def get_rule_analyzer() -> RuleAnalyzer:
    """获取规则分析器实例"""
    return _rule_analyzer
