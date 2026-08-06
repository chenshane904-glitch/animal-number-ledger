# -*- coding: utf-8 -*-
"""
玩法模式配置加载工具
"""

import json
from pathlib import Path
from play_mode import PlayMode


def load_play_mode_config(mode: PlayMode) -> dict:
    """
    加载玩法配置

    Args:
        mode: 玩法模式

    Returns:
        dict: 配置字典
    """
    config_path = Path(__file__).parent / 'play_modes.json'

    with open(config_path, 'r', encoding='utf-8') as f:
        all_config = json.load(f)

    mode_str = str(mode)
    if mode_str not in all_config:
        raise ValueError(f"未找到玩法模式配置: {mode_str}")

    return all_config[mode_str]


def get_odds(mode: PlayMode) -> float:
    """
    获取玩法赔率

    Args:
        mode: 玩法模式

    Returns:
        float: 赔率
    """
    config = load_play_mode_config(mode)
    return config.get('odds', 1.0)


def should_expand_numbers(mode: PlayMode) -> bool:
    """
    判断是否需要展开号码

    Args:
        mode: 玩法模式

    Returns:
        bool: 是否展开
    """
    config = load_play_mode_config(mode)
    return config.get('expand_numbers', False)


def get_display_type(mode: PlayMode) -> str:
    """
    获取显示类型

    Args:
        mode: 玩法模式

    Returns:
        str: 'numbers' 或 'animals'
    """
    config = load_play_mode_config(mode)
    return config.get('display_type', 'numbers')


def get_animals_list(mode: PlayMode) -> list:
    """
    获取生肖列表（仅平特模式）

    Args:
        mode: 玩法模式

    Returns:
        list: 生肖列表
    """
    if mode != PlayMode.FLAT_ZODIAC:
        return []

    config = load_play_mode_config(mode)
    return config.get('animals', [])
