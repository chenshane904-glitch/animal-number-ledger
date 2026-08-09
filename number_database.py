# -*- coding: utf-8 -*-
"""
号码属性数据库
定义0-49每个号码的固有属性
"""

from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class NumberAttributes:
    """号码属性"""
    number: int
    color: str  # 'red', 'blue', 'green'
    parity: str  # 'odd', 'even'
    size: str  # 'small', 'big'
    tail: int  # 尾数 0-9
    head: int  # 头 0-4


# 号码颜色映射（基于传统规则）
COLOR_MAPPING = {
    'red': [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46],
    'blue': [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48],
    'green': [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]
}


class NumberDatabase:
    """号码属性数据库"""

    def __init__(self):
        self._numbers: Dict[int, NumberAttributes] = {}
        self._init_database()

    def _init_database(self):
        """初始化所有号码属性"""
        for num in range(1, 50):  # 1-49
            self._numbers[num] = NumberAttributes(
                number=num,
                color=self._get_color(num),
                parity='odd' if num % 2 == 1 else 'even',
                size='small' if num <= 24 else 'big',
                tail=num % 10,
                head=num // 10
            )

    def _get_color(self, num: int) -> str:
        """获取号码颜色"""
        if num in COLOR_MAPPING['red']:
            return 'red'
        elif num in COLOR_MAPPING['blue']:
            return 'blue'
        elif num in COLOR_MAPPING['green']:
            return 'green'
        else:
            return 'unknown'

    def get(self, num: int) -> NumberAttributes:
        """获取号码属性"""
        return self._numbers.get(num)

    def get_all_numbers(self) -> List[int]:
        """获取所有号码"""
        return list(range(1, 50))

    def filter_by_color(self, color: str) -> Set[int]:
        """按颜色筛选"""
        return {num for num, attr in self._numbers.items() if attr.color == color}

    def filter_by_parity(self, parity: str) -> Set[int]:
        """按单双筛选"""
        return {num for num, attr in self._numbers.items() if attr.parity == parity}

    def filter_by_size(self, size: str) -> Set[int]:
        """按大小筛选"""
        return {num for num, attr in self._numbers.items() if attr.size == size}

    def filter_by_tail(self, tail: int) -> Set[int]:
        """按尾数筛选"""
        return {num for num, attr in self._numbers.items() if attr.tail == tail}

    def filter_by_head(self, head: int) -> Set[int]:
        """按头数筛选"""
        return {num for num, attr in self._numbers.items() if attr.head == head}

    def filter_by_tail_size(self, size: str) -> Set[int]:
        """按尾数大小筛选"""
        if size == 'big':
            return {num for num, attr in self._numbers.items() if attr.tail >= 5}
        else:  # small
            return {num for num, attr in self._numbers.items() if attr.tail < 5}


# 全局实例
_number_db = NumberDatabase()


def get_number_db() -> NumberDatabase:
    """获取号码数据库实例"""
    return _number_db
