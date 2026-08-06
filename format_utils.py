# -*- coding: utf-8 -*-
"""
金额格式化工具
统一整个软件的金额显示格式
"""


def format_amount(value: float) -> str:
    """
    格式化金额显示

    规则：
    - 整数金额不显示小数部分：600.00 -> 600
    - 有小数的金额保留实际小数位：600.5 -> 600.5, 600.25 -> 600.25

    Args:
        value: 金额数值（元）

    Returns:
        格式化后的字符串
    """
    if value == int(value):
        # 整数金额，不显示小数
        return str(int(value))
    else:
        # 有小数，去除末尾多余的0
        return f"{value:g}"


def format_amount_with_separator(value: float) -> str:
    """
    格式化金额显示（带千分位分隔符）

    用于大额金额显示，例如顶部统计

    Args:
        value: 金额数值（元）

    Returns:
        格式化后的字符串（带千分位分隔符）
    """
    if value == int(value):
        # 整数金额，使用千分位分隔符
        return f"{int(value):,}"
    else:
        # 有小数，去除末尾多余的0，并添加千分位分隔符
        formatted = f"{value:,.10f}".rstrip('0').rstrip('.')
        return formatted
