# -*- coding: utf-8 -*-
"""
号码过滤引擎
基于条件过滤号码集合
"""

from typing import Set, List, Dict, Any
from dataclasses import dataclass
from number_database import get_number_db


@dataclass
class FilterCondition:
    """过滤条件"""
    type: str  # 'color', 'parity', 'size', 'tail', 'head', 'tail_size'
    value: Any  # 具体值


class NumberFilterEngine:
    """号码过滤引擎"""

    def __init__(self):
        self.db = get_number_db()

    def apply_condition(self, condition: FilterCondition) -> Set[int]:
        """应用单个条件"""
        if condition.type == 'color':
            return self.db.filter_by_color(condition.value)
        elif condition.type == 'parity':
            return self.db.filter_by_parity(condition.value)
        elif condition.type == 'size':
            return self.db.filter_by_size(condition.value)
        elif condition.type == 'tail':
            return self.db.filter_by_tail(condition.value)
        elif condition.type == 'head':
            return self.db.filter_by_head(condition.value)
        elif condition.type == 'tail_size':
            return self.db.filter_by_tail_size(condition.value)
        else:
            return set(self.db.get_all_numbers())

    def apply_conditions(self, conditions: List[FilterCondition]) -> Set[int]:
        """应用多个条件（AND逻辑）"""
        if not conditions:
            return set(self.db.get_all_numbers())

        # 第一个条件
        result = self.apply_condition(conditions[0])

        # 其余条件取交集
        for condition in conditions[1:]:
            result = result & self.apply_condition(condition)

        return result

    def filter_numbers(self, conditions: List[FilterCondition]) -> List[int]:
        """过滤号码并返回排序列表"""
        result_set = self.apply_conditions(conditions)
        return sorted(list(result_set))


# 全局实例
_filter_engine = NumberFilterEngine()


def get_filter_engine() -> NumberFilterEngine:
    """获取过滤引擎实例"""
    return _filter_engine
