# -*- coding: utf-8 -*-
"""
解析器 v2.0
统一的号码解析引擎
"""

from typing import List, Tuple
from models import Instruction
from rule_analyzer import get_rule_analyzer
from number_filter_engine import get_filter_engine


class ParserV2:
    """解析器 v2.0"""

    def __init__(self):
        self.rule_analyzer = get_rule_analyzer()
        self.filter_engine = get_filter_engine()

    def parse(self, text: str) -> List[Instruction]:
        """
        解析输入文本

        Args:
            text: 输入文本，如 "蓝波双200", "1头20"

        Returns:
            指令列表
        """
        text = text.strip()
        if not text:
            return []

        # 步骤1: 规则分析
        conditions, amount_integer, remaining = self.rule_analyzer.analyze(text)

        # 如果没有条件或没有金额，返回空
        if not conditions or amount_integer is None:
            return []

        # 步骤2: 过滤号码
        numbers = self.filter_engine.filter_numbers(conditions)

        # 如果没有号码，返回空
        if not numbers:
            return []

        # 步骤3: 生成指令（适配现有的 Instruction 模型）
        number_str = ','.join(str(num) for num in numbers)
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
