# -*- coding: utf-8 -*-
"""
头数筛选功能 - 快捷号码选择

头数不是号码属性，而是一组号码的快捷选择方式：
- 一头：10-19
- 二头：20-29
- 三头：30-39
- 四头：40-49
"""

from typing import List


# 头数定义（头数名称 -> 号码范围）
HEAD_MAPPING = {
    "一头": (10, 19),   # 10-19
    "二头": (20, 29),   # 20-29
    "三头": (30, 39),   # 30-39
    "四头": (40, 49),   # 40-49
}

# 头数显示顺序
HEAD_ORDER = ["一头", "二头", "三头", "四头"]


def get_head_range(head_name: str) -> tuple:
    """
    获取指定头数对应的号码范围

    参数:
        head_name: 头数名称（一头、二头、三头、四头）

    返回:
        (起始号码, 结束号码) 元组

    异常:
        ValueError: 如果头数名称无效
    """
    if head_name not in HEAD_MAPPING:
        raise ValueError(f"无效的头数名称: {head_name}")

    return HEAD_MAPPING[head_name]


def get_head_numbers(head_name: str) -> List[int]:
    """
    获取指定头数对应的号码列表

    参数:
        head_name: 头数名称（一头、二头、三头、四头）

    返回:
        号码列表

    异常:
        ValueError: 如果头数名称无效
    """
    start, end = get_head_range(head_name)
    return list(range(start, end + 1))


def format_head_numbers_for_input(head_name: str) -> str:
    """
    格式化头数号码为输入文本格式（使用范围表示法）

    参数:
        head_name: 头数名称

    返回:
        格式化的输入文本，如 "10-19"
    """
    start, end = get_head_range(head_name)
    return f"{start}-{end}"


def get_all_heads() -> List[str]:
    """
    获取所有头数名称列表（按顺序）

    返回:
        头数名称列表
    """
    return HEAD_ORDER.copy()


def is_valid_head(head_name: str) -> bool:
    """
    检查是否为有效的头数名称

    参数:
        head_name: 头数名称

    返回:
        True 如果有效，否则 False
    """
    return head_name in HEAD_MAPPING
